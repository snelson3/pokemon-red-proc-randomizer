import shutil
class RandUtils:
    def __init__(self):
        pass
    def replaceFile(self, new, old):
        shutil.copy(new,old)
    def replaceLine(self, fn, ln, st):
        content = []
        with open(fn) as f:
            for line in f:
                content.append(line)
        content[ln-1] = st + "\n"
        with open(fn, "w") as f:
            for line in content:
                f.write(line)
    def addLine(self, fn, ln, st):
        content = []
        with open(fn) as f:
            for line in f:
                content.append(line)
        content = content[:ln-1] + [st+"\n"] + content[ln-1:]
        with open(fn, "w") as f:
            for line in content:
                f.write(line)