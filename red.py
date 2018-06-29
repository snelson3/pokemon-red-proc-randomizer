from Randomizer import Randomizer
import os, random, subprocess, shutil

GAMEDIR = 'pokered'

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
        names = map(lambda k: k.split()[1], constants)
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

if __name__ == "__main__":
    rand = Pokered()
    rand.prepare()
    rand.process()
    rand.create()