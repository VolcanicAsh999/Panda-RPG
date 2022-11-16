# Handles healing effects of a healing potion

game.script_change_player_hp(3) # heal

pos = game.script_get_position(source)
game.script_set_position(source, 100, 100) # remove healing potion from map

data = game.script_get_data(source)

# deactivate potion
if data == "health potion":
    game.script_set_data(source, "used health potion")
elif data == "used health potion":
    game.script_change_player_hp(-3)
else:
    game.script_change_player_hp(-3)

# double-check that the tile is steppable
if game.script_get_tile_steppable(pos[0], pos[1]) == False:
    game.script_set_tile_steppable(pos[0], pos[1], True)
