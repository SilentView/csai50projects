"""
Tic Tac Toe Player
"""

import math
import copy
X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    numX = 0
    numO = 0
    numE = 0
    for row in board:
        numX += row.count(X)
        numO += row.count(O)
        numE += row.count(EMPTY)
    return X if numX == numO else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    all_actions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                all_actions.append((i, j))
    return all_actions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    fill = O
    if X == player(board):
        fill = X

    # new_board = board[:]
    new_board = copy.deepcopy(board)
    i, j = action
    if board[i][j] != EMPTY:
        raise Exception("Not Empty!")
    new_board[i][j] = fill
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check rows
    for i in range(3):
        if board[i].count(X) == 3:
            return X
        if board[i].count(O) == 3:
            return O
    # check columns
    for j in range(3):
        X_col = 0
        O_col = 0
        for i in range(3):
            X_col += 1 if board[i][j] == X else 0
            O_col += 1 if board[i][j] == O else 0
        if X_col == 3:
            return X
        if O_col == 3:
            return O
    # check diags
    X_diagL = 0
    O_diagL = 0
    X_diagR = 0
    O_diagR = 0
    for i in range(3):
        X_diagL += 1 if board[i][i] == X else 0
        O_diagL += 1 if board[i][i] == O else 0
        X_diagR += 1 if board[i][2-i] == X else 0
        O_diagR += 1 if board[i][2-i] == O else 0
    if X_diagR == 3 or X_diagL == 3:
        return X
    if O_diagR == 3 or O_diagL == 3:
        return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # has winner——over；no winner and full——over
    if winner(board) is not None:
        return True

    for row in board:
        if row.count(EMPTY) != 0:
            return False
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0


def max_value(board):
    if terminal(board):
        return utility(board)
    v = -10
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    if terminal(board):
        return utility(board)
    v = 10
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

def argmax(v):
    ix = 0
    maxV = v[0]
    for i,x in enumerate(v):
        if x > maxV:
            ix, maxV = i, x
    return ix


def argmin(v):
    ix = 0
    minV = v[0]
    for i,x in enumerate(v):
        if x < minV:
            ix, minV = i, x
    return ix

# 关于递归的一个思路：对于基本递归的复杂化就放在被拆开的第一层，在这一层有类似递归主体的结构
# 但是会加入一些其他的处理（如下面记录每一个以寻找对应的action）不要想着一个递归函数调用解决一切的
# 设计，这往往会导致过于复杂
def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    # find max
    if player(board) == X:
        maxi = 0
        maxv = -10
        Actions = actions(board)
        for i, action in enumerate(Actions):
            v = min_value(result(board, action))
            if v > maxv:
                maxv = v
                maxi = i
        return Actions[maxi]
    else:
        mini = 0
        minv = 10
        Actions = actions(board)
        i = 0
        for action in actions(board):
            v = max_value(result(board, action))
            if v < minv:
                minv = v
                mini = i
            i += 1
        return Actions[mini]

