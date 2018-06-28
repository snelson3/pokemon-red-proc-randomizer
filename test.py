class A():
    def __init__(self):
        pass
    def hi(self):
        print "hi"


class B(A):
    def __init__(self, s=None):
        if s:
            self.s = s
        else:
            self.s = 3

class C(B):
    def __init__(self, s=None):
        B.__init__(self, s)
    def getS(self):
        print self.s

x = C()
x.hi()
x.getS()
y = C(2)
y.getS()

# hi
# 3
# 2