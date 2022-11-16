import math
from general_gui import *
import tkinter.filedialog as tkFileDialog

## Frame that can be scrolled.
class ScrolledFrame(Frame):
  def __init__(self, parent, *args, **kw):
    Frame.__init__(self, parent, *args, **kw)
    
    # create a canvas object and a vertical scrollbar for scrolling it

    vscrollbar = Scrollbar(self,orient=VERTICAL)
    vscrollbar.pack(fill=Y,side=RIGHT,expand=FALSE)
    
    hscrollbar = Scrollbar(self,orient=HORIZONTAL)
    hscrollbar.pack(fill=X,side=BOTTOM,expand=FALSE)
    
    canvas = Canvas(self,bd=0,highlightthickness=0,yscrollcommand=vscrollbar.set,xscrollcommand=hscrollbar.set)
    canvas.pack(side=LEFT,fill=BOTH,expand=TRUE)
    
    vscrollbar.config(command=canvas.yview)
    hscrollbar.config(command=canvas.xview)
    
    # reset the view
    canvas.xview_moveto(0)
    canvas.yview_moveto(0)
    # create a frame inside the canvas which will be scrolled with it
    self.interior = interior = Frame(canvas)
    interior_id = canvas.create_window(0,0,window=interior,anchor=NW)
    
    # track changes to the canvas and frame width and sync them, also updating the scrollbar
    
    def _configure_interior(event):
      # update the scrollbars to match the size of the inner frame
      size = (interior.winfo_reqwidth(),interior.winfo_reqheight())
      canvas.config(scrollregion="0 0 %s %s" % size)
    
    interior.bind('<Configure>',_configure_interior)
    
    def _configure_canvas(event):
      return

    canvas.bind('<Configure>',_configure_canvas)

class MapEditor(ScrolledFrame):
  TILE_SIZE = 20
  PROP_SIZE = 15         
  SMALL_TILE_SIZE = 14         # for displaying ceiling
  PADDING_X = 3
  PADDING_Y = 1
  BORDER_COLOR = "white"       # border color of non selected objects on the map
  
  def __init__(self, parent):
    ScrolledFrame.__init__(self, parent)   
    self.selected_tile = None        ##< selected tile coordinates or None
    self.selected_prop = None        ##< selected prop reference or None
    self.selected_item = None        ##< selected item reference or None
    self.selected_npc = None
    self.parent = parent
    self.init_ui()
        
  def on_save_file_click(self):
    filename = tkFileDialog.asksaveasfilename()
    
    if len(filename) == 0:
      return
    
    Level.save_to_file(self.level,filename)
   
  def on_new_item_click(self):
    new_item = LevelItem()
    new_item.position = (1.0,1.0)
    self.level.add_item(new_item)
    self.redraw_level()
   
  def on_load_file_click(self):
    filename = tkFileDialog.askopenfilename()
    
    if len(filename) == 0:
      return
    
    self.level = Level.load_from_file(filename)
    self.selected_tile = None
    self.redraw_level()
    self.update_gui_info()
   
  def on_is_wall_click(self):
    self.set_check("is steppable", not self.get_check("is wall"))
   
  def on_set_map_info_click(self):
    self.level.set_name(self.get_text("name"))
    self.level.set_skybox_textures(string_to_list(self.get_text("skybox textures")))
    self.level.set_database_name(self.get_text("database"))
    diffuse_lights = self.get_text("daytime colors").replace(" ", "").split(";")
   
    for i in range(len(diffuse_lights)):
      values = diffuse_lights[i][1:-1].split(",")
      diffuse_lights[i] = (float(values[0]),float(values[1]),float(values[2]))
      
    self.level.set_light_properties(float(self.get_text("ambient light amount")),diffuse_lights)
    
    self.level.set_size(int(self.get_text("width")),int(self.get_text("height")))
    self.level.set_fog_distance(float(self.get_text("fog distance")))
    
    fog_color = self.get_text("fog color").replace(" ", "")[1:-1].split(",")
    fog_color = (float(fog_color[0]),float(fog_color[1]),float(fog_color[2]))
    self.level.set_fog_color(fog_color)
    
    self.selected_tile = None
    self.redraw_level()
    
  def on_new_prop_click(self):
    new_prop = LevelProp()
    new_prop.position = (1.0,1.0)
    self.level.add_prop(new_prop)
    self.redraw_level()

  def on_new_npc_click(self):
    new_npc = LevelNpc()
    new_npc.position = (1.0,1.0)
    self.level.add_npc(new_npc)
    self.redraw_level()
    
  def on_set_prop_item_properties_click(self):
    if self.selected_item != None:
      self.set_item_properties()
    elif self.selected_prop != None:
      self.set_prop_properties()
    elif self.selected_npc != None:
      self.set_npc_properties()
    
  def set_item_properties(self):
    if self.selected_item == None:
      return

    helper_list = self.get_text("item position").split(";")
    self.selected_item.position = (float(helper_list[0]),float(helper_list[1]))
    self.selected_item.orientation = float(self.get_text("item orientation"))
    self.selected_item.data = self.get_text("item data")
    self.selected_item.db_id = self.get_text("item DB ID")
    self.selected_item.scripts_pickup = string_to_list(self.get_text("scripts - pick up"))

    self.redraw_level()
    self.update_gui_info()
    return

  def set_npc_properties(self):
    if self.selected_npc == None:
      return

    helper_list = self.get_text("npc position").split(";")
    self.selected_npc.position = (float(helper_list[0]),float(helper_list[1]))
    self.selected_npc.orientation = float(self.get_text("npc orientation"))
    self.selected_npc.data = self.get_text("npc data")
    self.selected_npc.db_id = self.get_text("npc DB ID")
    self.selected_npc.scripts_load = string_to_list(self.get_text("scripts - load"))
    self.selected_npc.scripts_interact = string_to_list(self.get_text("scripts - interact"))

    self.redraw_level()
    self.update_gui_info()
    return
    
  def on_delete_prop_item_click(self):
    props = self.level.get_props()
    items = self.level.get_items()
    npcs = self.level.get_npcs()
    
    for i in range(len(props)):
      if props[i] == self.selected_prop:
        del props[i]
        break
      
    for i in range(len(items)):
      if items[i] == self.selected_item:
        del items[i]
        break

    for i in range(len(npcs)):
      if items[i] == self.selected_item:
        del items[i]
        break
      
    self.selected_prop = None
    self.selected_item = None
    self.selected_npc = None
    self.redraw_level()
    self.update_gui_info()

  def on_duplicate_prop_item_click(self):
    if self.selected_prop != None:
      new_prop = self.selected_prop.copy()
      new_prop.position = (1.0,1.0)
      self.level.add_prop(new_prop)
      self.redraw_level()
    elif self.selected_item != None:
      new_item = self.selected_item.copy()
      new_item.position = (1.0,1.0)
      self.level.add_item(new_item)
      self.redraw_level()
    elif self.selected_npc != None:
      new_npc = self.selected_npc.copy()
      new_npc.position = (1.0,1.0)
      self.level.add_npc(new_npc)
      self.redraw_level()
    
  def set_prop_properties(self):
    if self.selected_prop == None:
      return
    
    helper_list = self.get_text("prop position").split(";")
    self.selected_prop.position = (float(helper_list[0]),float(helper_list[1]))
    self.model_widgets["prop model"].fill_model(self.selected_prop.model)
    self.selected_prop.orientation = float(self.get_text("prop orientation"))
    self.selected_prop.caption = self.get_text("caption")
    self.selected_prop.data = self.get_text("prop data")
    self.selected_prop.scripts_load = string_to_list(self.get_text("scripts - load"))
    self.selected_prop.scripts_use = string_to_list(self.get_text("scripts - use"))
    self.selected_prop.scripts_examine = string_to_list(self.get_text("scripts - examine"))
    
    self.redraw_level()
    self.update_gui_info()
    
  ## Checks if clicked coordinates are near given point, for selection by clicking.
    
  def clicked_near(self, clicked_where_coords, near_where_coords):
    dx = clicked_where_coords[0] - near_where_coords[0]
    dy = clicked_where_coords[1] - near_where_coords[1]
    
    distance = math.sqrt(dx * dx + dy * dy)
    
    return distance < 0.7
    
  def on_canvas_click(self, event):   # left click
    prop_clicked = None
    item_clicked = None
    npc_clicked = None
    
    if self.get_check("display props"):
      for prop in self.level.get_props():
        coordinates = self.pixel_to_world_coordinates(event.x,event.y)
        
        if self.clicked_near(coordinates,prop.position):
          prop_clicked = prop
          break
        
    if self.get_check("display items"):
      for item in self.level.get_items():
        coordinates = self.pixel_to_world_coordinates(event.x,event.y)
        
        if self.clicked_near(coordinates,item.position):
          item_clicked = item
          prop_clicked = None
          break

      if self.get_check("display npcs"):
        for npc in self.level.get_npcs():
          coordinates = self.pixel_to_world_coordinates(event.x,event.y)

          if self.clicked_near(coordinates,npc.position):
            npc_clicked = npc
            prop_clicked = None
            item_clicked = None
            break
      
    if prop_clicked != None:
      self.selected_prop = prop_clicked
      self.selected_tile = None
      self.selected_item = None
      self.selected_npc = None
    elif item_clicked != None:
      self.selected_prop = None
      self.selected_npc = None
      self.selected_tile = None
      self.selected_item = item_clicked
    elif npc_clicked != None:
      self.selected_prop = None
      self.selected_item = None
      self.selected_tile = None
      self.selected_npc = npc_clicked
    else:
      self.selected_prop = None
      self.selected_item = None
      self.selected_npc = None
      self.selected_tile = self.pixel_to_tile_coordinates(event.x,event.y)
    
    self.redraw_level()
    self.update_gui_info()

  def on_canvas_click2(self, event):  # right click 
    try:
      if self.selected_tile != None:
        clicked_tile = self.pixel_to_tile_coordinates(event.x,event.y)
        tile = self.level.get_tile(clicked_tile[0],clicked_tile[1])
        tile.wall = self.get_check("is wall")
        tile.ceiling = self.get_check("has ceiling")
        self.model_widgets["wall model"].fill_model(tile.wall_model)
        self.model_widgets["floor model"].fill_model(tile.floor_model)
        self.model_widgets["ceiling model"].fill_model(tile.ceiling_model)
        tile.floor_orientation = int(self.get_text("orientation"))
        tile.steppable = self.get_check("is steppable")
        tile.ceiling_height = float(self.get_text("ceiling height"))
      elif self.selected_prop != None or self.selected_item != None or self.selected_npc != None:
        selected_thing = None
        selected_thing = self.selected_prop if self.selected_prop != None else selected_thing
        selected_thing = self.selected_item if self.selected_item != None else selected_thing
        selected_thing = self.selected_npc if self.selected_npc != None else selected_thing
        
        selected_thing.position = self.pixel_to_world_coordinates(event.x,event.y)
        
        if self.get_check("stick to grid"):
          selected_thing.position = (round(selected_thing.position[0] * 2) / 2.0,round(selected_thing.position[1] * 2) / 2.0)
        
      self.redraw_level()
      self.update_gui_info()
    except Exception:
      print("error")
    
  def color_to_string(self, color):
    return "(" + str(color[0]) + "," + str(color[1]) + "," + str(color[2]) + ")"
    
  ## Sets text in given text widget (of given name).
    
  def set_text(self, name, text):
    self.text_widgets[name].delete("1.0",END)
    self.text_widgets[name].insert("1.0",text)
    
  def get_text(self, name):
    return self.text_widgets[name].get("1.0",END).replace("\n","")
    
  ## Sets checkbox value of checkbox of given name.
    
  def set_check(self, name, bool_value):
    self.checkbox_widgets[name].value.set(bool_value == True)
    
  ## Gets a bool value of a checkbox of given name.
    
  def get_check(self, name):
    return self.checkbox_widgets[name].value.get() == True
    
  ## Updates the info in GUI, i.e. selected tile information etc.
    
  def update_gui_info(self):
    self.set_text("width",str(self.level.get_width()))
    self.set_text("height",str(self.level.get_height()))
    self.set_text("name",self.level.get_name())
    self.set_text("ambient light amount",str(self.level.get_ambient_light_amount()))
    self.set_text("skybox textures",list_to_string(self.level.get_skybox_textures()))
    self.set_text("daytime colors",list_to_string(self.level.get_diffuse_lights()).replace(" ",""))
    self.set_text("fog color",self.color_to_string(self.level.get_fog_color()))
    self.set_text("fog distance",float(self.level.get_fog_distance()))
    self.set_text("database",self.level.get_database_name())
    
    if self.selected_tile != None:
      tile = self.level.get_tile(self.selected_tile[0],self.selected_tile[1])
      self.set_text("tile coordinates",str(self.selected_tile[0]) + ";" + str(self.selected_tile[1]))
 
      self.model_widgets["wall model"].set_model(tile.wall_model)
      self.model_widgets["floor model"].set_model(tile.floor_model)
      self.model_widgets["ceiling model"].set_model(tile.ceiling_model)
      self.set_text("ceiling height",str(tile.ceiling_height))
      self.set_text("orientation",str(tile.floor_orientation))
      self.set_check("is wall",tile.wall)
      self.set_check("is steppable",tile.steppable)
      self.set_check("has ceiling",tile.ceiling)
    else:
      self.set_text("tile coordinates","")
      self.model_widgets["wall model"].clear()
      self.model_widgets["floor model"].clear()
      self.model_widgets["ceiling model"].clear()
      self.set_text("ceiling height","")
      self.set_text("orientation","")
      self.set_check("is wall",False)
      self.set_check("has ceiling",False)
      self.set_check("is steppable",False)
      
    if self.selected_prop != None:
      self.set_text("prop position",str(self.selected_prop.position[0]) + ";" + str(self.selected_prop.position[1]))
      self.set_text("prop orientation",str(self.selected_prop.orientation))
#      self.set_text("prop model",self.selected_prop.model.model_name)
#      self.set_text("prop textures",list_to_string(self.selected_prop.model.texture_names))
#      self.set_text("prop framerate",str(self.selected_prop.model.framerate))

      self.model_widgets["prop model"].set_model(self.selected_prop.model)

      self.set_text("caption",str(self.selected_prop.caption))
      self.set_text("prop data",str(self.selected_prop.data))
      self.set_text("scripts - load",list_to_string(self.selected_prop.scripts_load))
      self.set_text("scripts - use",list_to_string(self.selected_prop.scripts_use))
      self.set_text("scripts - examine",list_to_string(self.selected_prop.scripts_examine))
    else:
      self.set_text("prop position","")
      self.set_text("prop orientation","")

      self.model_widgets["prop model"].clear()

#      self.set_text("prop model","")
#      self.set_text("prop textures","")
#      self.set_text("prop framerate","")
      self.set_text("caption","")
      self.set_text("prop data","")
      self.set_text("scripts - load","")
      self.set_text("scripts - use","")
      self.set_text("scripts - examine","")

    if self.selected_npc != None:
      self.set_text("npc position",str(self.selected_npc.position[0]) + ";" + str(self.selected_npc.position[1]))
      self.set_text("npc orientation",str(self.selected_npc.orientation))
      self.set_text("npc DB ID",str(self.selected_npc.db_id))

      self.set_text("caption",str(self.selected_npc.caption))
      self.set_text("npc data",str(self.selected_npc.data))
      self.set_text("scripts - load",list_to_string(self.selected_npc.scripts_load))
      self.set_text("scripts - interact",list_to_string(self.selected_npc.scripts_interact))
    else:
      self.set_text("npc position","")
      self.set_text("npc orientation","")
      self.set_text("npc DB ID","")

      self.set_text("caption","")
      self.set_text("npc data","")
      self.set_text("scripts - load","")
      self.set_text("scripts - interact","")

    if self.selected_item != None:
      self.set_text("item position",str(self.selected_item.position[0]) + ";" + str(self.selected_item.position[1]))
      self.set_text("item orientation",str(self.selected_item.orientation))
      self.set_text("item DB ID",str(self.selected_item.db_id))  
      self.set_text("scripts - pick up",list_to_string(self.selected_item.scripts_pickup))
      self.set_text("item data",self.selected_item.data)
    else:
      self.set_text("item position","")
      self.set_text("item orientation","")
      self.set_text("item DB ID","")
      self.set_text("scripts - pick up","")
      self.set_text("item data","")
      
  ## Returns integer tile coordinates from canvas pixel coordinates.
      
  def pixel_to_tile_coordinates(self, x, y):
    return (int(math.floor(x / MapEditor.TILE_SIZE)),int(math.floor(y / MapEditor.TILE_SIZE)))
  
  ## Same as pixel_to_tile_coordinates but returns floats coordiantes.
  
  def pixel_to_world_coordinates(self, x, y):
    return (float(x) / MapEditor.TILE_SIZE,float(y) / MapEditor.TILE_SIZE)
  
  def world_to_pixel_coordinates(self, x, y):
    return (int(x * self.TILE_SIZE),int(y * self.TILE_SIZE))
  
  ## Computes color for AnimatedTextureModel object as its hash based on attributes checked
  #  in GUI (display texture, display model etc.). Returns tkinter color string.
   
  def compute_model_color(self, model):
    textures = ""
  
    for texture_name in model.texture_names:
      textures += texture_name
  
    red = hash(model.model_name) % 256
    green = hash(textures) % 256
    blue = hash(model.model_name + textures) % 256
    
    return ("#%0.2x" % red) + ("%0.2x" % green) + ("%0.2x" % blue)
   
  def redraw_level(self):
    self.canvas.config(width=self.level.get_width() * MapEditor.TILE_SIZE, height=self.level.get_height() * MapEditor.TILE_SIZE)
    self.canvas.delete("all")
    
    small_tile_offset = math.floor((MapEditor.TILE_SIZE - MapEditor.SMALL_TILE_SIZE) / 2)
    
    half_tile_size = MapEditor.TILE_SIZE / 2
    
    for y in range(self.level.get_height()):
      for x in range(self.level.get_width()):
        corner1 = (x * MapEditor.TILE_SIZE, y * MapEditor.TILE_SIZE)
        corner2 = (corner1[0] + MapEditor.TILE_SIZE - 1, corner1[1] + MapEditor.TILE_SIZE - 1)
        
        tile = self.level.get_tile(x,y)
        
        if tile.wall:
          fill_color = self.compute_model_color(self.level.get_tile(x,y).wall_model)
        else:
          fill_color = self.compute_model_color(self.level.get_tile(x,y).floor_model)
        
        ceiling_color = self.compute_model_color(self.level.get_tile(x,y).ceiling_model)
           
        if tile.wall:       # wall
          self.canvas.create_rectangle(corner1[0], corner1[1], corner2[0], corner2[1], outline="black", fill=fill_color)
        else:               # floor
          self.canvas.create_rectangle(corner1[0], corner1[1], corner2[0], corner2[1], outline=fill_color, fill=fill_color)

          if self.get_check("display orientation"):
            if tile.floor_orientation == 0:
              p1 = (corner1[0] + 1,corner2[1] - 1)
              p2 = (corner2[0] + 1,corner2[1] - 1)
            elif tile.floor_orientation == 1:
              p1 = (corner1[0] + 1,corner1[1] - 1)
              p2 = (corner1[0] + 1,corner2[1] - 1)
            elif tile.floor_orientation == 2:
              p1 = (corner1[0] + 1,corner1[1] - 1)
              p2 = (corner2[0] + 1,corner1[1] - 1)
            else:
              p1 = (corner2[0] + 1,corner1[1] - 1)
              p2 = (corner2[0] + 1,corner2[1] - 1)
              
            p3 = (corner1[0] + half_tile_size,corner1[1] + half_tile_size)
            
            self.canvas.create_polygon(p1[0],p1[1],p2[0],p2[1],p3[0],p3[1],outline="white",fill="green")

        if tile.ceiling and self.get_check("display ceiling"):
          self.canvas.create_rectangle(corner1[0] + small_tile_offset, corner1[1] + small_tile_offset, corner2[0] - + small_tile_offset, corner2[1] - + small_tile_offset, outline=ceiling_color, fill=ceiling_color)

        if self.selected_tile != None and self.selected_tile[0] == x and self.selected_tile[1] == y:
          self.canvas.create_rectangle(corner1[0], corner1[1], corner2[0], corner2[1], outline="red")

    # draw props:
    
    if self.get_check("display props"):
      for prop in self.level.get_props():
        border = MapEditor.BORDER_COLOR
      
        if prop == self.selected_prop:
          border = "red"
        
        position = self.world_to_pixel_coordinates(prop.position[0],prop.position[1])
      
        difference = MapEditor.PROP_SIZE / 2
  
        fill_color = self.compute_model_color(prop.model)
        self.canvas.create_oval(position[0] - difference,position[1] - difference, position[0] + difference, position[1] + difference, fill=fill_color, outline=border)
        self.canvas.create_line(position[0],position[1],position[0] + int(math.cos(math.radians(prop.orientation)) * difference),position[1] - int(math.sin(math.radians(prop.orientation)) * difference),fill="black")
  
    # draw items:
    
    if self.get_check("display items"):
      for item in self.level.get_items():
        border = MapEditor.BORDER_COLOR
        
        if item == self.selected_item:
          border = "red"
        
        position = self.world_to_pixel_coordinates(item.position[0],item.position[1])
        difference = MapEditor.TILE_SIZE / 2
      
        self.canvas.create_polygon(position[0] - difference,position[1] - difference,position[0] + MapEditor.TILE_SIZE - difference,position[1] - difference,position[0] + MapEditor.TILE_SIZE / 2 - difference,position[1] + MapEditor.TILE_SIZE - difference,fill="green",outline=border)

    if self.get_check("display npcs"):
      for npc in self.level.get_npcs():
        border = MapEditor.BORDER_COLOR

        if npc == self.selected_npc:
          border = "red"

        position = self.world_to_pixel_coordinates(npc.position[0],npc.position[1])
        difference = MapEditor.TILE_SIZE / 2
        self.canvas.create_oval(position[0] - difference + 2, position[1] - difference, position[0] + difference - 2, position[1] + difference, fill=fill_color, outline=border)
        self.canvas.create_line(position[0],position[1],position[0] + int(math.cos(math.radians(npc.orientation)) * difference),position[1] - int(math.sin(math.radians(npc.orientation)) * difference),fill="black")
    
  ## Adds given widget to given place in grid layout.

  def add_widget(self, widget, grid_x, grid_y, column_span=1, row_span=1, spread_x=False, tooltip=""):
    stick = W + N
    
    if spread_x:
      stick = stick + E
    
    widget.grid(row=grid_x, column=grid_y, rowspan=row_span, columnspan=column_span, padx=MapEditor.PADDING_X, pady=MapEditor.PADDING_Y, sticky=stick)

    if len(tooltip) != 0:   # add tooltip
      widget.tooltip_decorator = TooltipDecorator(widget,text=tooltip)
     
  def add_name_value_input(self, name, left=True, tooltip=""):
    column = 0 if left else 3
    row = self.current_row_left if left else self.current_row_right
    
    self.label_widgets[name] = Label(self.interior, text=name)
    self.add_widget(self.label_widgets[name],row,column)
    
    self.text_widgets[name] = Text(self.interior, height=1, width=30)
    self.add_widget(self.text_widgets[name],row,column + 1,tooltip=tooltip)
    
    if left:
      self.current_row_left += 1
    else:
      self.current_row_right += 1
    
  def add_separator(self, left=True):
    column = 0 if left else 3
    row = self.current_row_left if left else self.current_row_right
    
    self.add_widget(Label(self.interior,text="----------------------\n"),row,column,1,2,True)
    
    if left:
      self.current_row_left += 1
    else:
      self.current_row_right += 1
    
  def add_name_check_input(self, name, checked=False, command=None, left=True, tooltip=""):
    column = 0 if left else 3
    row = self.current_row_left if left else self.current_row_right
    
    self.label_widgets[name] = Label(self.interior, text=name)
    self.add_widget(self.label_widgets[name],row,column)
    
    value = IntVar()
    
    self.checkbox_widgets[name] = Checkbutton(self.interior,variable=value,command=command)
    self.checkbox_widgets[name].value = value
    self.add_widget(self.checkbox_widgets[name],row,column + 1,tooltip=tooltip)
    
    self.set_check(name,checked)
    
    if left:
      self.current_row_left += 1
    else:
      self.current_row_right += 1

  def add_name_model_input(self, name, command=None, left=True, tooltip=""):
    column = 0 if left else 3
    row = self.current_row_left if left else self.current_row_right
    
    self.label_widgets[name] = Label(self.interior,text=name)
    self.add_widget(self.label_widgets[name],row,column,tooltip=tooltip)
   
    self.model_widgets[name] = AnimatedTextureModelInput(self.interior)
    self.add_widget(self.model_widgets[name],row,column + 1,row_span=6)
    
    if left:
      self.current_row_left += 6
    else:
      self.current_row_right += 6
      
  def add_button(self, name, command=None, left=True, tooltip=""):
    column = 0 if left else 3
    row = self.current_row_left if left else self.current_row_right
    
    self.button_widgets[name] = Button(self.interior,text=name,command=command)
    self.add_widget(self.button_widgets[name],row,column,2,1,True,tooltip=tooltip)
        
    if left:
      self.current_row_left += 1
    else:
      self.current_row_right += 1
      
  def init_ui(self):
    self.parent.title("map editor")
    self.style = Style()
    self.style.theme_use("default")
    self.pack(fill=BOTH, expand=1)
        
    self.label_widgets = {}
    self.text_widgets = {}
    self.checkbox_widgets = {}
    self.button_widgets = {}
    self.model_widgets = {}
    
    self.current_row_left = 0
    self.current_row_right = 0
    
    self.add_button("save file",self.on_save_file_click,tooltip="Saves the map to file.")
    self.add_button("load file",self.on_load_file_click,tooltip="Loads a map from file.")
    self.add_name_value_input("name",tooltip="Map name.")
    self.add_name_value_input("skybox textures",tooltip="Semicolon separated filenames of skybox textures that will be cycled through during each day.")
    self.add_name_value_input("daytime colors",tooltip="Semicolon separated colors in format (R,G,B) where each component is\n0.0 - 1.0, e.g. \"(0,0.5,0);(1,1,0.7)\". Colors will be cycled thorough during each day.")
    self.add_name_value_input("ambient light amount",tooltip="Number 0 - 1 specifying how much ambient light there will be.")
    self.add_name_value_input("fog color",tooltip="Color in format (R,G,B) where each component is number 0 - 1.")
    self.add_name_value_input("fog distance",tooltip="How far the fog will be.")
    self.add_name_value_input("width",tooltip="Map width in squares.")
    self.add_name_value_input("height",tooltip="Map height in squares.") 
    self.add_name_value_input("database",tooltip="Name of the database file for the map.")
    self.add_button("set map info",self.on_set_map_info_click,tooltip="Applies the above entered map info.")
    self.add_name_value_input("tile coordinates",tooltip="Selected tile coordinates, read only.")

    self.add_name_model_input("wall model",command=None,left=True,tooltip="Wall model, if the tile is wall.")
    self.add_name_model_input("floor model",command=None,left=True,tooltip="Floor model, if the tile is floor.")
    self.add_name_model_input("ceiling model",command=None,left=True,tooltip="Ceiling model, if the tile has one.")

    self.add_name_value_input("ceiling height",tooltip="Height of the ceiling above the ground.")
    self.add_name_value_input("orientation",tooltip="Orientation of the tile. This can be used to rotate the tile by 90 degrees steps. Values: 0 = up, 1 = right, 2 = down, 3 = left.")
    self.add_name_check_input("is wall",command=self.on_is_wall_click,tooltip="Whether the selected tile is wall (will be floor if unchecked).")
    self.add_name_check_input("is steppable",tooltip="Whether the tile can be walked on.")
    self.add_name_check_input("has ceiling",tooltip="Whether the tile has a ceiling above it.")
    
    self.add_button("new prop",self.on_new_prop_click,left=False,tooltip="Creates a new prop.")
    self.add_name_value_input("prop position",left=False,tooltip="Position of the prop in tiles (doesn't have to be integer).")
    self.add_name_value_input("prop orientation",left=False,tooltip="Prop rotation in degrees CCW.")

    self.add_name_model_input("prop model",command=None,left=False,tooltip="Prop model.")
    
    self.add_name_value_input("caption",left=False,tooltip="Ingame prop caption that will appear when player looks at it.")
    self.add_name_value_input("prop data",left=False,tooltip="String data of the prop, can be used to store data for use in scripts.")

    self.add_name_value_input("scripts - load",left=False,tooltip="Filename of a script that will be run when the prop is loaded.")
    self.add_name_value_input("scripts - use",left=False,tooltip="Filename of a script that will be run when the prop is used.")
    self.add_name_value_input("scripts - examine",left=False,tooltip="Filename of a script that will be run when the prop is looked at.")
    
    self.add_button("new item",self.on_new_item_click,left=False,tooltip="Creates a new item.")
    self.add_name_value_input("item position",left=False,tooltip="Item position in tiles (doesn't have to be integer).")
    self.add_name_value_input("item orientation",left=False,tooltip="Item rotation in degrees CCW.")
    self.add_name_value_input("item DB ID",left=False,tooltip="Database ID of the concrete item this item will represent.")
    self.add_name_value_input("scripts - pick up",left=False,tooltip="Filename of a script that will be run when the item is picked up.")
    self.add_name_value_input("item data",left=False,tooltip="String data of the item, can be used to store data for use in scripts.")

    self.add_button("new npc",self.on_new_npc_click,left=False,tooltip="Creates a new npc.")
    self.add_name_value_input("npc position",left=False,tooltip="Npc position in tiles (doesn't have to be integer).")
    self.add_name_value_input("npc orientation",left=False,tooltip="Npc rotation in degrees CCW.")
    self.add_name_value_input("npc DB ID",left=False,tooltip="Database ID of the concrete npc this npc will represent.")
    self.add_name_value_input("scripts - load",left=False,tooltip="Filename of a script that will be run when the npc is loaded.")
    self.add_name_value_input("scripts - interact",left=False,tooltip="Filename of a script thar will be run when the npc is interacted with.")
    self.add_name_value_input("npc data",left=False,tooltip="String data of the npc, can be used to store data for use in scripts.")

    self.add_button("set prop/item/npc properties",left=False,command=self.on_set_prop_item_properties_click,tooltip="Sets the data entered above for currently selected item or prop.")
    self.add_button("duplicate prop/item/npc",left=False,command=self.on_duplicate_prop_item_click,tooltip="Duplicates currently selected prop or item.")
    self.add_button("delete prop/item/npc",left=False,command=self.on_delete_prop_item_click,tooltip="Deletes currently selected prop or item.")
    
    self.add_name_check_input("stick to grid",True,self.redraw_level,left=False,tooltip="If checked, props and items will stick to a grid when moved.")
    self.add_name_check_input("display texture",True,self.redraw_level,left=False,tooltip="If checked, texture names will affect the color of the objects in editor.")
    self.add_name_check_input("display model",True,self.redraw_level,left=False,tooltip="If checked, model names will affect the color of the objects in editor.")
    self.add_name_check_input("display ceiling",True,self.redraw_level,left=False,tooltip="If checked, ceilings will be displayed.")
    self.add_name_check_input("display props",True,self.redraw_level,left=False,tooltip="If checked, props will be displayed.")
    self.add_name_check_input("display items",True,self.redraw_level,left=False,tooltip="If checked, items will be displayed.")
    self.add_name_check_input("display npcs",True,self.redraw_level,left=False,tooltip="If checked, npcs will be displayed.")
    self.add_name_check_input("display ceiling height",True,self.redraw_level,left=False,tooltip="If checked, ceiling heights be displayed. NOT IMPLEMENTED YET.")
    self.add_name_check_input("display orientation",False,self.redraw_level,left=False,tooltip="If checked, tile orientations will be displayed as arrows.")
    
    self.canvas = Canvas(self.interior, width=200, height=100, background="white", borderwidth=2, relief=SUNKEN)
    self.add_widget(self.canvas,0,2,1,max(self.current_row_left,self.current_row_right) + 1)
    
    self.canvas.bind("<Button-1>", self.on_canvas_click)
    self.canvas.bind("<Button-3>", self.on_canvas_click2)
    
    self.selected_tile = (0,0)
    
    self.level = Level(30,30)
    self.redraw_level()
    self.update_gui_info()
    
def main():
  root = Tk()
  root.geometry("1280x1100")
  app = MapEditor(root)
  root.mainloop()

if __name__ == '__main__':
  main()  

d_floors={'floor_flat.obj':('grass.png','pavement.png'),
          'tile_warped.obj':'dirt.png',
    }
d_props={'column_bulwark.obj':'wall_bulwark.png',
         'plant.obj':'plant.png',
         'prop_arc.obj':'wall_bulwark.png',
         'corner_house.obj':'house.png',
         'corner_cave.obj':'dirt_wall.png',
         'fence.obj':'wood.png',
    }
d_ceilings={'ceiling_warped.obj':'dirt2.png',
    }
d_walls={'wall_cave.obj':'dirt_wall.png',
         'wall_bulwark.obj':'wall_bulwark.png',
         'wall_house.obj':'house.png',
    }
