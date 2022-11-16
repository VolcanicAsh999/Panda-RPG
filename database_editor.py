from tkinter import *
from tkinter.ttk import Frame, Button, Label, Style, Notebook
from tkinter import filedialog as tkFileDialog
from direct.actor.Actor import Actor
import math
from general import *
from game_database import *
from level import *
from general_gui import *

class Tab(Frame):
  def __init__(self, parent, database):
    Frame.__init__(self, parent)
    self.parent = parent
    self.database = database
    self.button_widgets = {}
    self.text_widgets = {}
    self.model_widgets = {}
    self.check_widgets = {}
    self.label_widgets = {}
    self.next_row = 0

  def add_button(self,name,grid_x=0,grid_y=None,command=None):
    if grid_y == None:
      grid_y = self.next_row
      self.next_row += 1
    
    self.button_widgets[name] = Button(self,text=name,command=command)
    self.button_widgets[name].grid(row=grid_y,column=grid_x,sticky=N + S + W + E)

  def add_text_input(self,name,grid_x=0,grid_y=None):
    if grid_y == None:
      grid_y = self.next_row
      self.next_row += 1
    
    self.text_widgets[name] = Text(self, height=1, width=30)
    self.text_widgets[name].grid(row=grid_y,column=grid_x,sticky=N + S + W + E)

  def add_model_input(self,name,grid_x=0,grid_y=None):
    if grid_y == None:
      grid_y = self.next_row
      self.next_row += 1
    
    self.model_widgets[name] = AnimatedTextureModelInput(self)
    self.model_widgets[name].grid(row=grid_y,column=grid_x,sticky=N + S + W + E)

  def add_label(self,name,text=None,grid_x=0,grid_y=None):
    if grid_y == None:
      grid_y = self.next_row
      self.next_row += 1
    if text == None:
      text = name
      name = 'label%s%s'%(grid_x,grid_y)
    
    label = Label(self, text=text)
    label.grid(row=grid_y,column=grid_x,sticky=N + S + W + E)
    self.label_widgets[name] = label

  def set_text_label(self,name,text):
    self.label_widgets[name]['text'] = text

  def add_checkbutton(self,name,grid_x=0,grid_y=None):
    if grid_y == None:
      grid_y = self.next_row
      self.next_row += 1

    var = StringVar()
    self.check_widgets[name] = (Checkbutton(self,text=name,variable=var), var)
    self.check_widgets[name][0].grid(row=grid_y,column=grid_x,sticky=N + S + W + E)

  def get_check_value(self,name):
    return (self.check_widgets[name][1].get() == '1')

  def set_check_value(self,name,value):
    self.check_widgets[name][1].set('1' if value else '0')

  def get_text_value(self,name):
    return self.text_widgets[name].get("1.0",END).replace("\n","")

  def set_text_value(self,name,text):
    self.text_widgets[name].delete("1.0",END)
    self.text_widgets[name].insert("1.0",text)

class TabWithIDList(Tab):
  def __init__(self, parent, database): 
    Tab.__init__(self, parent, database)
    self.helper_line = 0
    self.selected_id = -1
    
  def create_list(self,on_change_command):
    self.listbox = Listbox(self)
    self.listbox.grid(row=0,column=1,rowspan=self.next_row)
    self.listbox.bind('<<ListboxSelect>>',self.on_listbox_change)
    self.list_update_command = on_change_command

  def get_selected_item_id(self):
    try:
      selection = self.listbox.curselection()
      selected_item_text = self.listbox.get(selection[0])
      helper = selected_item_text.split(" ")

      return int(helper[0])
    except Exception as e:
      # list clicked but no items => index exception
      return -1  

  def on_listbox_change(self,event):
    self.selected_id = self.get_selected_item_id()
      
    if self.selected_id >= 0:
      self.list_update_command()
    
  def clear_list(self):
    self.listbox.delete(0,END)
    self.helper_line = 0
    
  def add_item_to_list(self,int_id,string_description):
    self.listbox.insert(self.helper_line,str(int_id) + " " + string_description)
    self.helper_line += 1

class ItemTab(TabWithIDList):
  def __init__(self, parent, database):
    TabWithIDList.__init__(self, parent, database)
    
    self.selected_id = None          # non negative integer id or None
    self.init_ui()
    self.update_listbox()
    self.update_item_info()

  def init_ui(self):
    self.style = Style()
    self.style.theme_use("default")
   
    self.add_label("id")
    self.add_text_input("id")
    self.add_label("name")
    self.add_text_input("name")
    self.add_label("model")
    self.add_model_input("item model")
    self.add_button("edit item",command=self.on_edit_item_click)
    self.add_button("new item",command=self.on_new_item_type_click)
    self.add_button("delete item",command=self.on_delete_item_click)
   
    self.create_list(self.on_list_change)
   
    self.pack(fill=BOTH, expand=1)

  def on_new_item_type_click(self):
    self.selected_id = self.database.new_item_type()
    self.update_listbox()

  def on_list_change(self):
    self.update_item_info()

  def on_edit_item_click(self):
    if self.selected_id != None:
      selected_item = self.database.get_item_types()[self.selected_id]
      
      selected_item.name = self.get_text_value("name")
      self.model_widgets["item model"].fill_model(selected_item.model)
      
      self.database.get_item_types().pop(self.selected_id,None)
      self.database.get_item_types()[self.selected_id] = selected_item
      
      self.update_item_info()
      self.update_listbox()
    
  def on_delete_item_click(self):
    if self.selected_id != None:
      self.database.get_item_types().pop(self.selected_id,None)
      self.selected_id = None
    
    self.update_listbox()
    self.update_item_info()
    
  def update_listbox(self):
    items = self.database.get_item_types()
    
    self.clear_list()
    
    for item_id in items:
      self.add_item_to_list(item_id,self.database.item_types[item_id].name)
      
  def update_item_info(self):
    if self.selected_id != None:
      selected_item = self.database.get_item_types()[self.selected_id]
      
      self.set_text_value("id",self.selected_id)
      self.set_text_value("name",selected_item.name)
      self.model_widgets["item model"].set_model(selected_item.model)
    else:
      self.set_text_value("id","")
      self.set_text_value("name","")
      self.model_widgets["item model"].clear()

class NPCTab(TabWithIDList):
  def __init__(self, parent, database):
    TabWithIDList.__init__(self, parent, database)
    
    self.selected_id = None
    self.init_ui()  
    self.update_listbox()
    self.update_npc_info()

  def init_ui(self):
    self.style = Style()
    self.style.theme_use("default")
   
    self.add_label("id")
    self.add_text_input("id")
    self.add_label("name")
    self.add_text_input("name")
    self.add_label("max health")
    self.add_text_input("max health")
    self.add_label("max strength")
    self.add_text_input("max strength")
    self.add_label("scale")
    self.add_text_input("scale")
    self.set_text_value("scale","1.0")
    self.add_checkbutton("is idle")
    #self.add_label("models name")
    #self.add_text_input("models name")
    #self.add_label("texture filename")
    #self.add_text_input("texture filename")
    self.add_model_input("npc model")
    self.add_label("label1", "anim: (anims=[])")
    self.add_text_input("anim")
    self.add_button("edit npc",command=self.on_edit_npc_click)
    self.add_button("new npc",command=self.on_new_npc_type_click)
    self.add_button("delete npc",command=self.on_delete_npc_click)
    
    self.create_list(self.on_list_change)
   
    self.pack(fill=BOTH, expand=1)

  def update_listbox(self):
    npcs = self.database.get_npc_types()
    
    self.clear_list()
    
    for npc_id in npcs:
      self.add_item_to_list(npc_id,self.database.npc_types[npc_id].name)

  def on_list_change(self):
    self.update_npc_info()

  def update_npc_info(self):
    if self.selected_id != None:
      selected_npc = self.database.get_npc_types()[self.selected_id]

      self.set_text_value("id",self.selected_id)
      self.set_text_value("name",selected_npc.name)
      self.set_text_value("max health",selected_npc.max_health)
      self.set_text_value("max strength",selected_npc.max_strength)
      self.set_text_value("scale",str(selected_npc.scale))
      self.set_check_value("is idle",selected_npc.idle)
      self.set_text_value("anim",selected_npc.anim)
      a='['+str(Actor('resources\\'+selected_npc.model.model_name)).split('[')[-1]
      self.set_text_label("label1","anim: (anims=%s)"%(a if a else '["idle"]'))
      self.model_widgets["npc model"].set_model(selected_npc.model)
    else:
      self.set_text_value("id","")
      self.set_text_value("name","")
      self.set_text_value("max health","")
      self.set_text_value("max strength","")
      self.set_text_value("scale","1.0")
      self.set_check_value("is idle","")
      self.set_text_value("anim","idle")
      self.set_text_label("label1","anim: (anims=[])")
      self.model_widgets["npc model"].clear()

  def on_new_npc_type_click(self):
    self.selected_id = self.database.new_npc_type()
    self.update_listbox()

  def on_edit_npc_click(self):
    if self.selected_id != None:
      selected_npc = self.database.get_npc_types()[self.selected_id]
      
      selected_npc.name = self.get_text_value("name")
      selected_npc.max_health = self.get_text_value("max health")
      selected_npc.max_strength = self.get_text_value("max strength")
      selected_npc.idle = self.get_check_value("is idle")
      selected_npc.scale = float(self.get_text_value("scale"))
      selected_npc.anim = self.get_text_value("anim")
      self.model_widgets["npc model"].fill_model(selected_npc.model)
      
      self.database.get_npc_types().pop(self.selected_id,None)
      self.database.get_npc_types()[self.selected_id] = selected_npc
      
      self.update_npc_info()
      self.update_listbox()
    
  def on_delete_npc_click(self):
    if self.selected_id != None:
      self.database.get_npc_types().pop(self.selected_id,None)
      self.selected_id = None
    
    self.update_listbox()
    self.update_item_info()

class MainTab(Tab):
  def __init__(self, parent, database):
    Tab.__init__(self, parent, database)
    self.init_ui()  

  def init_ui(self):
    self.add_button("load database",0,0,self.on_load_click)
    self.add_button("save database",0,1,self.on_save_click)
    self.pack(fill=BOTH, expand=1)
    
  def on_save_click(self):
    filename = tkFileDialog.asksaveasfilename()
    
    if len(filename) == 0:
      return
    
    GameDatabase.save_to_file(self.database,filename)    
  
  def on_load_click(self):
    filename = tkFileDialog.askopenfilename()
    
    if len(filename) == 0:
      return
    
    self.database = GameDatabase.load_from_file(filename)
    
    self.parent.tab_items.database = self.database
    self.parent.tab_items.update_listbox()

    self.parent.tab_npcs.database = self.database
    self.parent.tab_npcs.update_listbox()
    
def main():
  root = Tk()
  root.title("database editor")
  notebook = Notebook(root)
  
  database = GameDatabase()
  
  notebook.tab_main = MainTab(notebook,database)
  notebook.tab_items = ItemTab(notebook,database)
  notebook.tab_npcs = NPCTab(notebook,database)
  
  notebook.add(notebook.tab_main,text='Main')
  notebook.add(notebook.tab_items,text='Items')
  notebook.add(notebook.tab_npcs,text='NPCs')
  
  notebook.pack()
  
  root.mainloop()  

if __name__ == '__main__':
  main()  
