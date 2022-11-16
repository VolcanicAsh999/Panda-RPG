from tkinter import *
from tkinter.ttk import Frame, Button, Label, Style
from tkinter import filedialog as tkFileDialog
from general import *
from level import *

def list_to_string(input_list):
  result = ""
    
  first = True
    
  for item in input_list:
    if first:
      first = False
    else:
      result += ";"
      
    result += str(item)
    
  return result
    
def string_to_list(input_string):
  return [] if len(input_string.strip()) == 0 else input_string.split(";")

## Decorator for widget tooltips.

class TooltipDecorator(object):
  def __init__(self, widget, text='widget info'):
    self.widget = widget
    self.text = text
    self.widget.bind("<Enter>",self.enter)
    self.widget.bind("<Leave>",self.close)
    self.top_window = None

  def enter(self, event=None):
    bouding_box = self.widget.bbox("insert")
    
    if bouding_box == None:
      return
    
    x = bouding_box[0]
    y = bouding_box[1]
    cx = bouding_box[2]
    cy = bouding_box[3]
    
    x += self.widget.winfo_rootx() + 25
    y += self.widget.winfo_rooty() + 20
    
    self.top_window = Toplevel(self.widget)
    
    # Leaves only the label and removes the app window
    self.top_window.wm_overrideredirect(True)
    self.top_window.wm_geometry("+%d+%d" % (x, y))
    label = Label(self.top_window, text=self.text, justify='left',
                       background="white", relief='solid', borderwidth=1,
                       font=("times", "12", "normal"))
    label.pack(ipadx=1)

  def close(self, event=None):
    if self.top_window:
      self.top_window.destroy()

## Serves as an input for AnimatedTextureModel info.

class AnimatedTextureModelInput(Frame):
  def __init__(self, parent, *args, **kw):
    Frame.__init__(self, parent, relief=GROOVE, borderwidth=2)
    
    self.label_model = Label(self,text="model name")
    self.input_model = Text(self,height=1,width=30)
    self.tooltip_model = TooltipDecorator(self.input_model,"Model filename.")
    
    self.label_textures = Label(self,text="texture names")
    self.input_textures = Text(self,height=1,width=30)
    self.tooltip_textures = TooltipDecorator(self.input_textures,"Semicolon separated texture filenames.\nThe textures will be cycled through with specified framerate.")
    
    self.label_framerate = Label(self,text="texture framerate")
    self.input_framerate = Text(self,height=1,width=30)
    self.tooltip_framerate = TooltipDecorator(self.input_framerate,"How fast the textures will be changed.")  
    
    self.label_model.pack()
    self.input_model.pack()
    self.label_textures.pack()
    self.input_textures.pack()
    self.label_framerate.pack()
    self.input_framerate.pack()
    
  def clear(self):
    self.input_model.delete("1.0",END)
    self.input_textures.delete("1.0",END)
    self.input_framerate.delete("1.0",END)
    
  ## Returns list of texture names.
  def get_textures(self):
    text = self.input_textures.get("1.0",END).replace("\n","")
    return text.split(";")
    
  def get_model(self):
    text = self.input_model.get("1.0",END).replace("\n","")
    return text
  
  def get_framerate(self):
    text = self.input_framerate.get("1.0",END).replace("\n","")
    
    try:
      return float(text)
    except Exception:
      return 1.0
  
  ## Fills the widget with info from given model.
  def set_model(self,animated_texture_model):
    self.clear()
    self.input_model.insert("1.0",animated_texture_model.model_name)
    self.input_textures.insert("1.0",list_to_string(animated_texture_model.texture_names))
    self.input_framerate.insert("1.0",animated_texture_model.framerate)

  ## Sets the properties of given model by values in the widget.
  def fill_model(self,animated_texture_model):
    animated_texture_model.model_name = self.get_model()
    animated_texture_model.texture_names = self.get_textures()
    animated_texture_model.framerate = self.get_framerate()
