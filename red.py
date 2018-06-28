from Randomizer import Randomizer
import os

GAMEDIR = 'pokered'

class Pokered(Randomizer):
    def __init__(self, seed=None):
        Randomizer.__init__(self, seed)
        self.gamedir = GAMEDIR
    def prepare(self):
        os.chdir(self.gamedir)
        self.resetGit(files_to_remove='pokered.gbc')
    def process(self):
        self.resetSeed()
        if not self.args:
            raise Exception("No Arguments Set")
        if "reorder-pokedex" in args:
            randomize_pokemon_constants()
    def create(self, fn="pokered.gbc"):
        output = subprocess.check_output(['make', 'red'], stderr=subprocess.STDOUT)
        self.log.log(output)
        self.log.output("Pokemon Red Assembled")

        shutil.copyfile('pokered.gbc', '../{}'.format(fn))
        self.log.output("Pokemon Red Copied")
    def randomize_pokemon_constants():
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
                log(line)
                f.write(line + '\n')
        self.log.output("Pokemon Constants Randomized")

if __name__ == "__main__":
    rand = Pokered()
    rand.setArguments()
    # Setting a seed in the arguments does nothing, should pass them in  when creating
    rand.prepare()
    rand.process()
    rand.create()