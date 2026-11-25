from constants import *

VERTICAL_MAX_MOVE = 200
HORIZONTAL_MAX_MOVE = 200

PLATFORM_MOVE_TYPE_X = 1 << 1
PLATFORM_MOVE_TYPE_Y = 1 << 2

class MovingPlatform:
    """
    cree le deplacement des plateforme
    """
    def __init__(self, sprite, move_type):
        self.sprite = sprite
        self.base_y = self.sprite.center_y
        self.base_x = self.sprite.center_x
        self.move_y_speed = MONSTER_PLATFORM_SPEED_Y
        self.move_x_speed = MONSTER_PLATFORM_SPEED_X
        self.move_type = move_type

    def move_y(self):
        """
        cree des deplacement verticaux
        """
        if self.sprite.center_y >= self.base_y + VERTICAL_MAX_MOVE:
            self.move_y_speed = -MONSTER_PLATFORM_SPEED_Y
        elif self.sprite.center_y <= self.base_y - VERTICAL_MAX_MOVE:
            self.move_y_speed = MONSTER_PLATFORM_SPEED_Y
        self.sprite.center_y += self.move_y_speed

    def move_x(self):
        """
        cree des deplacement horizontaux
        """
        if self.sprite.center_x >= self.base_x + HORIZONTAL_MAX_MOVE:
            self.move_x_speed = -MONSTER_PLATFORM_SPEED_X
        elif self.sprite.center_x <= self.base_x - HORIZONTAL_MAX_MOVE:
            self.move_x_speed = MONSTER_PLATFORM_SPEED_X
        self.sprite.center_x += self.move_x_speed

    def move(self):
        if self.move_type == PLATFORM_MOVE_TYPE_X:
            self.move_x()
        elif self.move_type == PLATFORM_MOVE_TYPE_Y:
            self.move_y()
        else:
            self.move_x_speed()
            self.move_y_speed()
