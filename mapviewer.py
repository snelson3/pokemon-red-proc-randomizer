import os
GAMEDIR = 'pokered'

# I'm passing around arguments more than I think I should be

class Tile():
    def __init__(self, index, tileset):
        self.index = index
        self.tileset = tileset

class SmallBlock():
    # 2x2 block of tiles, collision matters here
    def __init__(self, tiles, collisions, tileset):
        self.tiles = [Tile(t, tileset) for t in tiles]
        self.collides = tiles[0] not in collisions

class BigBlock():
    # 4x4 block of tiles
    def __init__(self, index, blockset, collisions, tileset):
        self.tileset = tileset
        self.collisions = collisions
        self.blocklist = blockset[index]
        self.blocks = self.makeSmallBlocks()
    def makeSmallBlocks(self):
        return [SmallBlock(self.blocklist[i:i+4], self.collisions, self.tileset) for i in range(len(self.blocklist)//4)]

class Map():
    def __init__(self, mapname, width, tileset):
        self.mapname = mapname
        self.width = width
        self.tileset = tileset
        self.blockset = self.readBlockset()
        self.collisions = self.readTileColl()
        self.map = self.readMapLayout()
    def readMapLayout(self):
        with open(os.path.join(GAMEDIR, 'maps', self.mapname+'.blk'), "rb") as f:
            return [BigBlock(i, self.blockset, self.collisions, self.tileset) for i in f.read()]
    def readBlockset(self):
        with open(os.path.join(GAMEDIR, 'gfx', 'blocksets', self.tileset+'.bst'), "rb") as f:
            single_dim = [i for i in f.read()]
            return [single_dim[i:i+16] for i in range(len(single_dim)//16)]
    def readTileColl(self):
        with open(os.path.join(GAMEDIR, 'gfx', 'tilesets', self.tileset+'.tilecoll'), "rb") as f:
            return [i for i in f.read()]

# 18x20 is what I'm looking for
class MapViewer():
    def readMap(self, m):
        # Return a 2D array of the 2x2 blocks
        bigblocks = m.map
        rows = []
        top = True
        for rn in range(len(bigblocks) // (m.width // 2)):
            rows.append([])
            for i in range(m.width // 2):
                rows[-1].append(bigblocks[rn+i].blocks[0])
                rows[-1].append(bigblocks[rn+i].blocks[1])
            rows.append([])
            for i in range(m.width // 2):
                rows[-1].append(bigblocks[rn+i].blocks[2])
                rows[-1].append(bigblocks[rn+i].blocks[3])
        return rows
    def viewMap(self, fn, width):
        pass # Use Pygame to launch a window with the map
    def printCollisions(self, m):
        print ("{}x{}".format(len(self.readMap(m)), len(self.readMap(m)[0])))
        print('\n'.join([''.join([' ' if b.collides else 'X' for b in r]) for r in self.readMap(m)]))

if __name__ == '__main__':
    my_map = Map('pallettown', 10, 'overworld')
    viewer = MapViewer()
    viewer.printCollisions(my_map)