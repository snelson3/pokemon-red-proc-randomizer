from red import *

rand = Pokered()
rand.setDir()
rand.makeMap()

loc = "null"
curr = list(rand.map.keys())
options = {}

def getOptions():
    o = {}
    for conn in curr.connections:
        if curr.connections[conn]:
            o[conn[0].lower()] = curr.connections[conn]
    for w in range(len(curr.warps)):
        o[w] = curr.warps[w+1] # the +1 is weird/confusing
    return o

def getName(thing):
    if type(thing) == MapObject:
        return thing.getName()
    return thing

print("Welcome to a Pokemon Red Mapper")

while loc != "exit":


    if type(curr) == list:

        for i in range(len(curr)):
            print("{}: {}".format(i, getName(curr[i])))

        loc = input("Select the map you want to start on\n")

        if loc in [str(i) for i in range(len(curr))]:
            curr = rand.map[getName(curr[int(loc)])]
            options = getOptions()
    else:
        for i in options:
            print("{}: {}".format(i, getName(options[i]['destination'])))

        loc = input("Select the map to go to\n")

        if loc in [str(i) for i in options]:
            if loc not in ['n','s','w','e']:
                loc = int(loc)
            curr = rand.map[getName(options[loc]['destination'])]
            options = getOptions()

# Problem because the .connections[] are all mapObjects and the .warps[] are a mix (when updating)
# the connections aren't working
# places like reds house 1f that have a -1 and a specific place are getting the specific places overwritten
# Once it seems like the map can be traversed, make unit tests that update the values to be what they should be
# connections should be exactly right
# warps shouldn't, as the -1 will be filled in, go through github to quickly verify that nothing looks weird

# Then I can add connection randomizers and warp randomizers very easily

# Right places like RedsHouse1F have a inside map linking to it, and an outside map
# So to fix I should only fillmissing warps if the dest isn't already listed