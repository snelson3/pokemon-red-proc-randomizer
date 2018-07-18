DEBUG=True

class Logger:
    def __init__(self, fn, seed):
        self.fn = fn
        f = open(self.fn, 'w')
        f.write("Seed {}".format(seed) + '\n')
        f.close()
        self.output( "Using seed {}".format(seed) )
    def log(self, st):
        f = open(self.fn, 'a')
        f.write(str(st) + '\n')
        f.close()
    def output(self, st):
        print( st )
        self.log(st)
    def debug(self, st):
        if DEBUG:
            print( st )
        self.log(st)