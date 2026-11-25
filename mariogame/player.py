import arcade
from constants import *

def load_texture_pair(filename):
    texture = arcade.load_texture(filename)
    return [
        texture,
        texture.flip_left_right(),
    ]

class PlayerCharacter(arcade.Sprite):
    """
    sert a definir le personnage et c'est differente animation
    """
    def __init__(self):
        super().__init__()
        
        self.character_face_direction = RIGHT_FACING
        
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        # initialise les deplacement speciaux
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        main_path = ":resources:images/animated_characters/zombie/zombie"# cherche le personnage dans une base de donner

        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        self.walk_textures = []
        # channge le skin pour les annimation
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        self.texture = self.idle_texture_pair[0]
        

    def update_animation(self, delta_time: float = 1 / 60):
        """
        permet de rafraichir toutes les annimation
        """
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return
        
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return
        
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]
