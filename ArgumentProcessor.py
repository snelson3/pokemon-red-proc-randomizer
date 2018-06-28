import sys

class ArgumentProcessor:
    def __init__(self):
        pass
    def parseCmd(self):
        # TODO Add YAML Support as alternatives to command line
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