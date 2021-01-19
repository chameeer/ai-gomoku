import itertools
import pisqpipe as pp
from Board import Board
from CriticNetwork import CriticNetwork
import pickle
from pisqpipe import DEBUG_EVAL, DEBUG

MAX_BOARD = 20
board = Board(MAX_BOARD)
critic_network = CriticNetwork(params=[len(board.features)*5 + 2, 60, 1], pattern_finder=board.pattern_finder)

# 读取之前训练好的layer
critic_network.layers = pickle.load(open(r"C:\Users\Yuer\Desktop\pbrain-pyrandom-master\critic_network_big", 'rb'))

# Code followed is alpha-beta purning part
class Node:
    def __init__(self, ruleForPlayers=1, successor=[], isLeaf=False, value=None, action=None):
        if ruleForPlayers == 1:
            self.rule = 'max'
        else:
            self.rule = 'min'
        self.successor = successor
        self.isLeaf = isLeaf
        self.value = value
        self.action = action


def value(node, alpha, beta):
    if node.rule == 'max':
        return maxValue(node, alpha, beta)
    else:
        return minValue(node, alpha, beta)


def maxValue(node, alpha, beta):
    if node.isLeaf:
        return node.value, None
    action = None
    newAlpha = alpha
    up_bound = float('-inf')
    for child in node.successor:
        if minValue(child, newAlpha, beta)[0] > up_bound:
            up_bound = minValue(child, newAlpha, beta)[0]
            action = child.action
        if up_bound >= beta:
            return up_bound, None
        newAlpha = max(newAlpha, up_bound)
    return up_bound, action


def minValue(node, alpha, beta):
    if node.isLeaf:
        return node.value, None
    action = None
    newBeta = beta
    low_bound = float('inf')
    for child in node.successor:
        if maxValue(child, alpha, newBeta)[0] < low_bound:
            action = child.action  # renew action
            low_bound = maxValue(child, alpha, newBeta)[0]
        if low_bound <= alpha:
            return low_bound, None  # pruning, don't care how to arrive it
        newBeta = min(low_bound, newBeta)
    return low_bound, action


def constructTree(n, board, ruleOfPlayers, action, probOfPosition=None):
    '''
	construct a tree using given information, and return the root node
	:param n:  the height of tree
	:param board: the input board described in 2 - dim list form
	:param ruleOfPlayers: root node's type, 1 for max, 0 for min
	:param action: take variance actions accorfing to probability
	:param probOfPosition: all positions that a point can go next
	:return: root node
	'''

    root = Node(ruleForPlayers=ruleOfPlayers, action=action)
    depth = 4
    successors = []
    if not probOfPosition:
        probOfPosition = probablePosition(board)
        if not probOfPosition:
            return None
    choice = dict()
    if n == 1:
        if len(probOfPosition) < depth:
            for position in probOfPosition:
                board_copy = board.deepcopy()
                board_copy[position[0]][position[1]] = ruleOfPlayers
                temp_value = critic_network.forward(board_copy)
                successors.append(
                    Node(ruleForPlayers=3 - ruleOfPlayers, isLeaf=True, value=temp_value, action=position))
        else:
            for position in probOfPosition:
                board_copy = board.deepcopy()
                board_copy[position[0]][position[1]] = ruleOfPlayers
                temp_value = critic_network.forward(board_copy)
                choice[position] = temp_value

            sortChoice = sorted(choice.items(), key=lambda x: x[1], reverse=True)
            for val in range(depth):
                position = sortChoice[val][0]
                successors.append(Node(ruleForPlayers=3 - ruleOfPlayers, isLeaf=True, value=val, action=position))

    else:
        if len(probOfPosition) < depth:
            for position in probOfPosition:
                board_copy = board.deepcopy()
                board_copy[position[0]][position[1]] = ruleOfPlayers
                successors.append(constructTree(n - 1, board_copy, 3 - ruleOfPlayers, position,
                                                updateProbablePosition(position, probOfPosition, board_copy)))
        else:
            for position in probOfPosition:
                board_copy = board.deepcopy()
                board_copy[position[0]][position[1]] = ruleOfPlayers
                temp_value = critic_network.forward(board_copy)
                choice[position] = temp_value

            sortChoice = sorted(choice.items(), key=lambda x: x[1], reverse=True)
            for v in range(depth):
                pos = sortChoice[v][0]
                board_copy = board.deepcopy()
                board_copy[pos[0]][pos[1]] = ruleOfPlayers
                successors.append(constructTree(n - 1, board_copy, 3 - ruleOfPlayers, pos,
                                                updateProbablePosition(pos, probOfPosition, board_copy)))
    root.successor = successors
    return root


def probablePosition(board):
    """
    |x-pos_x|<3, |y-pos_y|<3
    :param
        board: the current board state
    :return:
        position:  all position may be considered
    """
    probable_list = []
    for (pos_x, pos_y) in itertools.product(range(pp.width), range(pp.height)):
        if not board[pos_x][pos_y] == 0:
            continue
        for (i, j) in itertools.product(range(3), range(3)):
            x, y = pos_x + i - 1, pos_y + j - 1
            if x < 0 or x >= pp.width or y < 0 or y >= pp.height:  # out of the board
                continue
            if not board[x][y] == 0:
                probable_list.append((pos_x, pos_y))
                break
    return probable_list  # prob_list may be empty


def updateProbablePosition(action, probable_list, board):
    """
    renew the probable list
    :param
        action: the position AI or player put at
        probable_list: the list needed to be renewed
    :returns
        a new list
    """
    x, y = action[0], action[1]
    for (i, j) in itertools.product(range(3), range(3)):
        new_x = x + i - 1
        new_y = y + j - 1
        if (new_x, new_y) not in probable_list and valid(new_x) and valid(new_y) and board[new_x][new_y] == 0:
            probable_list.append((new_x, new_y))

    if (x, y) in probable_list:
        probable_list.remove((x, y))

    return probable_list


# check whether this position is valid
def valid(x):
    if x >= 0 and x <= pp.height - 1:
        return True
    else:
        return False


# search types around a position 
def pos_type_count(board, pos, turn):
    height = pp.height
    width = pp.width
    if turn == 'my':
        five = '11111'
        four = '011110'
    else:
        five = '22222'
        four = '022220'
    types = {'FIVE': 0, 'FOUR': 0}
    item_list = list()

    # search types in row
    row = ''
    for x in range(max(0, pos[1] - 4), min(width, pos[1] + 5)):
        row += str(board[pos[0]][x])
    item_list.append(row)

    # search types in column
    col = ''
    for y in range(max(0, pos[0] - 4), min(height, pos[0] + 5)):
        col += str(board[y][pos[1]])
    item_list.append(col)

    # search types in diagonal
    row1 = ''
    row2 = ''
    for k in range(-4, 5):
        x1 = pos[0] + k
        y1 = pos[1] + k
        if valid(x1) and valid(y1):
            row1 += str(board[x1][y1])
        x2 = pos[0] + k
        y2 = pos[1] - k
        if valid(x2) and valid(y2):
            row2 += str(board[x2][y2])
    item_list.append(row1)
    item_list.append(row2)

    for item in item_list:
        if five in item:
            types['FIVE'] += 1
        if four in item:
            types['FOUR'] += 1

    return types


# pre-process module
def pre_process(board):
    probOfPosition = probablePosition(board)
    rank = {2: 0, 3: 0, 4: 0}
    for pos in probOfPosition:
        board_copy_my = board.deepcopy()
        board_copy_my[pos[0]][pos[1]] = 1
        type_list_my = pos_type_count(board_copy_my, pos, 'my')
        if type_list_my['FIVE'] != 0:
            return pos
        if type_list_my['FOUR'] != 0:
            rank[3] = pos

        board_copy_opponent = board.deepcopy()
        board_copy_opponent[pos[0]][pos[1]] = 2
        type_list_opponent = pos_type_count(board_copy_opponent, pos, 'opponent')
        if type_list_opponent['FIVE'] != 0:
            rank[2] = pos
        if type_list_opponent['FOUR'] != 0:
            rank[4] = pos

    if rank[2] != 0:
        return rank[2]
    elif rank[3] != 0:
        return rank[3]
    elif rank[4] != 0:
        return rank[4]
    else:
        return None


def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")

def brain_restart():
    global adjacent
    adjacent = []
    board.reset()
    pp.pipeOut("OK")

def isFree(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
	if isFree(x,y):
		board[x][y] = 1
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	if isFree(x,y):
		board[x][y] = 2
	else:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	if isFree(x,y):
		board[x][y] = 3
	else:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
		board[x][y] = 0
		return 0
	return 2

def pruning_brain():
    action = pre_process(board)
    if action is not None:
        x, y = action
        pp.do_mymove(x, y)
    else:
        max_depth = 2
        root_node = constructTree(max_depth, board, 1, None)
        if root_node is None:
        # logDebug("This is the log when root node is None")
            pp.do_mymove(10, 10)
        else:
            _, action = value(root_node, float("-inf"), float("inf"))
        # assert action is not None
        # logDebug("This is the log when root node is not None")
            pp.do_mymove(action[0], action[1])


def brain_end():
	pass

def brain_about():
	pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
	import win32gui
	def brain_eval(x, y):
		# TODO check if it works as expected
		wnd = win32gui.GetForegroundWindow()
		dc = win32gui.GetDC(wnd)
		rc = win32gui.GetClientRect(wnd)
		c = str(board[x][y])
		win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
		win32gui.ReleaseDC(wnd, dc)


# "overwrites" functions in pisqpipe module
pp.width, pp.height = 20, 20
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = pruning_brain
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval

def main():
	pp.main()

if __name__ == "__main__":
	main()

