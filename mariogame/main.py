import time
import math
import arcade
from constants import *
from player import PlayerCharacter
from maps import MAPS
from monster import Monster
from moving_platform import MovingPlatform, PLATFORM_MOVE_TYPE_X, PLATFORM_MOVE_TYPE_Y

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Maryo"

def format_duration(dur):
    return time.strftime('%Mm%Ss', time.gmtime(dur))

class Maryo(arcade.Window):
    """
    la classe principale qui appèle tous les autres

    """
    collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
    jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
    #game_over = arcade.load_sound(Path("sounds") / "ah.wav")
    game_over = arcade.load_sound(":resources:sounds/gameover1.wav")

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        # on mets tous a l'etat initiale
        self.paused = False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.level = 1
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.immunity_start = 0
        self.tile_map = None
        self.monsters = []
        self.moving_platforms_x = []
        self.moving_platforms_y = []
        # chronomètre jusqu'a fin du jeu
        self.timer_start = time.time()

    def setup(self):
        """
        on mets en place les parametre d'afichage
        """
        start = time.time()
        if self.level > len(MAPS):
            self.close()
            print(f"Bravo vous avez terminer le niveau ultime. "
                  f"Au total, vous avez effectué {self.level - 1} niveaux en {format_duration(start - self.timer_start)} "
                  f"avec un score de {self.score} ! Maryo est fier de vous !")
            return

        self.camera = arcade.Camera2D()
        self.scene = arcade.Scene()
        self.gui_camera = arcade.Camera2D()
        self.immunity_start = time.time()
        self.tile_map = MAPS[self.level - 1].load()

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # liste des monstres, avec un direction initiale différente pour chaque monstre
        self.monsters = [Monster(monster, -1 if i % 2 == 0 else 1, self.scene[LAYER_NAME_PLATFORMS]) for (i, monster) in enumerate(self.scene[LAYER_NAME_MONSTER])]
        # liste des plateform qui ce deplacent
        self.moving_platforms = [MovingPlatform(platform, PLATFORM_MOVE_TYPE_Y) for platform in self.scene[LAYER_NAME_MOVING_PLATFORMS_Y]] + [MovingPlatform(platform, PLATFORM_MOVE_TYPE_X) for platform in self.scene[LAYER_NAME_MOVING_PLATFORMS_X]]
        # definis comment le personnage se deplace
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        self.scene.add_sprite_list_after("Player", LAYER_NAME_FOREGROUND)

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)
        # definis qu'elle objet sur la map est considérer comme des elements dur
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            platforms=[self.scene[LAYER_NAME_MOVING_PLATFORMS_Y], self.scene[LAYER_NAME_MOVING_PLATFORMS_X]],# plateform est une class liée a arcade qui est dur mais bouge
            walls=self.scene[LAYER_NAME_PLATFORMS],# walls est une classe lié a arcade qui est dur mais ne bouge pâs
            ladders=self.scene[LAYER_NAME_LADDERS]
        )

        # compenser le temps perdu sans setup pour chronometre
        self.timer_start += time.time() - start

    def on_draw(self):
        """
        permet de suivre le personnage
        """
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()
        # definition du score
        arcade.draw_text(
            f"Score : {self.score}",
            35,
            SCREEN_HEIGHT - 35,
            arcade.csscolor.WHITE,
            18,
        )
        # permet d'avoir une immunité pour pas mourir en boucle
        remaining_time = math.floor(time.time() - self.immunity_start)
        if remaining_time < PLAYER_SPAWN_IMMUNITY_DURATION:
            arcade.draw_text(
                f"Durée d'immunité : {PLAYER_SPAWN_IMMUNITY_DURATION - remaining_time}s",
                35,
                SCREEN_HEIGHT - 60,
                arcade.csscolor.WHITE,
                18,
            )
        # dessine le chrono
        arcade.draw_text(
            f"Chronomètre : {format_duration(time.time() - self.timer_start)}",
            SCREEN_WIDTH - 35,
            SCREEN_HEIGHT - 35,
            arcade.csscolor.WHITE,
            18,
            anchor_x="right",
        )
        # dessine le niveau
        arcade.draw_text(
            f"Niveau actuel : {self.level}",
            SCREEN_WIDTH - 35,
            SCREEN_HEIGHT - 60,
            arcade.csscolor.WHITE,
            18,
            anchor_x="right",
        )

    def process_keychange(self):
        if self.physics_engine.is_on_ladder():
            # monter échelle
            if self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = PLAYER_LADDER_SPEED
            # descente échelle (volontaire ou non)
            elif not self.up_pressed:
                self.player_sprite.change_y = -PLAYER_LADDER_SPEED
            else:
                self.player_sprite.change_y = 0
        # sauter si HAUT appuyé (si possible & pas de saut en cours & BAS non appuyé)
        elif self.up_pressed and self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset and not self.down_pressed:
            self.physics_engine.jump(PLAYER_JUMP_SPEED)
            self.jump_needs_reset = True
            arcade.play_sound(self.jump_sound)

        # déplacements : droite/gauche/rien
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, _modifiers):
        """
        on change l'etat en fonction de la precion sur la touche
        """
        # bouger invalide l'immunité (pour pas tricher au spawn)
        self.immunity_start = 0
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        # permet de faire stop ou de l'enlever
        elif key == arcade.key.ESCAPE:
            self.paused = not self.paused

        self.process_keychange()

    def on_key_release(self, key, _modifiers):
        """
        on change l'etat en fonction du relachement de touche
        """
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def center_camera_to_player(self):
        """
        permet de suivre le personnage
        """
        # Dans arcade 3, la position de la caméra = le CENTRE de l'écran
        camera_x = self.player_sprite.center_x
        camera_y = self.player_sprite.center_y

        # Empêche la caméra d'afficher du vide à gauche et en bas de la carte
        half_width = self.width / 2
        half_height = self.height / 2
        if camera_x < half_width:
            camera_x = half_width
        if camera_y < half_height:
            camera_y = half_height

        self.camera.position = (camera_x, camera_y)

    def gameover(self):
        """
        definit les facon de mourrir et de le replacer
        """
        arcade.play_sound(self.game_over)
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        # renistiallisé le debut de la periode d'immunité
        self.immunity_start = time.time()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y

    def on_update(self, delta_time):
        """
        sert a rafraichir en permanence la map
        """
        if self.paused:# peret de stopper le programe si il y a une pause
            return

        self.physics_engine.update()

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        self.scene.update_animation(
            delta_time, [LAYER_NAME_COINS, LAYER_NAME_BACKGROUND, LAYER_NAME_PLAYER]
        )

        self.center_camera_to_player()

        for monster in self.monsters:
            monster.move()
            # gameover si le joueur n'est plus immunis et touche un monstre
            is_immunity_finished = time.time() - self.immunity_start > PLAYER_SPAWN_IMMUNITY_DURATION
            if is_immunity_finished and arcade.check_for_collision(monster.sprite, self.player_sprite):
                self.gameover()

        for moving_platform in self.moving_platforms:
            moving_platform.move()

        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene[LAYER_NAME_COINS])
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        # gameover en cas de sortie de map ou colision avec élement mortels (feux, etc)
        if self.player_sprite.center_y < -100 or arcade.check_for_collision_with_list(self.player_sprite, self.scene[LAYER_NAME_DONT_TOUCH]):
            self.gameover()

        # ligne d'arrivé
        if arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_FIN]
        ):
            self.level += 1
            self.setup()

        self.center_camera_to_player()

if __name__ == "__main__":
    window = Maryo()
    window.setup()
    arcade.run()