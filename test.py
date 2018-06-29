import sys

def a():
    print( sys.argv )

sys.argv = ['test.py', 'sup']

a()