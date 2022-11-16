from general import *
import pickle
import copy

## Represents one level tile.

class LevelTile:
  def __init__(self):
    self.wall = False                                ##< whether the tile is a wall (True) or floor (False)
    self.ceiling = False                             ##< whether the tile has a ceiling (ceiling can also be above walls)
    self.ceiling_height = 1.0
    self.floor_orientation = 0                       ##< rotation of the floor, possible values: 0, 1, 2, 3
    self.wall_model = AnimatedTextureModel()         ##< model for wall 
    self.floor_model = AnimatedTextureModel()        ##< model for floor
    self.ceiling_model = AnimatedTextureModel()      ##< model for ceiling
    self.steppable = not self.wall                   ##< whether the tile can be stepped on

  def copy(self):
    return copy.deepcopy(self)
    
  ## Checks if the tile is empty (has no model). Empty tile can still have ceiling.
    
  def is_empty(self):
    return (self.wall and len(self.wall_model.model_name) == 0) or (not self.wall and len(self.floor_model.model_name) == 0)
    
## Represents an item placed in the level.
    
class LevelItem:
  def __init__(self, position=[0.0,0.0], orientation=0):
    self.position = position             ##< (x,y) float position
    self.orientation = orientation       ##< rotation in degrees
    self.data = ""                       ##< may contain arbitrary data relevant to the object
    self.db_id = 0                       ##< ID of the item in the game database

    # scripts (filenames):

    self.scripts_pickup = []             ##< called when the item is picked up

  def copy(self):
    return copy.deepcopy(self)
    
## Represents a level prop, for example a column. Prop has its position and orientation
#  but doesnt affect anything in the game and has no colissions.

class LevelProp:
  def __init__(self, position=[0.0,0.0], orientation=0):
    self.model = AnimatedTextureModel()
    self.position = position             ##< (x,y) float position
    self.orientation = orientation       ##< rotation in degrees
    self.caption = ""                    ##< caption displayed in the game, "" = no caption
    self.data = ""                       ##< may contain arbitrary data relevant to the object

    # scripts (filenames):

    self.scripts_load = []               ##< called when the prop is created
    self.scripts_use = []                ##< called when the prop is used
    self.scripts_examine = []            ##< called when the prop is examind (looked at from short distance so that its label displays)

  def copy(self):
    return copy.deepcopy(self)

class LevelNpc:
  def __init__(self, position=[0.0,0.0], orientation=0):
    self.model = AnimatedTextureModel()
    self.position = position
    self.orientation = orientation
    self.caption = ""
    self.data = ""
    self.db_id = 0
    self.anim = []

    self.scripts_load = []
    self.scripts_interact = []

  def copy(self):
    return copy.deepcopy(self)
    
## Represents one game level.

class Level:
  ## Class static method, saves the level into given file.
  
  @staticmethod
  def save_to_file(level, filename):
    output_file = open(filename,"wb")
    pickle.dump(level,output_file)
    output_file.close()
  
  ## Class static method, loads the level from given file and returns it.
  #  the level argument has to be there because of python interpreter
  #  for some reason.
  
  @staticmethod
  def load_from_file(filename):
    input_file = open(filename,"rb")
    level = Level(1,1)
    result = unpickle_backwards_compatible(level,input_file)
    input_file.close()
    return result
  
  ## Returns a 2D list representing the level collision mask (x, y
  #  coordinates contain either True - steppable, or False - not
  #  steppable)
  
  def get_collision_mask(self):
    result = []
    
    for i in range(self.get_width()):
      result.append([])
      for j in range(self.get_height()):
        result[i].append(self.get_tile(i,j).steppable)
          
    return result
    
  def __init__(self, width, height, default_tile=None):
    self.layout = [[None for i in range(height)] for j in range(width)]
    self.width = width
    self.height = height
    self.skybox_textures = []              ##< contains names of skybox textures that are being chained between during daytime
    self.ambient_light_amount = 0.5        ##< amount of ambient light in range <0,1>
    self.fog_color = (0.5,0.5,0.5)         ##< fog color
    self.fog_distance = 10
    self.diffuse_lights = [(1.0,1.0,1.0),(0.5,0.5,0.5)]  ##< list of light colors (3-item tuples tuples) that are interpolated between during daytime
    self.props = []
    self.items = []
    self.npcs = []
    self.name = ""                         ##< level name
    self.database_name = "resources\\db.txt"                ## name of the database file

    for i in range(len(self.layout)):
      for j in range(len(self.layout[0])):
        if default_tile == None:
          self.layout[i][j] = LevelTile()
        else:
          self.layout[i][j] = LevelTile(default_tile)

  def get_database_name(self):
    return "resources/db.txt"#self.database_name
  
  def set_database_name(self, new_name):
    self.database_name = new_name
    return new_name

  ## Resizes the map.

  def set_size(self, new_width, new_height):
    old_size = (self.get_width(),self.get_height())
    old_layout = self.layout
    
    self.width = new_width
    self.height = new_height
    
    self.layout = [[None for i in range(new_height)] for j in range(new_width)]
    
    for i in range(len(self.layout)):
      for j in range(len(self.layout[0])):
        try:
          self.layout[i][j] = old_layout[i][j]
        except Exception:
          self.layout[i][j] = LevelTile()

  def set_fog_distance(self,distance):
    self.fog_distance = distance

  def get_fog_distance(self):
    return self.fog_distance

  def add_prop(self, prop):
    self.props.append(prop)

  def add_item(self, item):
    self.items.append(item)

  def add_npc(self, npc):
    self.npcs.append(npc)

  def get_props(self):
    return self.props

  def get_items(self):
    return self.items

  def get_npcs(self):
    return self.npcs

  def get_width(self):
    return self.width

  def set_name(self, name):
    self.name = name
    
  def get_name(self):
    return self.name

  def get_height(self):
    return self.height
  
  ## Sets the lighting properties of the level.
  #
  #  @param ambient_light_amount amount of ambient light in range <0,1>
  #  @param diffuse_lights list of light colors (3-item tuples tuples) that are interpolated between during daytime
  
  def set_light_properties(self,ambient_light_amount, diffuse_lights):
    self.ambient_light_amount = ambient_light_amount
    self.diffuse_lights = diffuse_lights
    
  def get_ambient_light_amount(self):
    return self.ambient_light_amount
  
  def get_diffuse_lights(self):
    return self.diffuse_lights
  
  ## Sets the fog color.
  #
  #  @param fog_color fog color (three item tuple of floats in range <0,1>)
  
  def set_fog_color(self, fog_color):
    self.fog_color = fog_color
    
  def get_fog_color(self):
    return self.fog_color
  
  ## Sets the names of skybox textures used for different
  #  times of day.
  #
  #  @param texture_names list of texture names, the textures
  #         will be chenged between depending on the time of day
  
  def set_skybox_textures(self, texture_names):
    self.skybox_textures = texture_names
    
  ## Gets the list of skybox texture names.
    
  def get_skybox_textures(self):
    return self.skybox_textures

  def get_tile(self, x, y):
    return self.layout[x][y]
  
  def set_tile(self, x, y, tile):
    try:
      self.layout[x][y] = tile
    except Exception:
      pass
  
  def is_wall(self, x, y):
    if x < 0 or y < 0 or x >= self.get_width() or y >= self.get_height():
      return True
    
    return self.layout[x][y].wall
