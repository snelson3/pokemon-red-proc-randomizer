import sys, json

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

if __name__ == '__main__':
    print ArgumentProcessor().parseCmd()