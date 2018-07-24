from Randomizer import Randomizer
from RandUtils import RandUtils
ru = RandUtils()
import os, random, subprocess, shutil

GAMEDIR = 'pokered'

def getOppositeDirection(dir):
    d = dir.lower()
    if d == 'north':
        return 'south'
    if d == 'south':
        return 'north'
    if d == 'east':
        return 'west'
    return 'east'


class MapObject():
    def __init__(self, fn, logger=None):
        self.fn = fn
        self.log = logger
        # Change data to be a dict not a list
        self.data = self.read()
        self.header = self.readHeader()
        # I should take all the relevant data out of the data/header and move it into outside objects
        self.isOverworld = self.header["tileset"] == "OVERWORLD"
        self.connections = {
            "NORTH": None,
            "SOUTH": None,
            "EAST": None,
            "WEST": None
        }
        self.warps = {}
    def read(self):
        # I need to rewrite this I was very timid
        fn = self.fn
        obj = {}
        assert os.path.exists(fn), "Invalid Filename! {}".format(fn)
        with open(fn) as f:
            lines = f.read().split('\n')
        # First line should end in :
        assert lines[0].strip()[-1] == ':'
        obj["name"] = lines.pop(0)[:-1]
        obj["blocks"] = []
        db = None
        while len(lines) > 0:
            line = lines.pop(0).strip()
            if line == '':
                if db == None:
                    raise Exception("No db to add!")
                obj["blocks"].append(db)
                db = None
                continue
            if not db:
                if line[:2] == 'db':
                    sep = line.split("db")[1].split(";")
                    db = {}
                    db["addr"] = sep[0].strip()
                    db["descr"] = sep[1].strip()
                    db["rows"] = []
                    continue
                elif line[0] == ';':
                    db = {}
                    db["descr"] = line[1:].strip()
                    db["rows"] = []
                    continue
                raise Exception("Unexpected line {}", line)
            row = {}
            sep = line
            if ';' in sep:
                sep = sep.split(';')
                row["descr"] = sep[1].strip()
                sep = sep[0]
            row["items"] = [x.strip() for x in sep.split(',')]
            db["rows"].append(row)
        self.inp = obj
        return obj
    def write(self):
        assert self.inp, "obj not set!"
        obj = self.inp
        # Return a string with the mapObject in .asm format
        lines = []
        lines.append("{}:".format(obj["name"]))
        for block in obj["blocks"]:
            s = '\t'
            if 'addr' in block:
                s += 'db {} '.format(block['addr'])
            if 'descr' in block:
                s += '; {}'.format(block['descr'])
            lines.append(s)
            for row in block["rows"]:
                s = '\t' +', '.join(row["items"])
                if 'descr' in row:
                    s += ' ; {}'.format(row['descr'])
                lines.append(s)
            lines.append('')
        return '\n'.join(lines)
    def readHeader(self):
        h = {}
        self.hfn = "data/mapHeaders/{}".format(os.path.basename(self.fn))
        content = list(open(self.hfn))
        h["name"] = content.pop(0).split(":")[0].strip()
        h["tileset"] = content.pop(0).split("db")[1].split(";")[0].strip()
        hw = content.pop(0).split("db")[1].split(";")[0].split(",")
        h["height"] = hw[0].strip()
        h["width"] = hw[1].strip()
        l = content.pop(0).split("dw")[1].split(";")[0].strip().split(',')
        h["blocks"] = l[0].strip()
        h["textPointers"] = l[1].strip()
        h["script"] = l[2].strip()
        connections = content.pop(0).split("db")[1].split(";")[0].strip()
        if '|' in connections or connections in ["NORTH", "SOUTH", "WEST", "EAST"]:
            h["connections"] = {}
            for i in range(len(connections.split('|'))):
                d = content.pop(0)
                h["connections"][d.split("_MAP")[0].strip()] = list(map(lambda k: k.strip(), d.split("MAP_CONNECTION")[1].split(",")))
        else:
            h["connections"] = connections
        h["object"] = content.pop(0).split("dw")[1].split(";")[0].strip()
        if len(content) > 0:
            h["postpend"] = content
        return h
    def writeHeader(self):
        h = self.header
        with open(self.hfn,"w") as f:
            f.write("{}:\n".format(h["name"]))
            f.write("\tdb {} ; tileset\n".format(h["tileset"]))
            f.write("\tdb {}, {} ; dimensions (y, x)\n".format(h["height"], h["width"]))
            f.write("\tdw {}, {}, {} ; blocks, texts, scripts\n".format(h["blocks"], h["textPointers"], h["script"]))
            c = "\tdb "
            if type(h["connections"]) == str:
                c += "{} ; connections\n".format(h["connections"])
                f.write(c)
            else:
                c += " | ".join(h["connections"].keys())
                c += " ; connections\n"
                f.write(c)
                for conn in h["connections"]:
                    f.write("\t{}_MAP_CONNECTION {}\n".format(conn, ", ".join(h["connections"][conn])))
            f.write("\tdw {} ; objects\n".format(h["object"]))
            if "postpend" in h:
                f.write(''.join(h["postpend"]))
    def hasConnections(self):
        return self.connections["NORTH"] or self.connections["SOUTH"] or self.connections["EAST"] or self.connections["WEST"]
    def getName(self):
        return self.header['height'].split("_HEIGHT")[0]
    def getConnectionsData(self):
        if type(self.header["connections"]) != dict:
            return []
        return list(map(
            lambda x: {"name": x[1][1] if x[1][0] == self.getName() else x[1][0], "direction": x[0], "details": x[1]},
            self.header["connections"].items()
        ))
    def linkConnection(self, conn, obj):
        if self.log and "PALLET_TOWN" in [obj.getName(), self.getName()]:
            self.log.debug("Connecting {} - {}".format(self.getName(), obj.getName()))
        if (self.connections[conn["direction"]]):
            return # Doesn't need to be setup twice
        self.connections[conn["direction"]] = {
            "destination": obj,
            "x": conn["details"][2],
            "y": conn["details"][3],
            "blocks": conn["details"][4],
            "extra_stuff": conn["details"][5:]# Some maps have an extra argument or two, idk why
        }
    def updateConnections(self):
        if type(self.header["connections"]) != dict:
            return # Is a map without any connections, shouldn't be updated
        def _generateConnList(conn):
            # NORTH_MAP_CONNECTION PALLET_TOWN, ROUTE_1, 0, 0, Route1Blocks
            base = [self.getName(), conn["destination"].getName(), conn["x"], conn["y"], conn["blocks"]]
            if "extra_stuff" in conn:
                base += conn["extra_stuff"]
            return base
        for dir in self.header['connections']:
            self.header['connections'][dir] = _generateConnList(self.connections[dir])
    def getWarpsData(self):
        warps = list(filter(lambda k: k["descr"] == "warps", self.data["blocks"]))[0]["rows"]
        return list(map(
            lambda k: {"name": k["items"][-1], "details": [k["items"][0].split("warp ")[1]] + k["items"][1:]},
            warps
        ))
    def linkWarp(self, warp, num, dest):
        if dest == '-1':
            dest_name = '-1'
        elif dest == '237': # Not sure what to do about the elevator
            dest_name = '237'
        else:
            dest_name = dest.getName()
        if self.log and False: # Temp disabling
            self.log.debug("Linking {} - {}".format(self.getName(), dest_name))
        if num in self.warps:
            return # Already linked the warp don't do it again
        # Really the destination and dest_num should be a tuple, so you can't change one without the other
        self.warps[num] = {
            "destination": dest if type(dest) == MapObject else dest_name,
            "x": warp["details"][0],
            "y": warp["details"][1],
            "dest_num": warp["details"][2],
        }
    def fillMissingWarps(self, dest):
        if dest.getName() not in list(map(lambda w: self.warps[w]["destination"] if type(self.warps[w]["destination"]) == str else self.warps[w]["destination"].getName(), self.warps.keys())):
            for w in self.warps.keys():
                warp = self.warps[w]
                if warp["destination"] == '-1':
                    warp["destination"] = dest
    def updateWarps(self):
        for j in range(len(self.data["blocks"])):
            x = self.data["blocks"][j]
            if x["descr"] == "warps":
                for i in range(len(x["rows"])):
                    last = self.warps[i+1]["destination"]
                    if type(self.warps[i+1]["destination"]) == MapObject:
                        last = last.getName()
                    x["rows"][i]["items"] = ["warp {}".format(self.warps[i+1]["x"]),
                                             self.warps[i+1]["y"],
                                             self.warps[i+1]["dest_num"],
                                             last]

        #	warp 7, 1, 0, REDS_HOUSE_2F ; staircase

# The destnums are fucked up

class Pokemon():
    def __init__(self, fn):
        self.fn = fn
        self.stats = self.readStats()
    def readStats(self):
        s = {}
        with open(self.fn) as f:
            content = f.read().split("\n")
        if ":" in content[0]:
            s["funcDef"] = content.pop(0)
        gValue = lambda s: s.split()[1].strip()
        s["name"] = gValue(content.pop(0))[4:]
        s["hp"] = gValue(content.pop(0))
        s["attack"] = gValue(content.pop(0))
        s["defense"] = gValue(content.pop(0))
        s["speed"] = gValue(content.pop(0))
        s["special"] = gValue(content.pop(0))
        s["type1"] = gValue(content.pop(0))
        s["type2"] = gValue(content.pop(0))
        s["catchRate"] = gValue(content.pop(0))
        s["xpYield"] = gValue(content.pop(0))
        spritedims = content.pop(0).split("INCBIN")[1].split(";")
        s["SpriteDims"] = spritedims[0].strip().split(",")
        s["SpriteDims_desc"] = spritedims[1].strip()
        s["FrontPic"] = gValue(content.pop(0))
        s["BackPic"] = gValue(content.pop(0))
        content.pop(0) # Comment Line
        s["Attack1"] = gValue(content.pop(0))
        s["Attack2"] = gValue(content.pop(0))
        s["Attack3"] = gValue(content.pop(0))
        s["Attack4"] = gValue(content.pop(0))
        s["growth"] = gValue(content.pop(0))
        content.pop(0) # Comment Line
        s["learnset"] = []
        while len(content) > 0 and "tmlearn" in content[0]:
            s["learnset"].append(gValue(content.pop(0)).split(','))
        if len(content) > 0:
            padding = content.pop(0).split("db")[1].split(";")
            s["padding"] = padding[0].strip()
            s["padding_desc"] = padding[1].strip()
        if len(content) > 0:
            s["postpend"] = content
        return s
    def writeStats(self):
        s = self.stats
        with open(self.fn, "w") as f:
            if "funcDef" in s:
                f.write(s["funcDef"]+"\n")
            f.write("db DEX_{} ; {}\n".format(s["name"], "pokedex id"))
            dbw = lambda l,d : f.write("db {} ; {}\n".format(l,d))
            dbw(s["hp"], "base hp")
            dbw(s["attack"], "base attack")
            dbw(s["defense"], "base defense")
            dbw(s["speed"], "base speed")
            dbw(s["special"], "base special")
            dbw(s["type1"], "species type 1")
            dbw(s["type2"], "species type 2")
            dbw(s["catchRate"], "catch rate")
            dbw(s["xpYield"], "base exp yield")
            f.write("INCBIN {} ; {}\n".format(",".join(s["SpriteDims"]), s["SpriteDims_desc"]))
            f.write("dw {}\n".format(s["FrontPic"]))
            f.write("dw {}\n".format(s["BackPic"]))
            f.write("; attacks known at lvl 0\n")
            f.write("db {}\n".format(s["Attack1"]))
            f.write("db {}\n".format(s["Attack2"]))
            f.write("db {}\n".format(s["Attack3"]))
            f.write("db {}\n".format(s["Attack4"]))
            dbw(s["growth"], "growth rate")
            f.write("; learnset\n")
            for tmset in s["learnset"]:
                f.write("\ttmlearn {}\n".format(",".join(tmset)))
            if 'padding' in s:
                dbw(s["padding"], s["padding_desc"])
            if "postpend" in s:
                for l in s["postpend"]:
                    if not l == '':
                        f.write(l + '\n')

class Pokered(Randomizer):
    def __init__(self):
        Randomizer.__init__(self)
        self.gamedir = GAMEDIR
        self.pokemon = {}
        self.map = {}
    def makeMapObject(self, fn):
        return MapObject(fn, self.log)
    def setDir(self):
        os.chdir(self.gamedir)
    def prepare(self):
        self.setDir()
        if "build" not in self.args:
            self.resetGit(files_to_remove=['pokered.gbc'])
    def process(self):
        if not self.args:
            raise Exception("No Arguments Set")
        if "map" in self.args:
            self.resetSeed()
            self.makeMap()
        if "reorder-pokemon" in self.args: # This should not be a public option
            self.resetSeed()
            self.randomize_pokemon_constants() # Tis should not be a public option
        if "reorder-pokedex" in self.args:
            self.resetSeed()
            self.randomize_pokedex_constants()
        if 'starters' in self.args:
            self.resetSeed()
            self.randomize_starters(self.args['starters'])
        if 'types' in self.args:
            self.resetSeed()
            self.randomize_types(self.args['types'])
        if 'warps' in self.args:
            self.resetSeed()
            self.randomize_warps(self.args['warps'])
        if 'connections' in self.args:
            self.resetSeed()
            self.randomize_connections(self.args['connections'])
        if 'skip-intro' in self.args:
            self.resetSeed()
            self.skip_intro()
        if 'wild' in self.args:
            self.resetSeed()
            self.randomize_wilds(self.args['wild'])
        if "rebuild" in self.args or "build" in self.args:
            pass
    def create(self, fn="pokered.gbc"):
        output = subprocess.check_output(['make', 'red'], stderr=subprocess.STDOUT)
        self.log.log(output)
        self.log.output("Pokemon Red Assembled")
        shutil.copyfile('pokered.gbc', '../{}'.format(fn))
        self.log.output("Pokemon Red Copied")
    def makeMap(self):
        if not self.map == {}: # only do this once
            return
        directory = 'data/mapObjects/'
        fns = list(os.walk(directory))[0][2]
        # Create all the map objects and add them to the map
        for f in fns:
            fn = os.path.join(directory,f)
            obj = self.makeMapObject(fn)
            self.map[obj.getName()] = obj
        for key, obj in self.map.items():
            # Link the connections
            for conn in obj.getConnectionsData():
                dest = self.map[conn["name"]]
                obj.linkConnection(conn, dest)
            # Link the warps (outside of the -1 ones)
            warpData = obj.getWarpsData()
            for w in range(len(warpData)):
                warp = warpData[w]
                dest = warp["name"]
                if dest != '-1' and dest != '237':
                    dest = self.map[dest]
                obj.linkWarp(warp, w+1, dest)
        for key, obj in self.map.items():
            warpData = obj.getWarpsData()
            for w in range(len(warpData)):
                warp = warpData[w]
                dest = warp["name"]
                if dest != '-1' and dest != '237':
                    dest = self.map[dest]
                    dest.fillMissingWarps(obj)
    def randomize_constants_1(self, fn, end_lines = []):
        with open(fn, "r") as f:
            inp = f.read().split('\n')
        constants = inp[2:len(inp)-1-len(end_lines)]
        names = list(map(lambda k: k.split()[1], constants))
        random.shuffle(names)
        reordered = []
        for p in range(len(constants)):
            reordered.append('\tconst {}   ; {}'.format(names[p], constants[p].split()[-1])) # Might need exact spacing
        with open(fn, "w") as f:
            f.write("const_value = 1\n\n")
            for line in reordered:
                self.log.log(line)
                f.write(line + '\n')
            for line in end_lines:
                f.write(line)
    def randomize_pokemon_constants(self):
        # This can mess up the sprites pretty badly
        self.log.output("Randomizing Pokemon Constants")
        FN = "constants/pokemon_constants.asm"
        self.randomize_constants_1(FN)
        self.log.output("Pokemon Constants Randomized")
    def randomize_pokedex_constants(self):
        self.log.output("Randomizing Pokedex Constants")
        FN = "constants/pokedex_constants.asm"
        self.randomize_constants_1(FN, end_lines=["\n","NUM_POKEMON    EQU 151"])
        self.log.output("Pokedex Constants Randomized")
    def randomize_starters(self, options=None):
        def _getChooseText(pokemon):
            lines = []
            if pokemon.stats["type1"] == pokemon.stats["type2"]:
                lines.append('\tline "{} #MON,"'.format(pokemon.stats["type1"].lower()))
            else:
                lines.append('\tline "{} and"\n\tcont "{} #MON,"'.format(pokemon.stats["type1"].lower(),pokemon.stats["type2"].lower()))
            lines.append('\tcont "{}?"'.format(pokemon.stats["name"]))
            return lines
        # This should happen last, I'm thinking I should make things happen in a defined order
        self.log.output("Randomizing Starters")
        # Default is to completely randomize starters
            # Read Pokedex Constants
            # Randomly pick 3
            # Replace the starters file
        self.readPokemon() # Create a self.pokemon attribute with a dict of all pokemon
        options = list(self.pokemon.keys())
        random.shuffle(options)
        ru.replaceLine("constants/starter_mons.asm", 1, "STARTER1 EQU {}".format(options[0]))
        ru.replaceLine("constants/starter_mons.asm", 2, "STARTER2 EQU {}".format(options[1]))
        ru.replaceLine("constants/starter_mons.asm", 3, "STARTER3 EQU {}".format(options[2]))
        text1 = _getChooseText(self.pokemon[options[0]])
        text2 = _getChooseText(self.pokemon[options[1]])
        text3 = _getChooseText(self.pokemon[options[2]])
        ru.replaceLine("text/maps/oaks_lab.asm", 43, text3[1])
        ru.replaceLine("text/maps/oaks_lab.asm", 42, text3[0])

        ru.replaceLine("text/maps/oaks_lab.asm", 37, text2[1])
        ru.replaceLine("text/maps/oaks_lab.asm", 36, text2[0])

        ru.replaceLine("text/maps/oaks_lab.asm", 31, text1[1])
        ru.replaceLine("text/maps/oaks_lab.asm", 30, text1[0])
    def randomize_types(self, options=None):
        self.log.output("Randomizing Types")
        self.readPokemon()
        fn = os.path.join('constants','type_constants.asm')
        types = list(map(lambda k: k.split()[0],list(open(fn))[1:]))
        for pokemon in self.pokemon.values():
            pokemon.stats["type1"] = random.choice(types)
            pokemon.stats["type2"] = random.choice(types)
            pokemon.writeStats() # This could be optimized
        # Really this should call another function to update the types in the randomize_starters
            # But that could lead things to be a bit messy, so I'm gonna leave it for now
    def randomize_warps(self, options=None):
        #TODO make it so the overworld maps are in their own randomization pool
        self.log.output("Randomizing warps")
        maps_to_exclude = ['OAKS_LAB', 'SILPH_CO_ELEVATOR']
        self.makeMap()
        mapNames = list(filter(lambda k: k not in maps_to_exclude, self.map))
        def _shuffleEntrances(mapNames):
            warps = []
            for m in mapNames:
                warps += map(lambda w: (w["dest_num"], w["destination"]), self.map[m].warps.values())
            random.shuffle(warps)
            for m in mapNames:
                for w in self.map[m].warps:
                    new = warps.pop()
                    self.map[m].warps[w]["dest_num"] = new[0]
                    self.map[m].warps[w]["destination"] = new[1]
                self.map[m].updateWarps()

                # When I refactor I'm going to want to change this, keep track of all the objects changed
                # so that then you only do file IO once for each necessary file at the end
                with open(self.map[m].fn,"w") as f:
                    f.write(self.map[m].write())
        self.log.output("Randomizing Overworld Warps")
        _shuffleEntrances(list(filter(lambda k: self.map[k].isOverworld, mapNames)))
        self.log.output("Randomizing Other Warps")
        _shuffleEntrances(list(filter(lambda k: not self.map[k].isOverworld, mapNames)))
        self.log.output("Warps Randomized")
    def randomize_connections(self, options=None):
        ONETOONE=True # Connections not being one-to-one is likely to cause map transition bugs
        self.log.output("Randomizing connections")
        self.makeMap()
        mapKeys = list(filter(lambda m: self.map[m].hasConnections(), self.map))
        connections = {"NORTH": [], "SOUTH": [], "EAST": [], "WEST": []}
        connections_set = {"NORTH": [], "SOUTH": [], "EAST": [], "WEST": []}
        for m in mapKeys:
            for direction in self.map[m].connections:
                val = self.map[m].connections[direction]
                if not val:
                    continue
                connections[direction].append((val["destination"], val["blocks"]))
        for dir in connections:
            random.shuffle(connections[dir])
        for m in mapKeys:
            for direction in self.map[m].connections:
                if m in connections_set[direction]:
                    continue
                val = self.map[m].connections[direction]
                if not val:
                    continue
                new = connections[direction].pop()
                self.map[m].connections[direction]["destination"] = new[0]
                self.map[m].connections[direction]["blocks"] = new[1]
                connections_set[direction].append(m)
                if ONETOONE:
                    new_dir = getOppositeDirection(direction).upper()
                    other_connection = list(filter(lambda k: k[0].getName() == m, connections[new_dir]))[0]
                    connections[new_dir].remove(other_connection)
                    new[0].connections[new_dir]["destination"] = other_connection[0]
                    new[0].connections[new_dir]["blocks"] = other_connection[1]
                    connections_set[new_dir].append(new[0].getName())
            self.map[m].updateConnections()
            self.map[m].writeHeader()
    def randomize_wilds(self, options=None):
        # Will eventually be many options
        # Loop through every file
        # Every time theres a spot for a wild pokemon
        # Pick a random one and replace that line
        self.log.output("Randomizing Wild Pokemon Locations")
        self.readPokemon()
        dir = 'data/wildPokemon'
        fns = list(os.walk(dir))[0][2]
        for f in fns:
            fn = os.path.join(dir,f)
            content = list(open(fn))
            for l in range(len(content)):
                line = content[l]
                if "db" in line and "," in line:
                    if line[:2] == "\t\t":
                        indents = "\t\t"
                    else:
                        indents = "\t"

                    content[l] = "{}db {},{}".format(
                        indents,
                        line.split("db")[1].split(",")[0].strip(),
                        random.choice(list(self.pokemon.keys()))
                    )
                    ru.replaceLine(fn,l+1,content[l])
    def skip_intro(self):
        self.log.output("Shortening the intro")
        # Makes oaks intro text less obnoxious
        self.log.log("Make Oaks speech manageable")
        ru.replaceFile(os.path.join("../custom_scripts","oakspeech.asm"), os.path.join("text", "oakspeech.asm"))
        # Starts player in oaks lab (should really start right in front of pokeballs)
        self.log.log("Starting player in oaks lab")
        warpsc = os.path.join("data", "special_warps.asm")
        ru.replaceLine(warpsc, 38, "\tdb OAKS_LAB")
        ru.replaceLine(warpsc, 39, "\tFLYWARP_DATA OAKS_LAB_WIDTH,5,7")
        ru.replaceLine(warpsc, 40, "\tdb OAKS_LAB")
        # Skip trainer battle (still get text right now)
        self.log.log("Skipping First Trainer Battle")
        labscript = os.path.join("scripts", "oakslab.asm")
        ru.addLine(labscript, 2, "\t SetEvent EVENT_OAK_ASKED_TO_CHOOSE_MON")
        ru.addLine(labscript, 380, "\tld [wJoyIgnore], a")
        ru.addLine(labscript, 381, "\tld a, PLAYER_DIR_UP")
        ru.addLine(labscript, 382, "\tld [wPlayerMovingDirection], a")
        ru.addLine(labscript, 383, "\tld a, $c")
        ru.addLine(labscript, 384, "\tld [wOaksLabCurScript], a")
        ru.addLine(labscript, 385, "\tret")
        # Set oak to not appear in pallet town
        self.log.log("Don't see oak in pallet town grass")
        palletscript = os.path.join("scripts", "pallettown.asm")
        ru.addLine(palletscript, 21, "\tret")
        # NEED TO FIGURE OUT
        # Don't let player leave lab without pokemon
        # Don't trigger gary's text at all
           # True Ideal would be making this battle optional
        # Put oak in the lab to start, without triggering any scripts
        # Start with pokedex, so the parcel trip isn't necessary to get pokeballs
        # Oaks speech can be even shorter
        pass
    def readPokemon(self):
        if not self.pokemon == {}:
            return # Don't run this multiple times
        dir = 'data/baseStats'
        for f in list(os.walk(dir))[0][2]:
            fn = os.path.join(dir,f)
            p = Pokemon(fn)
            self.pokemon[p.stats["name"]] = p

if __name__ == "__main__":
    if False:
        # Hard to make a real test, but check that all the warps get sent through properly
        os.chdir(GAMEDIR)
        rand = Pokered()
        rand.makeMap()
        for map in rand.map:
            rand.map[map].updateWarps()
            out = rand.map[map].write()
            with open(rand.map[map].fn, "w") as f:
                f.write(out)
    elif False:
        # Check that the connections all get sent through properly
        os.chdir(GAMEDIR)
        rand = Pokered()
        rand.makeMap()
        for map in rand.map:
            rand.map[map].updateConnections()
            rand.map[map].writeHeader()
    elif False:
        # Turn this into a unit test someday
        dir = 'pokered/data/mapObjects/'
        fns = list(os.walk(dir))[0][2]
        for f in fns:
            fn = os.path.join(dir, f)
            obj = MapObject(fn)
            s = open(fn).read()
            obj.writeHeader()
            s2 = open(fn).read()
            assert s == s2, "files differ!"
    elif False:
        p = Pokemon('pokered/data/baseStats/bulbasaur.asm')
        p.writeStats()
    elif False:
        # Also should be a unit test someday
        dir = 'pokered/data/baseStats/'
        fns = list(os.walk(dir))[0][2]
        for f in fns:
            fn = os.path.join(dir,f)
            old = open(fn).read().strip()
            poke = Pokemon(fn)
            poke.writeStats()
            assert old == open(fn).read().strip(), "files differ!"
    elif False:
        # Turn this into a unit test someday
        mp = []
        dir = 'pokered/data/mapObjects/'
        fns = list(os.walk(dir))[0][2]
        c = 0
        for f in fns:
            fn = os.path.join(dir,f)
            obj = MapObject(fn)
            s = open(fn).read().strip()
            inp = obj.read()
            for db in inp["blocks"]:
                mp.append(db["descr"])
            out = obj.write(inp).strip()
            c += 1
            assert s == out, "files differ!"
    else:
        rand = Pokered()
        rand.prepare()
        rand.process()
        rand.create()