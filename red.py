from Randomizer import Randomizer
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

class Pokered(Randomizer):
    def __init__(self):
        Randomizer.__init__(self)
        self.gamedir = GAMEDIR
    def prepare(self):
        os.chdir(self.gamedir)
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
            if arg == "rebuild":
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




if __name__ == "__main__":
    if False:
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