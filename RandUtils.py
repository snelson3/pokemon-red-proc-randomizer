import shutil
class RandUtils:
    def __init__(self):
        pass
    def replaceFile(self, new, old):
        shutil.copy(new,old)
    def replaceLine(self, fn, ln, st):
        content = open(fn, "r").read().split("\n")
        assert ln <= len(content)
        with open(fn, "w") as f:
            for l in range(ln-1):
                f.write(content.pop(0))
                if len(content) > 0:
                    f.write("\n")
            f.write(st+"\n")
            content.pop(0)
            while len(content) > 0:
                f.write(content.pop(0))
                if len(content) > 0:
                    f.write("\n")
    def addLine(self, fn, ln, st):
        content = open(fn, "r").read().split("\n")
        assert ln <= len(content)
        with open(fn, "w") as f:
            for l in range(ln-1):
                f.write(content.pop(0))
                if len(content) > 0:
                    f.write("\n")
            f.write(st+"\n")
            while len(content) > 0:
                f.write(content.pop(0))
                if len(content) > 0:
                    f.write("\n")