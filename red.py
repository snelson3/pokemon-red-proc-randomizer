# TODO Make this more generic so it tends to work for any randomizer
# Maybe two levels of abstraction
# Need to setup the environment, perform the randomization, and finish things up
# But parts of this will be useful for my generic univeral randomizer

import os, subprocess, shutil, time, random, sys

LOGNAME = 'recent.log'
GAMEDIR = 'pokered'

# Seed should be set before every different randomization function is called
seed = time.time()
random.seed(seed)

def startlog():
    open(LOGNAME, 'w').write("Seed {}".format(seed) + '\n')
    print "Using seed {}".format(seed)

def log(st):
    open(LOGNAME, 'a').write(str(st) + '\n')

startlog()

os.chdir(GAMEDIR)

output = subprocess.check_output(['git', 'reset', '--hard', 'master'], stderr=subprocess.STDOUT)
if os.path.exists('pokered.gbc'):
    os.remove('pokered.gbc')
print "Git repository has been reset"

####### MAKE THE RANDOMIZER EDITS HERE
def randomize_pokemon_constants():
    print "Randomizing Pokemon Constants"
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
    print "Pokemon Constants Randomized"

def parseArguments():
    #TODO Add YAML Support as alternatives to command line
    # Commands need to be done the same way, just the parse is different
    # Also this should be unit tested for the different possible cases
    args = list(sys.argv)
    args.pop(0)
    current_arg = None
    randomizer_args = {}
    while len(args) > 0:
        curr = args.pop(0)
        print "Current Arg: {}, curr: {}".format(current_arg, curr)
        if current_arg == None:
            current_arg = curr
        else:
            if current_arg in ["-s", "-seed"]:
                random.seed(curr)
            elif len(current_arg) > 0 and current_arg[0] == '-':
                randomizer_args[current_arg[1:]] = curr
            else:
                randomizer_args[current_arg] = True
            current_arg = None
    if current_arg:
        randomizer_args[current_arg] = True 
    return randomizer_args

args = parseArguments()
print args
if "reorder-pokedex" in args:
    randomize_pokemon_constants()

output = subprocess.check_output(['make', 'red'], stderr=subprocess.STDOUT)
log(output)
print "Pokemon Red Assembled"

shutil.copyfile('pokered.gbc', '../pokered.gbc')
print "Pokemon Red Copied"