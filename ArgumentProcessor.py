import sys, json, os

class ArgumentProcessor:
    def __init__(self):
        pass
    def parseCmd(self):
        # TODO Add YAML Support as alternatives to command line
        args = list(sys.argv)
        args.pop(0)
        current_arg = None
        randomizer_args = {}
        while len(args) > 0:
            curr = args.pop(0)
            if curr[0] == '-':
                assert len(args) > 0, "no value for argument!"
                val = args.pop(0)
                curr_name = curr[1:]
                if val[0] in ['[', '{']:
                    # We are assuming the string is valid json
                    randomizer_args[curr_name] = json.loads(val)
                else:
                    randomizer_args[curr_name] = val
            else:
                randomizer_args[curr] = True
        return randomizer_args
    def parseYml(self, fn):
        assert os.path.isfile(fn), "File not found!"
        from yaml import load
        from yaml import CLoader as Loader
        return load(open(fn, "r"), Loader=Loader) # TODO This is not safe?, use loads

if __name__ == '__main__':
    print(ArgumentProcessor().parseCmd())