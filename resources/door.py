# script for door - the door prop data should be a string:
# "m;x;y;a"
# m - destination map TODO, empty represents this map
# x - destination x float position
# y - destination y float position
# a - destination rotation in angles

data = game.script_get_data(source).split(";")

game.script_set_player_position(float(data[1]),float(data[2]))
game.script_set_player_rotation(float(data[3]),0)
