"""Implementation of command-line minesweeper by Abdul Basit Tonmoy
"""

import random
import re


# let's create a board object to represent the minesweeper game
# this is so that we can just say "create a new board object", or
# "dig here", or render this game for this object"
class Board:
    def __init__(self, dimension_size, num_bombs):
        # let's keep track of these parameters, they'll be helpful later
        self.dimension_size = dimension_size
        self.num_bombs = num_bombs

        # let's create the board
        self.board = self.make_new_board()
        self.assign_values_to_board()

        # Initialize a set to keep track of which locations we've uncovered
        # we'll save (row, col) tuples into this set
        self.dug = set()

    def make_new_board(self):
        # construct a new board based on the dimension size and num bomb
        # we  should construct the list of lists (or whatever representation you prefer
        # but since we have a 2D board, list of list is most natural)

        # generate a new board
        board = [[None for _ in range(self.dimension_size)] for _ in range(self.dimension_size)]
        # this creates an array like this:
        # [[None, None, ...., None],
        # [None, None,  ...., None],
        # [...                    ],
        # [None, None,  ...., None],]
        # we can see how this represents a board!
        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            loc = random.randint(0, self.dimension_size**2 - 1)  # return a random integer N such that a <= N <= b
            row = loc // self.dimension_size  # we want the number of times dimension_size
            # goes into loc to tell us what row to look at
            col = loc % self.dimension_size  # we want the remainder to tell us what index in the row to look at

            if board[row][col] == "*":
                # this means we've actually planted a bomb there already so keep going
                continue

            board[row][col] = "*"  # plant the bomb
            bombs_planted += 1

        return board

    def assign_values_to_board(self):
        # now that we have the bombs planted, let's assign a number 0-8 for all the empty spaces, which
        # represents how many neighbouring bombs there are. We can precompute these and it'll save us some
        # effort checking what's around the board later on :))
        for r in range(self.dimension_size):
            for c in range(self.dimension_size):
                if self.board[r][c] == "*":
                    # if this is already a bomb, we don't want to calculate anything
                    continue
                self.board[r][c] = self.get_num_neighboring_bombs(r, c)

    def get_num_neighboring_bombs(self, row, col):
        # let's iterate though each of the neighboring positions and sum number of bombs
        # top left: (row-1, col-1)
        # top middle: (row-1, col)
        # top right: (row-1, col+1)
        # left: (row, col-1)
        # right: (row, col+1)
        # bottom left: (row+1, col-1)
        # bottom middle: (row+1, col)
        # bottom right: (row+1, col+1)

        # make sure to not go out of bounds!

        num_neighbouring_bombs = 0
        for r in range(max(0, row-1), min(self.dimension_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dimension_size-1, col+1)+1):
                if r == row and c == col:
                    continue
                if self.board[r][c] == "*":
                    num_neighbouring_bombs += 1

        return num_neighbouring_bombs

    def dig(self, row, col):
        # dig at that location
        # return True if successful dig, False if bomb dug

        # a few scenarios:
        # hit a bomb -> game over
        # dig at a location with neighboring bombs -> finish digging
        # dig at a location with no neighboring bombs -> recursively dig neighbors!

        self.dug.add((row, col))  # keep track that we dug here

        if self.board[row][col] == "*":
            return False
        elif self.board[row][col] > 0:
            return True

        # self.board[row][col] == 0
        for r in range(max(0, row-1), min(self.dimension_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dimension_size-1, col+1)+1):
                if (r, c) in self.dug:
                    continue  # don't dig where you've already dug
                self.dig(r, c)

        # if our initial dig didn't hit a bomb, we *shouldn't* hit a bomb here
        return True

    def __str__(self):
        # this is a magic function where if you call print on this object,
        # it'll print out what this function returns!
        # return a string that shows the board to the player

        # first let's create a new array that represents what the user would see
        visible_board = [[None for _ in range(self.dimension_size)] for _ in range(self.dimension_size)]
        for row in range(self.dimension_size):
            for col in range(self.dimension_size):
                if (row, col) in self.dug:
                    visible_board[row][col] = str(self.board[row][col])
                else:
                    visible_board[row][col] = ' '

        # put this together in a string
        string_rep = ''
        # get max column widths for printing
        widths = []
        for idx in range(self.dimension_size):
            columns = map(lambda x: x[idx], visible_board)
            widths.append(
                len(
                    max(columns, key=len)
                )
            )

        # print the csv strings
        indices = [i for i in range(self.dimension_size)]
        indices_row = '   '
        cells = []
        for idx, col in enumerate(indices):
            format = '%-' + str(widths[idx]) + "s"
            cells.append(format % (col))
        indices_row += '  '.join(cells)
        indices_row += '  \n'

        for i in range(len(visible_board)):
            row = visible_board[i]
            string_rep += f'{i} |'
            cells = []
            for idx, col in enumerate(row):
                format = '%-' + str(widths[idx]) + "s"
                cells.append(format % (col))
            string_rep += ' |'.join(cells)
            string_rep += ' |\n'

        str_len = int(len(string_rep) / self.dimension_size)
        string_rep = indices_row + '-'*str_len + '\n' + string_rep + '-'*str_len

        return string_rep


# Play the game
def play(dimension_size=10, num_bombs=10):
    # Step 1: create the board and plant bombs
    board = Board(dimension_size, num_bombs)
    # Step 2: show the user the board and ask for where they want to dig

    # Step 3(a): if the location is bomb, show "game over" message
    # Step 3(b): if the location is not a bomb, dig recursively until each square
    #            is at least next to a bomb
    # Step 4 : repeat steps 2 and 3(a)/(b) until there are no more places to dig --> VICTORY
    safe = True

    while len(board.dug) < board.dimension_size ** 2 - num_bombs:
        print(board)
        # 0,0 or 0, 0 or 0,    0
        user_input = re.split(',(\\s)*', input("Where would you like to dig? Input as row,col: "))  # (0, 3)
        row, col = int(user_input[0]), int(user_input[-1])
        if row < 0 or row >= board.dimension_size or col < 0 or col >= board.dimension_size:
            print("Invalid location. Try again")

        # if it's valid, we dig
        safe = board.dig(row, col)
        if not safe:
            # dug a bomb and dead!!!
            break  # game over RIP

    if safe:
        print("CONGRATULATIONS!!! YOU HAVE WON!")
    else:
        print("SORRY, GAME OVER :( ")
        board.dug = [(r,c) for r in range(board.dimension_size) for c in range(board.dimension_size)]
        print(board)


if __name__ == '__main__':
    play()