import os, subprocess, shutil, time, random, sys
from Logger import Logger
from ArgumentProcessor import ArgumentProcessor

class Randomizer(ArgumentProcessor):
    def __init__(self):
        ArgumentProcessor.__init__(self)
        self.logname = 'recent.log'
        self.gamedir = ''
        self.seed = int(time.time())
        self.setArguments()
        self.log = Logger(os.path.abspath('./recent.log'), self.seed)
    def resetSeed(self):
        random.seed(self.seed)
    def resetGit(self, files_to_remove=[], branch='master'):
        assert os.path.isdir(".git")
        output = subprocess.check_output(['git', 'reset', '--hard', branch])
        self.log.log(output)
        for fn in files_to_remove:
            if os.path.exists(fn):
                os.remove(fn)
        self.log.output("Git repository has been reset")
    def setArguments(self):
        self.args = self.parseCmd()
        if 'f' in self.args:
            self.args = self.parseYml(self.args['f'])
        if 'seed' in self.args:
            self.seed = str(self.args['seed'])
            del self.args["seed"]
            self.resetSeed()
    def prepare(self):
        os.chdir(self.gamedir)
        pass # Filled in by inheriting child, function that gets the environment ready for editing
    def process(self):
        self.resetSeed()
        pass # Filled in by inheriting child, function that calls the right randomization functions
    def create(self):
        pass # Filled in by inheriting child, function that finalizes the edits