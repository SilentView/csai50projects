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

# 这个算法最有趣的的地方在于标准的传递，每一个player之上都有一个审视的标准，对于minplayer，
# 是上一轮maxplaer的highest预期alpha（current best），对于maxplayer，是上一轮minplayer的lowest预期beta，
# 当审视不存在时，即alpha、beta分别-inf和+inf；当审视者为maxplayer，一旦它发现下一个minplayer的current best比自己的alpha要小，
# 那么这个审视将立即停止，相应的，minplayer的计算也应立即停止，并返回其v。
# 根据这一叙述，可以有一个形象的说法：
# 1.正在计算的是minplayer，那么当前的alpha是上一级审视者maxplayer的，而beta是自己的current best，会随自己计算的推进被下拉；
# 2.正在计算的是maxplayer，那么当前的beta是上一级审视者maxplayer的，而alpha是自己的current best，会随自己计算的推进被上推
# 在分支循环的过程中，审视者的标准会改变


# # 会随自己计算的推进被下拉；
def alphabeta(board, alpha, beta):
    if terminal(board):
        return utility(board)
    all_actions = actions(board)
    if player(board) == X:
        maxv = -10
        for action in all_actions:
            v = alphabeta(result(board, action), alpha, beta)
            maxv = max(maxv, v)
            alpha = max(maxv, alpha)
            if alpha >= beta:
                break
        return maxv
    else:
        minv = 10
        for action in all_actions:
            v = alphabeta(result(board, action), alpha, beta)
            minv = min(minv, v)
            beta = min(beta, minv)
            if beta <= alpha:
                break
        return minv

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



# 关于递归的一个思路：对于基本递归的复杂化就放在被拆开的第一层，在这一层有类似递归主体的结构
# 但是会加入一些其他的处理（如下面记录每一个以寻找对应的action）不要想着一个递归函数调用解决一切的
# 设计，这往往会导致过于复杂
def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    alpha = -10
    beta = 10
    # maxplayer
    if player(board) == X:
        maxi = 0
        maxv = -10
        Actions = actions(board)
        for i, action in enumerate(Actions):
            v = alphabeta(result(board, action), alpha, beta)
            if v > maxv:
                maxv = v
                maxi = i
            alpha = max(maxv, alpha)
        return Actions[maxi]
    # minplayer
    else:
        mini = 0
        minv = 10
        Actions = actions(board)
        for i, action in enumerate(Actions):
            v = alphabeta(result(board, action), alpha, beta)
            if v < minv:
                minv = v
                mini = i
            beta = min(minv, beta)
        return Actions[mini]

