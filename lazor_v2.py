import copy
import math


class Blocks:

    # Initialize Class and Type of Blocks
    def __init__(self, bk_type):
        self.type = bk_type

    # Determine interaction between block and laser
    def interact(self, v, p):
        new_las = []
        # If the x coordinate is odd, then we will have a change in the x velocity
        if p[0] % 2 == 1:
            v_ind = 0
        # If the y coordinate is odd, then we will have a change in the y velocity
        elif p[1] % 2 == 1:
            v_ind = 1

        # Determine change in velocity based on the type of block
        if self.type == 'Reflect':
            v[v_ind] = -v[v_ind]
        elif self.type == 'Refract':
            # Split laser by making a copy and having an additional part deflect
            new_las = copy.deepcopy(v)
            v[v_ind] = -v[v_ind]
        elif self.type == 'Opaque':
            v[0] = 0
            v[1] = 0

        return v, new_las


def load_file(fptr):
    '''
    :param:
    fptr: Input file that contains grid, laser positions, number of movable blocks and their types, and target
    positions for beams
    :return:
    grid: list of lists showing grid layout, including spaces with blocks allowed, spaces without blocks allowed, and
    fixed blocks
    blocks: list containing the number of movable blocks of each type
    laser: list of lists containing laser positions and directions
    points: list of lists containing the coordinates of each target position for the beam
    '''

    bff_file = open(fptr, 'r')

    # Initialize list for grid and boolean for reading grid
    grid = []
    start = False
    # Initialize list of movable blocks
    blocks = []
    # Initialize list for laser positions and directions
    laser = []
    # Initialize list for target points
    points = []

    for line in bff_file:
        line = line.rstrip()
        # Read grid from file
        if start and not 'GRID STOP' == line:
            grid.append(line.split())
        elif 'GRID START' == line:
            start = True
        elif 'GRID STOP' == line:
            start = False
        if len(line) > 0:
            # Read movable blocks from file
            if line[0] == 'A' and not start:
                num = int(line[1:])
                for i in range(num):
                    blocks.append('Reflect')
            elif line[0] == 'B' and not start:
                num = int(line[1:])
                for i in range(num):
                    blocks.append('Refract')
            elif line[0] == 'C' and not start:
                num = int(line[1:])
                for i in range(num):
                    blocks.append('Opaque')
            # Read laser positions and directions from file
            elif line[0] == 'L':
                line = line[1:]
                laser.append([int(i) for i in line.split()])
            # Read target positions from file
            elif line[0] == 'P':
                line = line[1:]
                points.append([int(i) for i in line.split()])

    # Convert x's, o's, and fixed blocks to numbers in grid
    # x = 0, o = 1, A = 2, B = 3, C = 4
    # Initialize new grid with 2n+1 x 2n+1 indices where original grid was n x n
    full_grid = []
    for y, line in enumerate(grid):
        row = []
        zeros = []
        for z in range(2 * len(line) + 1):
            row.append(0)
            zeros.append(0)
        if y == 0:
            full_grid.append(zeros)
        full_grid.append(row)
        full_grid.append(zeros)

    # Initialize list to store potential positions for movable blocks
    empty = []
    for y, line in enumerate(grid):
        for z, ind in enumerate(line):
            if ind == 'x':
                full_grid[2 * y + 1][2 * z + 1] = 0
            elif ind == 'o':
                full_grid[2 * y + 1][2 * z + 1] = 0
                empty.append([2 * y + 1, 2 * z + 1])
            elif ind == 'A':
                full_grid[2 * y + 1][2 * z + 1] = 'Reflect'
            elif ind == 'B':
                full_grid[2 * y + 1][2 * z + 1] = 'Opaque'
            elif ind == 'C':
                full_grid[2 * y + 1][2 * z + 1] = 'Refract'

    # Set values of grid on edges of blocks
    for r, line in enumerate(grid):
        for i in range(len(line)):
            if full_grid[r][i] != 0:
                for j in range(-1, 3, 2):
                    full_grid[r][i + j] = grid[r][i]
                    full_grid[r + j][i] = grid[r][i]

    bff_file.close()
    return full_grid, empty, laser, blocks, points


def solve_recursively(empty, blocks, grid, laser, points, n, blk_pos=[], blk_type=[], j=0):

    '''
    :param:
    empty: list of lists containing x,y coordinates of available spaces to put blocks
    blocks: list containing all movable blocks
    grid: list of lists showing grid layout without movable blocks (empty spaces and fixed blocks)
    laser: list of lists containing positions and directions of each laser
    points: list of lists containing the coordinates of each target position for the beam
    n: iteration variable that keeps track of how many blocks have yet to be placed for a given guess at a solution
    blk_pos: list of lists containing positions of blocks for a given guess at a solution
    blk_type: list containing types of blocks at the corresponding index of blk_pos
    j: iteration variable that keeps track of the number of solutions that have been tried
    '''

    # Recursive for loop to pass through possible positions for each block
    while n >= 1:
        for i in range(j, len(empty)):
            if j == 0:
                blk_pos.append(empty[len(blocks) - n + i])
                blk_type.append(blocks[len(blocks) - n])
            else:
                blk_pos[k] = empty(j)
            n -= 1
            k += 1
            solve_recursively(empty, blocks, grid, laser, points, n, blk_pos, blk_type, j, k)
        if n == 0:
            if is_solution(blk_pos, blk_type, grid, laser, points):
                return blk_pos, blk_type
            blk_pos = []
            blk_type = []
            n = len(blocks)
            j += 1
            k = 0

    # If no solution found, try different order of blocks - valid if there are different types of blocks
    blocks[0] = blocks.pop()


def is_solution(block_positions, block_types, grid, laser, points):

    # Set values of grid
    for i in range(len(block_positions)):
        y = block_positions[i][0]
        x = block_positions[i][1]
        grid[x][y] = block_types[i]
        for j in range(-1, 3, 2):
            grid[x + j][y] = block_types[i]
            grid[x][y + j] = block_types[i]

    # Determine Path of Lasers
    path = []
    for i in range(len(laser)):
        x = laser[i][0]
        y = laser[i][1]
        vx = laser[i][2]
        vy = laser[i][3]
        pos = [x, y]
        path.append(pos)
        while 0 <= x <= len(grid) - 1 and 0 <= y <= len(grid[0]) - 1:
            if grid[y][x] != 0:
                blk = Blocks(grid[y][x])
                v, new = blk.interact([vx, vy], [x, y])
                if len(new) != 0:
                    laser.append([new[0], new[1], x, y])
            x += vx
            y += vy
            path.append([x, y])

    for i, j in enumerate(points):
        if j not in path:
            return False
        return True


if __name__ == '__main__':
    Puzzle, Positions, Lasers, Movable_blocks, Targets = load_file('mad_1.bff')
    solution = solve_recursively(Positions, Movable_blocks, Puzzle, Lasers, Targets, len(Movable_blocks))

