# Handles hurting effects of a hurt potion

game.script_change_player_hp(-3) # hurt

pos = game.script_get_position(source)
game.script_set_position(source, 100, 100) # remove hurt potion from map

data = game.script_get_data(source)

# deactivate potion
if data == "hurt potion":
    game.script_set_data(source, "used hurt potion")
elif data == "used hurt potion":
    game.script_change_player_hp(3)
else:
    game.script_change_player_hp(3)

#double-check that the tile is steppable
if game.script_get_tile_steppable(pos[0], pos[1]) == False:
    game.script_set_tile_steppable(pos[0], pos[1], True)
