import arcade
from constants import *

VERTICAL_MAX_MOVE = 50

class Monster:
  """
  permet de definir tous les mouvements des monstres

  """
  def __init__(self, sprite, start_direction, platforms):
    self.sprite = sprite
    self.platforms = platforms
    can_move_right = self.can_move_to(self.sprite.center_x + self.sprite.width)
    can_move_left = self.can_move_to(self.sprite.center_x - self.sprite.width)# initialise les possibilité de mouvement
    self.base_y = self.sprite.center_y
    self.move_y = -1
    self.move_x = start_direction * MONSTER_MOVEMENT_SPEED_X
    self.move_vertical = False
    self.x_limits = []# cree des limites au monstres pour pas qu'il tombe
    if not can_move_right and not can_move_left:
      self.move_vertical = True
    else:
      self.x_limits = [self.find_limit(-self.sprite.width), self.find_limit(self.sprite.width)]

  # fonction qui s'occupe de bouger le monstre dans la range qui lui est permise
  def move(self):
    """
    definit de le sens des deplacement avec les limites
    """
    if self.move_vertical:
      if self.sprite.center_y >= self.base_y + VERTICAL_MAX_MOVE:
        self.move_y = -MONSTER_MOVEMENT_SPEED_Y
      elif self.sprite.center_y <= self.base_y:
        self.move_y = MONSTER_MOVEMENT_SPEED_Y
      self.sprite.center_y += self.move_y
    else:
      if self.sprite.center_x >= self.x_limits[1]:
        self.move_x = -MONSTER_MOVEMENT_SPEED_X
      elif self.sprite.center_x <= self.x_limits[0]:
        self.move_x = MONSTER_MOVEMENT_SPEED_X
      self.sprite.center_x += self.move_x

  # trouve les limites x de la platforme sur laquelle le monstre est
  def find_limit(self, step):
    limit = self.sprite.center_x + step
    while self.can_move_to(limit):
      limit += step
    return limit - step

  # vérifie la possibilié du monstre à se déplacer vers une certaine position x
  def can_move_to(self, pos_x):
    check_no_void = len(arcade.get_sprites_at_point((pos_x, self.sprite.center_y - self.sprite.height), self.platforms)) > 0
    check_obstacle = len(arcade.get_sprites_at_point((pos_x, self.sprite.center_y), self.platforms)) == 0
    return check_no_void and check_obstacle