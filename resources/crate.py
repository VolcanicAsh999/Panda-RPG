# Handles initialisation and movement of a crate.

position_crate = game.script_get_position(source)

x = int(position_crate[0])
y = int(position_crate[1])

if event_type == "use":
  position_player = game.script_get_player_position()

  x2 = int(position_player[0])
  y2 = int(position_player[1])
  
  do_move = False
  
  if x == x2:
    if y == y2 + 1:
      # from north
      do_move = True
      new_position = (position_crate[0],position_crate[1] + 1.0)
    elif y == y2 - 1:
      # from south
      do_move = True
      new_position = (position_crate[0],position_crate[1] - 1.0)
  elif y == y2:
    if x == x2 + 1:
      # from west
      do_move = True
      new_position = (position_crate[0] + 1,position_crate[1])
    elif x == x2 - 1:
      # from east
      do_move = True
      new_position = (position_crate[0] - 1,position_crate[1])
  
  if do_move:
    x3 = int(new_position[0])
    y3 = int(new_position[1])
    
    if game.script_get_tile_steppable(x3,y3):
      game.script_set_tile_steppable(x,y,True)
      game.script_move(source,new_position[0],new_position[1],0.2)
      #game.script_set_position(source,new_position[0],new_position[1])
      game.script_set_tile_steppable(x3,y3,False)
      
      game.script_play_sound("crate_drag.wav")
      
elif event_type == "load":
  game.script_set_tile_steppable(x,y,False)
