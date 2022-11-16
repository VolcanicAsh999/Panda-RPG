import pickle

RESOURCE_PATH = "resources/"

## Represents a model that has either static or animated frame animated texture.

class AnimatedTextureModel:
  def __init__(self):
    self.model_name = ""
    self.texture_names = []
    self.framerate = 1.0

  def copy(self):
    return copy.deepcopy(self)

## Unpickles an object from given opened file. The difference from normal
#  pickle.load is that this function initialises also the object's
#  attributes that weren't pickled, thus preserving backward compatibility.

def unpickle_backwards_compatible(to_what_object,input_file):
  loaded_object = pickle.load(input_file)
  
  for attribute in loaded_object.__dict__:
    setattr(to_what_object,attribute,getattr(loaded_object,attribute,None))
    
  return to_what_object
