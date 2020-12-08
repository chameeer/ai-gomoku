import itertools
import random
import copy
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
import board_evaluate as be

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'

MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]


def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")


def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
    pp.pipeOut("OK")


def isFree(x, y):
    return pp.width > x >= 0 == board[x][y] and 0 <= y < pp.height


def brain_my(x, y):
    if isFree(x, y):
        board[x][y] = 1
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    if isFree(x, y):
        board[x][y] = 2
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_block(x, y):
    if isFree(x, y):
        board[x][y] = 3
    else:
        pp.pipeOut("ERROR winning move [{},{}]".format(x, y))


def brain_takeback(x, y):
    if pp.width > x >= 0 != board[x][y] and 0 <= y < pp.height:
        board[x][y] = 0
        return 0
    return 2


def brain_turn():
    if pp.terminateAI:
        return
    i = 0
    while True:
        x = random.randint(0, pp.width)
        y = random.randint(0, pp.height)
        i += 1
        if pp.terminateAI:
            return

        if isFree(x, y):
            break
    if i > 1:
        pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    pp.do_mymove(x, y)


def brain_end():
    pass


def brain_about():
    pp.pipeOut(pp.infotext)


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
    temp_alpha = alpha
    up_bound = float('-inf')
    # print 'len', len(node.successor)
    for child in node.successor:
        # print child.value, temp_alpha, beta
        if minValue(child, temp_alpha, beta)[0] > up_bound:
            # print 'hhh', minValue(child, temp_alpha, beta)[0], up_bound
            # print 'first if called'
            up_bound = minValue(child, temp_alpha, beta)[0]
            action = child.action  # renew action
        if up_bound >= beta:
            # print 'second if called'
            return up_bound, None  # pruning, don't care how to arrive it
        temp_alpha = max(temp_alpha, up_bound)
    return up_bound, action


def minValue(node, alpha, beta):
    if node.isLeaf:
        return node.value, None
    action = None
    temp_beta = beta
    low_bound = float('inf')
    for child in node.successor:
        if maxValue(child, alpha, temp_beta)[0] < low_bound:
            action = child.action  # renew action
            low_bound = maxValue(child, alpha, temp_beta)[0]
        if low_bound <= alpha:
            return low_bound, None  # pruning, don't care how to arrive it
        temp_beta = min(low_bound, temp_beta)
    return low_bound, action


def constructTree(n, board, ruleOfPlayers, action, probOfPosition=None):
    '''
	construct a tree using given information, and return the root node
	:param n:  the height of tree
	:param tree: the input tree described with list nested structure
	:param rule: root node's type, 1 for max, 0 for min
	:return: root node
	'''

    node = Node(ruleForPlayers=ruleOfPlayers, action=action)
    depth = 4
    successors = []
    if probOfPosition == None:
        probOfPosition = probable_position(board)
        if probOfPosition == None:
            return None
    top_list = []
    if n == 1:
        if len(probOfPosition) < depth:
            for pos in probOfPosition:
                board_copy = copy.deepcopy(board)
                board_copy[pos[0]][pos[1]] = ruleOfPlayers
                temp_value = be.evaluate(board_copy)
                successors.append(
                    Node(ruleOfPlayers=3 - ruleOfPlayers, isLeaf=True, value=temp_value,
                         action=pos))
        else:
            for pos in probOfPosition:
                board_copy = copy.deepcopy(board)
                board_copy[pos[0]][pos[1]] = ruleOfPlayers
                temp_value = be.evaluate(board_copy)
                top_list.append(temp_value)
            temp_list = top_list[:]
            temp_list.sort(reverse=True)
            for v in temp_list[0:depth]:
                pos = probOfPosition[top_list.index(v)]
                successors.append(Node(ruleForPlayers=3 - ruleOfPlayers, isLeaf=True, value=v, action=pos))

    else:
        if len(probOfPosition) < depth:
            for pos in probOfPosition:
                # i += 1
                # print pos, 'else called', i
                board_copy = copy.deepcopy(board)
                board_copy[pos[0]][pos[1]] = ruleOfPlayers
                # print board_copy
                successors.append(
                    constructTree(n - 1, board_copy, 3 - ruleOfPlayers, pos,
                                  renew_probable_position(pos, probOfPosition)))
        else:
            for pos in probOfPosition:
                board_copy = copy.deepcopy(board)
                board_copy[pos[0]][pos[1]] = ruleOfPlayers
                top_list.append(be.evaluate(board_copy))
            temp_list = top_list[:]
            temp_list.sort(reverse=True)
            for v in temp_list[0:depth]:
                pos = probOfPosition[top_list.index(v)]
                board_copy = copy.deepcopy(board)
                board_copy[pos[0]][pos[1]] = ruleOfPlayers
                successors.append(
                    constructTree(n - 1, board_copy, 3 - ruleOfPlayers, pos,
                                  renew_probable_position(pos, probOfPosition)))
    node.successor = successors
    return node


def probable_position(board):
    """
    find all position that may be considered as the next action.
    exist (x,y) not free, such that |x-pos_x|<3, |y-pos_y|<3
    :param
        board: the current board state
    :return:
        position:  all position may be considered
    """
    probable_list = []
    scale = 1
    for (pos_x, pos_y) in itertools.product(range(pp.width), range(pp.height)):
        if not board[pos_x][pos_y] == 0:
            continue
        for (i, j) in itertools.product(range(2 * scale + 1), range(2 * scale + 1)):
            x, y = pos_x + i - scale, pos_y + j - scale
            if x < 0 or x >= pp.width or y < 0 or y >= pp.height:  # out of the board
                continue
            if not board[x][y] == 0:  # a chess is in the region
                probable_list.append((pos_x, pos_y))
                break
    if not probable_list:
        return None
    return probable_list  # prob_list may be empty


def renew_probable_position(action, probable_list):
    """
    renew the probable list
    :param
        action: the position AI or player put at
        probable_list: the list needed to be renewed
    :returns
        a new list
    """
    x, y = action[0], action[1]
    scale = 1

    for (i, j) in itertools.product(range(2 * scale + 1), range(2 * scale + 1)):
        new_x = x + i - scale
        new_y = y + j - scale
        if (new_x, new_y) not in probable_list:
            probable_list.append((new_x, new_y))

    if (x, y) in probable_list:
        probable_list.remove((x, y))

    return probable_list


def pre_process(board):
    probOfPosition = probable_position(board)
    # 判断是否可以直接形成连五或活四
    for pos in probOfPosition:
        board_copy_my = copy.deepcopy(board)
        board_copy_my[pos[0]][pos[1]] = 1
        type_list_my = be.board_type_count(board_copy_my, 'my', attack=False)
        if type_list_my['FIVE'] != 0:
            return pos[0], pos[1]
        else:
            continue
    for pos in probOfPosition:
        board_copy_opponent = copy.deepcopy(board)
        board_copy_opponent[pos[0]][pos[1]] = 2
        type_list_opponent = be.board_type_count(board_copy_opponent, 'opponent', attack=False)
        if type_list_opponent['FIVE'] != 0 or type_list_opponent['FOUR'] != 0:
            return pos[0], pos[1]
        else:
            continue
    for pos in probOfPosition:
        board_copy_my = copy.deepcopy(board)
        board_copy_my[pos[0]][pos[1]] = 1
        type_list_my = be.board_type_count(board_copy_my, 'my', attack=False)
        if type_list_my['FOUR'] != 0:
            return pos[0], pos[1]
        else:
            continue
    return None


def pruning_brain():
    max_depth = 2
    root_node = constructTree(max_depth, board, 1, None)
    if pre_process(board) is not None:
        x, y = pre_process(board)
        pp.do_mymove(x, y)
    else:
        if root_node is None:
            # logDebug("This is the log when root node is None")
            pp.do_mymove(10, 10)
        else:
            max_value, action = value(root_node, float("-inf"), float("inf"))
            # assert action is not None
            # logDebug("This is the log when root node is not None")
            pp.do_mymove(action[0], action[1])


if DEBUG_EVAL:
    import win32gui


    def brain_eval(x, y):
        # TODO check if it works as expected
        wnd = win32gui.GetForegroundWindow()
        dc = win32gui.GetDC(wnd)
        rc = win32gui.GetClientRect(wnd)
        c = str(board[x][y])
        win32gui.ExtTextOut(dc, rc[2] - 15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################
#
# # define a file for logging ...
# DEBUG_LOGFILE = "/tmp/pbrain-pyrandom.log"
# # ...and clear it initially
# with open(DEBUG_LOGFILE, "w") as f:
#     pass
#
#
# # define a function for writing messages to the file
# def logDebug(msg):
#     with open(DEBUG_LOGFILE, "a") as f:
#         f.write(msg + "\n")
#         f.flush()
#
#
# # define a function to get exception traceback
# def logTraceBack():
#     import traceback
#     with open(DEBUG_LOGFILE, "a") as f:
#         traceback.print_exc(file=f)
#         f.flush()
#     raise


# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
# def brain_turn():
# 	logDebug("some message 1")
# 	try:
# 		logDebug("some message 2")
# 		1. / 0. # some code raising an exception
# 		logDebug("some message 3") # not logged, as it is after error
# 	except:
# 		logTraceBack()

######################################################################

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
