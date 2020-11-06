import copy
import math
from sympy.utilities.iterables import multiset_permutations
import time


class Grid:
    """
    This class creates objects which are representations of the board. There
    different boards generated each with different placements of the blocks.
    """

    def __init__(self, board, laser, blocks, points, empty):
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
        self.E = empty  # Empty positions
        length = len(self.board)
        width = len(self.board[0])
        grid = []
        for i in range(length):
            grid.append([])
            for j in range(width):
                grid[i].append('x')
        for i in range((len(self.board) - 1) // 2):
            for j in range((len(self.board[0]) - 1) // 2):
                grid[2 * i + 1][2 * j + 1] = self.board[2 * i + 1][2 * j + 1]
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

        for i in range(len(self.A)):
            movable_blocks.append('A')
        for i in range(len(self.A), (len(self.A) + len(self.B))):
            movable_blocks.append('B')
        for i in range((len(self.A) + len(self.B)), (len(self.A) + len(self.B) + len(self.C))):
            movable_blocks.append('C')

        # Make list for Permutations Consisting of Empty Spaces
        p_list = []
        for i, j in enumerate(empty):
            p_list.append('o')

        for i, j in enumerate(movable_blocks):
            p_list[i] = movable_blocks[i]

        ITER_B = 0
        print("Generating possible Boards.......", end="\r")
        t1 = time.time()
        permutations = list(multiset_permutations(p_list))
        t2 = time.time()
        print("Maximum possible iteration possible : ", len(permutations))
        print("Time for generating possible Boards: ", t2 - t1)
        x = 0
        print("Solving...", end="\r")
        t1 = time.time()
        for q, p in enumerate(permutations):
            holes = copy.deepcopy(self.H)
            actual_board = copy.deepcopy(self.grid)
            if q == 785:
                continue
            possible_grid = create_grid(actual_board, p, empty)
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
    # Initialize lists of movable blocks of types a, b, and c
    a = []
    b = []
    c = []
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
                    a.append('A')
            elif line[0] == 'B' and not start:
                num = int(line[1:])
                for i in range(num):
                    b.append('B')
            elif line[0] == 'C' and not start:
                num = int(line[1:])
                for i in range(num):
                    c.append('C')
            # Read laser positions and directions from file
            elif line[0] == 'L':
                line = line[1:]
                laser.append([int(i) for i in line.split()])
            # Read target positions from file
            elif line[0] == 'P':
                line = line[1:]
                points.append([int(i) for i in line.split()])

    # Combine lists of different block types
    blocks = [a, b, c]

    # Convert x's, o's, and fixed blocks to numbers in grid
    # x = 0, o = 1, A = 2, B = 3, C = 4
    # Initialize new grid with 2n+1 x 2n+1 indices where original grid was n x n
    full_grid = []
    for y, line in enumerate(grid):
        row = []
        zeros = []
        for z in range(2 * len(line) + 1):
            row.append('o')
            zeros.append('x')
        if y == 0:
            full_grid.append(zeros)
        full_grid.append(row)
        full_grid.append(zeros)

    # Initialize list to store potential positions for movable blocks
    empty = []
    for y, line in enumerate(grid):
        for z, ind in enumerate(line):
            if ind == 'x':
                full_grid[2 * y + 1][2 * z + 1] = 'o'
            elif ind == 'o':
                full_grid[2 * y + 1][2 * z + 1] = 'o'
                empty.append([2 * y + 1, 2 * z + 1])
            elif ind == 'A':
                full_grid[2 * y + 1][2 * z + 1] = 'A'
            elif ind == 'B':
                full_grid[2 * y + 1][2 * z + 1] = 'B'
            elif ind == 'C':
                full_grid[2 * y + 1][2 * z + 1] = 'C'

    bff_file.close()
    return full_grid, empty, laser, blocks, points


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
        if grid[y + direction[1]][x] == 'o' or grid[y + direction[1]][x] == 'x':
            new_direction = direction
        elif grid[y + direction[1]][x] == 'A':
            new_direction = [direction[0], -1 * direction[1]]
        elif grid[y + direction[1]][x] == 'B':
            new_direction = []
        elif grid[y + direction[1]][x] == 'C':
            d_1 = [direction[0], -1 * direction[1]]
            d_2 = direction
            new_direction = [d_1[0], d_1[1], d_2[0], d_2[1]]
    else:
        """
        If y is odd, the block is left or right
        """
        if grid[y][x + direction[0]] == 'o' or grid[y][x + direction[0]] == 'x':
            new_direction = direction
        elif grid[y][x + direction[0]] == 'A':
            new_direction = [-1 * direction[0], direction[1]]
        elif grid[y][x + direction[0]] == 'B':
            new_direction = []
        elif grid[y][x + direction[0]] == 'C':
            d_1 = [-1 * direction[0], direction[1]]
            d_2 = direction
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
    if 0 <= x <= x_max and 0 <= y <= y_max and 0 <= x + direction[0] <= x_max and 0 <= y + direction[1] <= y_max:
        return True
    else:
        return False


def create_grid(grid, p, empty):
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
    for i in range(len(p)):
        if p[i] != 'x':
            grid[empty[i][0]][empty[i][1]] = p[i]

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
        lasers_stack.append(lasers[i])
        iterations = 0
    max_iter = 100

    while len(holes) != 0:
        iterations += 1
        previous_lasers = []
        las = [lasers_stack[i]]
        if las in previous_lasers:
            return False, lasers_stack
        for i in range(len(lasers_stack)):
            laser_position = [lasers_stack[i][0], lasers_stack[i][1]]
            direction = [lasers_stack[i][2], lasers_stack[i][3]]
            while boundary_check(grid, laser_position, direction):
                las = [laser_position[0], laser_position[1], direction[0], direction[1]]
                new_direction = next_laser_direction(grid, laser_position, [direction[0], direction[1]])
                if iterations >= max_iter:
                    return False, lasers_stack
                # If lazer hits opaque block, go to next lazer in stack
                if not new_direction:
                    break
                # If lazer hits empty space or reflect block, change position
                elif len(new_direction) == 2:
                    direction = new_direction
                    laser_position = [laser_position[0] + direction[0], laser_position[1] + direction[1]]
                # If lazer hits refract block, add new laser to stack to account for split beam and readjust position
                else:
                    direction = new_direction
                    pos = laser_position
                    laser_position = [pos[0] + direction[0], pos[1] + direction[1]]
                    laser_position_2 = [pos[0] + direction[2], pos[1] + direction[3]]
                    lasers_stack.append([laser_position_2[0], laser_position_2[1], direction[2], direction[3]])
                iterations += 1
                previous_lasers.append([laser_position[0], laser_position[1], direction[0], direction[1]])
                # Remove position from holes if laser passes through
                if laser_position in holes:
                    holes.remove(laser_position)
    if len(holes) == 0:
        return True, lasers_stack
    else:
        return False, lasers_stack


if __name__ == '__main__':
    filename = "yarn_5.bff"
    board_given, empty, blocks, laser, points = load_file(filename)
    time_start = time.time()
    Board = Grid(board_given, blocks, laser, points, empty)
    Board.blocks(filename)
    time_end = time.time()
    print('Run time: %f seconds' % (time_end - time_start))
