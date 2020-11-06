import copy
import math
from sympy.utilities.iterables import multiset_permutations
import time


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


class Grid:
    """
    This class creates objects which are representations of the board. There
    different boards generated each with different placements of the blocks.
    """

    def __init__(self, board, blocks, laser, points):
        """
        This function initializes and object

        *** Parameters ***
            self:
                variable that holds all the data regarding the class object
            board:
                n*m matrix consisting of some or all of o, x, A, B and C
            blocks:
                list containing the number of movable blocks of each type
            laser:
                list of lists of all lasers consisting of origins and direction
                for example [[(1,3),(-1,-1)],[(2,4), (1,-1)]]  denotes 2 lasers
                [[origin, direction], [origin, direction]]
            points:
                list of hole points that the laser has to intersect
        *** Returns ***
            none
        """
        self.board = board
        self.A = blocks[0]  # A blocks
        self.B = blocks[1]  # B blocks
        self.C = blocks[2]  # C blocks
        self.L = laser
        self.H = points
        length = 2 * len(self.board) + 1
        width = 2 * len(self.board[0]) + 1
        grid = []
        for i in range(length):
            grid.append([])
            for j in range(width):
                grid[i].append('x')
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                grid[2 * i + 1][2 * j + 1] = self.board[i][j]
        self.grid = grid

    def blocks(self, filename):
        """
        This function generates all the possible boards by permuting the list
        of all movable blocks like o's, A's, B's, and C's. Each generated board
        is converted into a grid and then checked with "laser_path" and if the
        generated board is the solution, the iterations performed are printed.

        ** Parameters **
            self - consists of all data (board, blocks, laser, points)

        ** Returns **
            None
        """
        movable_blocks = []
        for x in self.board:
            for y in x:
                if y == 'o':
                    movable_blocks.append(y)

        for i in range(self.A):
            movable_blocks[i] = 'A'
        for i in range(self.A, (self.A + self.B)):
            movable_blocks[i] = 'B'
        for i in range((self.A + self.B), (self.A + self.B + self.C)):
            movable_blocks[i] = 'C'
        ITER_B = 0
        print("Generating possible Boards.......", end="\r")
        t1 = time.time()
        permutations = list(multiset_permutations(movable_blocks))
        t2 = time.time()
        print("Maximum possible iteration possible : ", len(permutations))
        print("Time for generating possible Boards: ", t2 - t1)
        x = 0
        print("Solving...", end="\r")
        t1 = time.time()
        for p in permutations:
            holes = copy.deepcopy(self.H)
            actual_board = copy.deepcopy(self.grid)
            possible_grid = create_grid(actual_board, p)
            ITER_B += 1
            Result, lasers_stack = laser_path(possible_grid, self.L, holes)
            if Result:
                print("Board solved")
                final_board = []
                length = int((len(possible_grid) - 1) / 2)
                width = int((len(possible_grid[0]) - 1) / 2)
                for i in range(length):
                    final_board.append([])
                    for j in range(width):
                        final_board[i].append(possible_grid[2 * i + 1][2 * j + 1])
                        print(possible_grid[2 * i + 1][2 * j + 1], end=' ')
                    print()
                print("This is the solution grid! Can also check the text file created.")
                ###
                new_name_1 = filename.split(".bff")[0]
                new_name_2 = new_name_1 + "_solution.txt"
                f = open(new_name_2, "w+")
                f.write("The solution to board is: \n")
                for i in range(length):
                    for j in range(width):
                        f.write(possible_grid[2 * i + 1][2 * j + 1])
                        f.write(" ")
                    f.write("\n")
                f.write("A is the reflect block, B is the opaque block and C is the refract block.")
                f.write("The o should be empty.")
                f.close()
                break
            t2 = time.time()
            if t2 - t1 >= 5:
                t1 = time.time()
                b = "Solving" + "..." * x
                print(b, end="\r")
                if x == 3:
                    x = 0
                x += 1
        print("Iterations til solved: ", ITER_B)


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


def next_laser_direction(grid, position, direction):
    """
    This function calculates the laser's new direction depending on its
    position and the type of the block it comes across;

    *** Parameters ***
        grid:
            List of lists representing the board
        position:
            Current position of the laser (array)
        direction:
            Current direction of the laser (array)

    *** Returns ***
        new_direction:
            New direction the laser is taking depending on the type of
            block it hits and its original position
    """
    x = position[0]
    y = position[1]
    if y % 2 == 0:
        """
        If y is even, the block is above or below
        """
        if grid[y + direction[1]][x].lower() == 'o' or grid[y + direction[1]][x].lower() == 'x':
            new_direction = direction
        elif grid[y + direction[1]][x].lower() == 'A':
            new_direction = [direction[0], -1 * direction[1]]
        elif grid[y + direction[1]][x].lower() == 'B':
            new_direction = []
        elif grid[y + direction[1]][x].lower() == 'C':
            d_1 = direction
            d_2 = [direction[0], -1 * direction[1]]
            new_direction = [d_1[0], d_1[1], d_2[0], d_2[1]]
    else:
        """
        If y is odd, the block is left or right
        """
        if grid[y][x + direction[0]].lower() == 'o' or grid[y][x + direction[0]].lower() == 'x':
            new_direction = direction
        elif grid[y][x + direction[0]].lower() == 'A':
            new_direction = [-1 * direction[0], direction[1]]
        elif grid[y][x + direction[0]].lower() == 'B':
            new_direction = []
        elif grid[y][x + direction[0]].lower() == 'C':
            d_1 = direction
            d_2 = [-1 * direction[0], direction[1]]
            new_direction = [d_1[0], d_1[1], d_2[0], d_2[1]]
    return new_direction


def boundary_check(grid, position, direction):
    """
    This function checks whether the current and next laser position is within
    the grid's boundary. If it is, we can continue with that particular laser.

    ** Parameters **
        grid:
            List of lists representing the board
        pos:
            Current position of the laser (array)
        direc:
            Current direction of the laser (array)

    ** Returns **
        Boolean:
            True if laser position is in boundary, false if otherwise
    """
    x = position[0]
    y = position[1]
    y_max = len(grid) - 1
    x_max = len(grid[0]) - 1
    if x < 0 or x > x_max or y < 0 or y > y_max or (x + direction[0]) < 0 or (x + direction[0]) > x_max or \
            (y + direction[1]) < 0 or (y + direction[1]) > y_max:
        return True
    else:
        return False


def create_grid(grid, p):
    """
    Creates a grid as explained in the top section for the given board
    Ex) If the board is - o A   then the grid is - x x x x x
                          B o                      x o x A x
                                                   x x x x x
                                                   x B x o x
                                                   x x x x x

    *** Parameters ***
        grid:
            List of lists representing the board
        p:
            List of permutations

    *** Returns ***
        grid:
            a (2n + 1) x (2m +1) matrix if board size is n x m
    """
    value = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 'o':
                grid[i][j] = p[value]
                value += 1
    return grid


def laser_path(grid, lasers, holes):
    """
    This function returns the main path the laser goes through for a given
    board.
    The variable "lasers_stack: consists of the laser path for all lasers
    available. Each step the laser takes is appended to this stack. If a
    step the laser takes reaches a hole, the hole is then removed from
    the "holes" list. If the "holes" list is empty, the while loops breaks
    and returns True. If not, the loop continues until the maximum iterations
    are reached.

    *** Parameters ***
        grid:
            List of lists consisting of the board on which the laser moves
        lasers:
            Array consisting of the origin and direction of each laser
        holes:
            Array consisting of all the hole points

    ***Returns***
        lasers_stack:
            List of lists of coordinates the laser took to reach the hole
    """

    # List of all lasers and and each laser list has its path
    lasers_stack = []
    for i in range(len(lasers)):
        lasers_stack.append([lasers[i]])
    iterations = 0
    max_iter = 100
    while len(holes) != 0 and iterations <= max_iter:
        iterations += 1
        for i in range(len(lasers_stack)):
            laser_position = list(lasers_stack[i][-1][0])
            direction = list(lasers_stack[i][-1][1])
            if boundary_check(grid, laser_position, direction):
                continue
            else:
                new_direction = next_laser_direction(grid, laser_position, direction)
                if len(new_direction) == 0:
                    lasers_stack[i].append([laser_position, direction])
                elif len(new_direction) == 2:
                    direction = new_direction
                    laser_position = [laser_position[0] + direction[0], laser_position[1] + direction[1]]
                    lasers_stack[i].append([laser_position, direction])
                else:
                    direction = new_direction
                    laser_position_1 = [laser_position[0] + direction[0], laser_position[1] + direction[1]]
                    laser_position_2 = [laser_position[0] + direction[2], laser_position[1] + direction[3]]
                    lasers_stack.append([[laser_position_1, [direction[0], direction[1]]]])
                    lasers_stack[i].append([laser_position_2, [direction[2], direction[3]]])
                    laser_position = laser_position_2
            if laser_position in holes:
                holes.remove(laser_position)
    if len(holes) == 0:
        return True, lasers_stack
    else:
        return False, lasers_stack


if __name__ == '__main__':
    # Puzzle, Positions, Lasers, Movable_blocks, Targets = load_file('mad_1.bff')
    # solution = solve_recursively(Positions, Movable_blocks, Puzzle, Lasers, Targets, len(Movable_blocks))

    filename = "dark_1.bff"
    board_given, empty, blocks, laser, points = load_file(filename)
    time_start = time.time()
    Board = Grid(board_given, blocks, laser, points)
    Board.blocks(filename)
    time_end = time.time()
    print('Run time: %f seconds' % (time_end - time_start))
