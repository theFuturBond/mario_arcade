
from pathlib import Path
from os import listdir
import arcade
from constants import *

MAPS_DIRECTORY_PATH = Path("maps")

class Map:
  """
  permet de crée des atributs à cette classe
  on a juste a rapelé la classe dans dautre code pour utiliser la map
  """
  def __init__(self, mapname: str):
    self.level = int(mapname.split('.')[1][3:])
    self.path = MAPS_DIRECTORY_PATH / mapname

  def load(self):
    return arcade.load_tilemap(self.path, TILE_SCALING, use_spatial_hash=True)

# - chercher automatiquement toutes les maps disponibles dans le dossier map suivant le format xxxx.mapXX.tmx
# - trier par ordre de niveau
MAPS = sorted([Map(path) for path in listdir(MAPS_DIRECTORY_PATH) if path.endswith('.tmx')], key=lambda m: m.level)

assert len(MAPS) == len(set([map.level for map in MAPS])), "Un niveau est présent en double"
