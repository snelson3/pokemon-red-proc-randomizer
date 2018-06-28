class Logger:
    def __init__(self, fn, seed):
        self.fn = fn
        open(self.fn, 'w').write("Seed {}".format(seed) + '\n')
        self.output( "Using seed {}".format(seed) )
    def log(self, st):
        open(self.fn, 'a').write(str(st) + '\n')
    def output(self, st):
        print st
        self.log(st)