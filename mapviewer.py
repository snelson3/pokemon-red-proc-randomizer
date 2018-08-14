import os
import pygame
import pygame.locals
GAMEDIR = 'pokered'
CLEAR = ' '
SOLID = '0'
SCALE_AMT = 2
COLLISION_OVERLAY = True

# I'm passing around arguments more than I think I should be
pygame.init()

def flatten_table(table):
    import functools
    return functools.reduce(lambda x,y:x+y, table)

def transpose_table(table):
    return list(map(list, zip(*table)))


def load_tileset(fn, flatten=True):
    image = pygame.image.load(fn).convert()
    i_width, i_height = image.get_size()
    tile_table = []
    for t_x in range(i_width//8):
        line = []
        tile_table.append(line)
        for t_y in range(0, i_height//8):
            rect = (t_x*8, t_y*8, 8, 8)
            line.append(image.subsurface(rect))
    tile_table = transpose_table(tile_table) # The tutorial I followed read the tiles rotated
    if flatten:
        return flatten_table(tile_table)
    return tile_table

class Tile():
    def __init__(self, index, collisions):
        self.index = index
        self.collides = index not in collisions

class SmallBlock():
    # 2x2 block of tiles, collision matters here
    def __init__(self, tiles, collisions):
        self.tiles = [Tile(t, collisions) for t in tiles]
    def getTile(self, row, col):
        return self.tiles[(2*row)+col]
    def printBlock(self):
        print("{} {}\n{} {}".format(*[i.index for i in self.tiles]))

class BigBlock():
    # 4x4 block of tiles
    def __init__(self, index, blockset, collisions):
        self.collisions = collisions
        self.blocklist = blockset[index]
        self.blocks = self.makeSmallBlocks()
    def makeSmallBlocks(self):
        # Probably a better math way to do this
        return [
            SmallBlock([self.blocklist[0], self.blocklist[1], self.blocklist[4], self.blocklist[5]], self.collisions),
            SmallBlock([self.blocklist[2], self.blocklist[3], self.blocklist[6], self.blocklist[7]], self.collisions),
            SmallBlock([self.blocklist[8], self.blocklist[9], self.blocklist[12], self.blocklist[13]], self.collisions),
            SmallBlock([self.blocklist[10], self.blocklist[11], self.blocklist[14], self.blocklist[15]], self.collisions),
        ]
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
    def printBlock(self):
        print("{} {} {} {}\n{} {} {} {}\n{} {} {} {}\n{} {} {} {}".format(*self.blocklist))

class Map():
    def __init__(self, mapname, width, tilesetname):
        self.mapname = mapname
        self.width = width
        self.tilesetname = tilesetname
        self.tileset = load_tileset(os.path.join(GAMEDIR, "gfx", "tilesets", tilesetname+'.png'))
        self.blockset = self.readBlockset()
        self.collisions = self.readTileColl()
        self.map = self.readMapLayout()
    def readMapLayout(self):
        with open(os.path.join(GAMEDIR, 'maps', self.mapname+'.blk'), "rb") as f:
            return [BigBlock(i, self.blockset, self.collisions) for i in f.read()]
    def readBlockset(self):
        with open(os.path.join(GAMEDIR, 'gfx', 'blocksets', self.tilesetname+'.bst'), "rb") as f:
            single_dim = [i for i in f.read()]
            return [single_dim[i*16:i*16+16] for i in range(len(single_dim)//16)]
    def readTileColl(self):
        with open(os.path.join(GAMEDIR, 'gfx', 'tilesets', self.tilesetname+'.tilecoll'), "rb") as f:
            return [i for i in f.read()]

# 18x20 is what I'm looking for
class MapViewer():
    def __init__(self):
        self.screen = pygame.display.set_mode((900, 900))
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
        big_blocks_per_row = m.width // 2 # The width is in 2x2 tiles and big blocks are groups of 4x4 tiles
        for i in range(len(m.map) // big_blocks_per_row):
            # i is the number of rows of big blocks
            for y in range(4):
                row = []
                # A big block has 4 rows
                start_index = (i*big_blocks_per_row)#+(y*(big_blocks_per_row))
                for block in m.map[start_index:start_index+big_blocks_per_row]:
                    for x in range(4):
                        # a big block has 4 columns
                        row.append(block.getTile(y,x))
                if len(row) < 1:
                    raise Exception("Empty Row! I don't think this should happen")
                translated_map.append(row)
        return translated_map
    def viewMap(self, m):
        tmap = self.breakDownTiles(m)
        for row in range(len(tmap)):
            for t in range(len(tmap[row])):
                tile = tmap[row][t]
                print(tile.index)
                surface = m.tileset[tile.index]
                scaled_size = 8*SCALE_AMT
                scaled_surface = pygame.transform.scale(surface,(scaled_size, scaled_size))

                if COLLISION_OVERLAY:
                    tile_color = (255, 0, 0, 0) if tile.collides else (0, 255, 0, 0)
                    # Color the surface
                    pxa = pygame.PixelArray(scaled_surface) 
                    for x in range(pxa.shape[0]):
                        for y in range(pxa.shape[1]):
                            old_color = scaled_surface.unmap_rgb(pxa[x,y])
                            blendColor = lambda x, y : (x + y) / 2
                            pxa[x,y] = (
                                blendColor(old_color[0], tile_color[0]),
                                blendColor(old_color[1], tile_color[1]),
                                blendColor(old_color[2], tile_color[2]),
                                blendColor(old_color[3], tile_color[3])
                            )
                    pxa.close()

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


    # tileset = load_tileset(os.path.join(GAMEDIR, "gfx", "tilesets", 'reds_house'+'.png'))
    # NUM_COLS = 16
    # for x in range(len(tileset) // NUM_COLS):
    #     for y, tile in enumerate(tileset[x*NUM_COLS:x*NUM_COLS+NUM_COLS]):
    #         viewer.screen.blit(pygame.transform.scale(tile, (8*SCALE_AMT, 8*SCALE_AMT)), (y*24, x*32))
    # pygame.display.flip()
    # while pygame.event.wait().type != pygame.locals.QUIT:
    #     pass

# http://qq.readthedocs.io/en/latest/tiles.html