import os
import pygame
import pygame.locals
GAMEDIR = 'pokered'
CLEAR = ' '
SOLID = '0'
SCALE_AMT = 2

# I'm passing around arguments more than I think I should be
pygame.init()

def flatten_table(table):
    import functools
    return functools.reduce(lambda x,y:x+y, table)

def load_tileset(fn):
    image = pygame.image.load(fn).convert()
    i_width, i_height = image.get_size()
    tile_table = []
    for t_x in range(i_width//8):
        line = []
        tile_table.append(line)
        for t_y in range(0, i_height//8):
            rect = (t_x*8, t_y*8, 8, 8)
            line.append(image.subsurface(rect))
    return flatten_table(tile_table)

class Tile():
    def __init__(self, index, tileset, collisions):
        self.index = index
        self.surface = tileset[index] # This shouldn't be here, it should just key off the indexx
        self.tileset = tileset
        self.collides = index not in collisions
    def loadTileset(self):
        fn = ''

class SmallBlock():
    # 2x2 block of tiles, collision matters here
    def __init__(self, tiles, collisions, tileset):
        self.tiles = [Tile(t, tileset, collisions) for t in tiles]
    def getTile(self, row, col):
        return self.tiles[((row-1)*2)+col]

class BigBlock():
    # 4x4 block of tiles
    def __init__(self, index, blockset, collisions, tileset):
        self.tileset = tileset
        self.collisions = collisions
        self.blocklist = blockset[index]
        self.blocks = self.makeSmallBlocks()
    def makeSmallBlocks(self):
        return [SmallBlock(self.blocklist[i:i+4], self.collisions, self.tileset) for i in range(len(self.blocklist)//4)]
    def getTile(self, row, col):
        # 00 01 10 11 (first block)
        # 02 03 12 13 (second block)
        # 20 21 30 31 (third block)
        # 22 23 32 33 (fourth block)
        if row < 2:
            if col < 2:
                return self.blocks[0].getTile(row, col)
            return self.blocks[1].getTile(row, col-2)
        if col < 2:
            return self.blocks[2].getTile(row-2, col)
        return self.blocks[3].getTile(row-2, col-2)

class Map():
    def __init__(self, mapname, width, tilesetname):
        self.mapname = mapname
        self.width = width
        self.tilesetname = tilesetname
        self.tileset = load_tileset(os.path.join(GAMEDIR, "gfx", "tilesets", tilesetname+'.png'))
        assert len(self.tileset) >= 60
        self.blockset = self.readBlockset()
        self.collisions = self.readTileColl()
        self.map = self.readMapLayout()
    def readMapLayout(self):
        with open(os.path.join(GAMEDIR, 'maps', self.mapname+'.blk'), "rb") as f:
            return [BigBlock(i, self.blockset, self.collisions, self.tileset) for i in f.read()]
    def readBlockset(self):
        with open(os.path.join(GAMEDIR, 'gfx', 'blocksets', self.tilesetname+'.bst'), "rb") as f:
            single_dim = [i for i in f.read()]
            return [single_dim[i:i+16] for i in range(len(single_dim)//16)]
    def readTileColl(self):
        with open(os.path.join(GAMEDIR, 'gfx', 'tilesets', self.tilesetname+'.tilecoll'), "rb") as f:
            return [i for i in f.read()]

# 18x20 is what I'm looking for
class MapViewer():
    def __init__(self):
        self.screen = pygame.display.set_mode((500, 500))
        self.screen.fill((255, 255, 255))
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
    def breakDownTiles(self, m):
        # Turn a 1D array of Big Blocks into a 2D array of Tiles
        translated_map = []
        big_blocks_per_row = m.width // 4
        for i in range(len(m.map) // big_blocks_per_row):
            # i is the number of rows of big blocks
            for y in range(4):
                row = []
                # A big block has 4 rows
                start_index = (i*big_blocks_per_row)*(y*(big_blocks_per_row))
                for block in m.map[start_index:start_index+big_blocks_per_row]:
                    for x in range(4):
                        # a big block has 4 columns
                        row.append(block.getTile(y,x))
                translated_map.append(row)
        return translated_map
    def viewMap(self, m):
        tmap = self.breakDownTiles(m)
        for row in range(len(tmap)):
            for t in range(len(tmap[row])):
                tile = tmap[row][t]
                scaled_size = 8*SCALE_AMT
                scaled_surface = pygame.transform.scale(tile.surface,(scaled_size, scaled_size))
                self.screen.blit(scaled_surface, (scaled_size*t, scaled_size*row))
        pygame.display.flip()
        while pygame.event.wait().type != pygame.locals.QUIT:
            pass
    def printCollisions(self, m):
        print ("{}x{}".format(len(self.readMap(m)), len(self.readMap(m)[0])))
        print('\n'.join([''.join([SOLID if b.collides else CLEAR for b in r]) for r in self.readMap(m)]))

if __name__ == '__main__':
    viewer = MapViewer()

    my_map = Map('pallettown', 20, 'overworld')
    viewer.viewMap(my_map)

    # tileset = load_tileset(os.path.join(GAMEDIR, "gfx", "tilesets", 'overworld'+'.png'))
    # NUM_ROWS = 8
    # for x in range(len(tileset) // NUM_ROWS):
    #     for y, tile in enumerate(tileset[x*NUM_ROWS:x*NUM_ROWS+NUM_ROWS]):
    #         print((x*32, y*24))
    #         viewer.screen.blit(pygame.transform.scale(tile, (8*SCALE_AMT, 8*SCALE_AMT)), (x*32, y*24))
    # pygame.display.flip()
    # while pygame.event.wait().type != pygame.locals.QUIT:
    #     pass

# http://qq.readthedocs.io/en/latest/tiles.html