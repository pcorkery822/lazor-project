import copy


class Blocks:

    def __init__(self, type):
        self.type = type

    def interact(self, other, position):
        if position[0] % 2 == 1:
            axis = 4
        elif position[1] % 2 == 1:
            axis = 3
 
        if self.type == 'reflect':
            other[axis] = -other[axis]
        elif self.type == 'refract':
            new = copy.deepcopy(other)
            other[axis] = -other[axis]
            other.append(new)
        elif self.type == 'opaque':
            other[3] = 0
            other[4] = 0


def load_file(fptr):
    '''
    :param fptr: Input file that contains grid, laser positions, number of movable blocks and their types, and target
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
    refract = []
    reflect = []
    opaque = []
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
                    reflect.append(1)
            elif line[0] == 'B' and not start:
                num = int(line[1:])
                for i in range(num):
                    refract.append(1)
            elif line[0] == 'C' and not start:
                num = int(line[1:])
                for i in range(num):
                    opaque.append(1)
            # Read laser positions and directions from file
            elif line[0] == 'L':
                line = line[1:]
                laser.append([int(i) for i in line.split()])
            # Read target positions from file
            elif line[0] == 'P':
                line = line[1:]
                points.append([int(i) for i in line.split()])

    blocks = [reflect, refract, opaque]

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
                full_grid[2 * y + 1][2 * z + 1] = 'Unavailable'
            elif ind == 'o':
                full_grid[2 * y + 1][2 * z + 1] = 'Open'
                empty.append([2 * y + 1, 2 * z + 1])
            elif ind == 'A':
                full_grid[2 * y + 1][2 * z + 1] = 'Reflect'
            elif ind == 'B':
                full_grid[2 * y + 1][2 * z + 1] = 'Opaque'
            elif ind == 'C':
                full_grid[2 * y + 1][2 * z + 1] = 'Refract'

    bff_file.close()
    return full_grid, empty, laser, blocks, points


def solve_puzzle(grid, empty, laser, blocks, points):

    for i, j in enumerate(empty):
        grid_new = grid





if __name__ == '__main__':
    puzzle, positions, lasers, movable_blocks, targets = load_file('dark_1.bff')
    solution = solve_puzzle(puzzle, positions, lasers, movable_blocks, targets)

