from Randomizer import Randomizer
from RandUtils import RandUtils
ru = RandUtils()
import os, random, subprocess, shutil

GAMEDIR = 'pokered'

class MapObject():
    def __init__(self, fn):
        self.fn = fn
        self.data = self.read()
    def read(self):
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
    def prepare(self):
        os.chdir(self.gamedir)
        if "build" not in self.args:
            self.resetGit(files_to_remove=['pokered.gbc'])
    def process(self):
        if not self.args:
            raise Exception("No Arguments Set")
        for arg in self.args:
            self.resetSeed()
            if arg == "reorder-pokemon":
                self.randomize_pokemon_constants()
            if arg == "reorder-pokedex":
                self.randomize_pokedex_constants()
            if arg == 'starters':
                self.randomize_starters(self.args['starters'])
            if arg == 'warps':
                self.randomize_warps(self.args['warps'])
            if arg == 'skip-intro':
                # Probably necessary when randomizing the map, but nice anyway
                self.skip_intro()
            if arg == "rebuild" or arg == "build":
                pass
    def create(self, fn="pokered.gbc"):
        output = subprocess.check_output(['make', 'red'], stderr=subprocess.STDOUT)
        self.log.log(output)
        self.log.output("Pokemon Red Assembled")
        shutil.copyfile('pokered.gbc', '../{}'.format(fn))
        self.log.output("Pokemon Red Copied")
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
        # Default is to completely randomize starters
            # Read Pokedex Constants
            # Randomly pick 3
            # Replace the starters file
        pass
    def randomize_warps(self, options=None):
        self.log.output("Randomizing warps")
        maps_to_exclude = ['pallettown.asm', 'redshouse1f.asm','redshouse2f.asm', 'oakslab.asm']
        dir = 'data/mapObjects'
        assert os.path.isdir(dir)
        objs = []
        warp_constants = []
        for f in list(os.walk(dir))[0][2]:
            if f in maps_to_exclude:
                self.log.output("Excluding {}".format(f))
                continue
            fn = os.path.join(dir,f)
            obj = MapObject(fn)
            obj.read()
            objs.append(obj)
            for block in obj.inp["blocks"]:
                if block["descr"] == "warps":
                    for row in block["rows"]:
                        warp_constants.append(row["items"][-1])
        self.log.output("{} constants added".format(len(warp_constants)))
        self.log.log("RANDOMIZING")
        self.log.output(sorted(list(set(warp_constants))))
        random.shuffle(warp_constants)
        for obj in objs:
            for b in range(len(obj.inp["blocks"])):
                block = obj.inp["blocks"][b]
                if block["descr"] == "warps":
                    for r in range(len(block["rows"])):
                        obj.inp["blocks"][b]["rows"][r]["items"][-1] = warp_constants.pop()
            out = obj.write()
            with open(obj.fn,"w") as f:
                f.write(obj.write())
        self.log.output("Warps Randomized")
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

if __name__ == "__main__":
    if False:
        p = Pokemon('pokered/data/baseStats/bulbasaur.asm')
        p.writeStats()
    elif True:
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