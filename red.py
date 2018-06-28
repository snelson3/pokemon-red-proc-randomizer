from Randomizer import Randomizer
import os, random, subprocess, shutil

GAMEDIR = 'pokered'

class Pokered(Randomizer):
    def __init__(self, seed=None):
        Randomizer.__init__(self, seed)
        self.gamedir = GAMEDIR
    def prepare(self):
        os.chdir(self.gamedir)
        self.resetGit(files_to_remove=['pokered.gbc'])
    def process(self):
        if not self.args:
            raise Exception("No Arguments Set")
        for arg in self.args:
            self.resetSeed()
            if arg == "reorder-pokedex":
                self.randomize_pokemon_constants()
            if arg == "rebuild":
                pass
    def create(self, fn="pokered.gbc"):
        output = subprocess.check_output(['make', 'red'], stderr=subprocess.STDOUT)
        self.log.log(output)
        self.log.output("Pokemon Red Assembled")
        shutil.copyfile('pokered.gbc', '../{}'.format(fn))
        self.log.output("Pokemon Red Copied")
    def randomize_pokemon_constants(self):
        # This messes up the sprites real bad I think
        self.log.output("Randomizing Pokemon Constants")
        FN = "constants/pokemon_constants.asm"
        with open(FN, "r") as f:
            inp = f.read().split('\n')
        pokemon = inp[2:len(inp)-1]
        names = map(lambda k: k.split()[1], pokemon)
        random.shuffle(names)
        reordered = []
        for p in range(len(pokemon)):
            reordered.append('\tconst {}   ; {}'.format(names[p], pokemon[p].split()[-1]))
        with open(FN, "w") as f:
            for line in reordered:
                self.log.log(line)
                f.write(line + '\n')
        self.log.output("Pokemon Constants Randomized")

if __name__ == "__main__":
    rand = Pokered()
    rand.setArguments()
    # Setting a seed in the arguments does nothing, should pass them in  when creating
    rand.prepare()
    rand.process()
    rand.create()