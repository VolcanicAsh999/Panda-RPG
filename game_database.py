from general import *
import pickle

## Describes an item (such as a potion, a sword etc.).

class ItemType:
  def __init__(self):
    self.name = ""
    self.model = AnimatedTextureModel()

## Describes an NPC (such as a town guard, a forest troll etc.).

class NPCType:
  def __init__(self):
    self.name = ""
    self.model = AnimatedTextureModel()
    self.max_health = 100
    self.max_strength = 100
    self.idle = False
    self.scale = 1.0
    self.anim = ''

class GameDatabase:
  def __init__(self):
    self.item_types = {}  # items by non negative ids
    self.npc_types = {}   # npcs by non negative ids
    
    self.next_item_id = 0
    self.next_npc_id = 0
    
  def get_item_types(self):
    return self.item_types
  
  def get_npc_types(self):
    return self.npc_types
  
  ## Creates a new ItemType object in the databse, returns
  #  its ID.
  
  def new_item_type(self):
    new_item_type = ItemType()
    
    while self.next_item_id in self.item_types:
      self.next_item_id += 1
      
    self.item_types[self.next_item_id] = new_item_type
    self.next_item_id += 1
    
    return self.next_item_id - 1

  def new_npc_type(self):
    new_npc_type = NPCType()
    
    while self.next_npc_id in self.npc_types:
      self.next_npc_id += 1
    
    self.npc_types[self.next_npc_id] = new_npc_type
    self.next_npc_id += 1
    
    return self.next_npc_id - 1
  
  @staticmethod
  def save_to_file(game_database, filename):
    output_file = open(filename,"wb")
    pickle.dump(game_database,output_file)
    output_file.close()
  
  @staticmethod
  def load_from_file(filename):
    input_file = open(filename,"rb")
    database = GameDatabase()
    result = unpickle_backwards_compatible(database,input_file)  
    input_file.close()
    return result
