# functions of Upper Confidence bounds for Tree (UCT)
# UCT方法要求对每一个可能的状态都进行模拟一次后，才能重复模拟表现最优的状态，因此对模拟次数有更高的要求

# 使用说明：
# 调用 UCT(board, action)，函数其中board和action为待模拟的棋盘和动作，输出reward

import pp
import random
import itertools
import copy
import time
import math
# import pisqpipe as pp

simulation_times = 200

# 树节点
class UCTNode:
    def __init__(self, board, action, turn, parent):
        # 需要更新的初始状态
        self.state = board
        self.action = action
        self.turn = turn
        self.parent = parent
        self.candidate = []
        self.is_terminal = False

        # 每expand一次，加入children中
        self.children = []

        # 用于backup
        self.reward = 0
        self.count = 0


# UCT主函数，包括selection、expand、simulation、backup
def UCT(board, action):
    # 创建根节点
    turn = 1  # 假设下一步为我方落子
    board[action[0]][action[1]] = turn
    root = UCTNode(board, action, turn, None)  # 根结点，state为待模拟的棋盘
    root.candidate = probablePosition(root.state)  # 该状态下可能的落子位置
    if is_terminal(root.state) or is_win(root.state, root.action, root.turn):
        root.is_terminal = True  # 该节点的状态非terminal状态

    times = 0
    while times < simulation_times:
        vl = TreePolicy(root)  # selection + expand
        probOfPosition = probablePosition(vl.state)
        board = copy.deepcopy(vl.state)
        value = simulation(board, vl.action, vl.turn, probOfPosition)  # simulation
        backup(vl, value)  # backup
        times += 1
    return root.reward/root.count


# selection + expand
def TreePolicy(v):
    while not v.is_terminal:  # 若该节点状态非terminal状态
        if len(v.candidate) != 0:  # 若该节点还没有完全expand（即还有子节点未进行模拟）
            return expand(v)  # expand
        else:
            v = BestChild(v, 1/math.sqrt(2), v.turn)  # 否则选取子节点中UCB值最高的节点
    return v


def expand(v):
    # 随机选择一个candidate（即未expand的子节点），并从candidate中删去
    action = random.sample(v.candidate, 1)[0]
    v.candidate.remove(action)

    # 将该子节点加入children
    turn = 3 - v.turn  # 子节点为对手落子
    state = copy.deepcopy(v.state)
    state[action[0]][action[1]] = turn  # 更新棋盘状态
    parent = v  # 父节点
    u = UCTNode(state, action, turn, parent)  # 创建子节点
    u.candidate = probablePosition(u.state)
    if is_terminal(u.state) or is_win(u.state, u.action, u.turn):
        u.is_terminal = True
    v.children.append(u)

    return u


# 选择最佳子节点
def BestChild(v, c, turn):
    candidates = dict()
    for child in v.children:
        candidates[child] = child.reward / child.count \
                       + c * math.sqrt(2 * math.log(v.count)/child.count)
    candidate = sorted(candidates.items(), key=lambda x: x[1], reverse=True)  # 按照值从大到小排列
    if turn == 1:  # 若子节点为对方落子，则选最小值（即对方的最优子节点）
        return candidate[-1][0]
    else:  # 若子节点为我方落子，则选最大值（即我方的最优节点）
        return candidate[0][0]


# 从选择好的节点开始模拟
def simulation(board, pos, turn, probOfPosition):
    board[pos[0]][pos[1]] = turn
    if is_win(board, pos, turn):
        if turn == 1:
            return 1
        else:
            return 0  # 原论文中取值为0
    if is_terminal(board):
        return 0
    action = pre_process(board, 3-turn)
    if action is not None:  # 可以直接决定下一步的动作（堵/连四/连五）
        updateProbablePosition(action, probOfPosition)
        return simulation(board, action, 3-turn, probOfPosition)
    else:  # 随机从可以选择的动作中选一个
        action = random.sample(probOfPosition, 1)[0]
        updateProbablePosition(action, probOfPosition)
        return simulation(board, action, 3-turn, probOfPosition)


# 回溯更新一次iteration中经过的状态
def backup(v, r):
    while v is not None:
        v.count += 1
        v.reward += r
        v = v.parent


# 判断是否获胜
# 输入棋盘和本轮轮次，turn = 1则为自己的轮次，否则为对手轮次
def is_win(board, pos, turn):
    if turn == 1:
        type_list = pos_type_count(board, pos, 'my')
    else:
        type_list = pos_type_count(board, pos, 'opponent')
    if type_list['FIVE'] != 0:
        return True


# 判断是否已经没有地方落子，即平局
def is_terminal(board):
    probOfPosition = probablePosition(board)
    if len(probOfPosition) == 0:
        return True


# 给定棋盘，返回可能的动作；同example中已实现的函数
def probablePosition(board):
    """
    |x-pos_x|<3, |y-pos_y|<3
    :param
        board: the current board state
    :return:
        position: all position may be considered
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


# 更新动作
def updateProbablePosition(action, probable_list):
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
        if (new_x, new_y) not in probable_list and valid(new_x) and valid(new_y):
            probable_list.append((new_x, new_y))

    if (x, y) in probable_list:
        probable_list.remove((x, y))


# 判断坐标是否在棋盘内（update修改）
def valid(x):
    if x >= 0 and x <= pp.height-1:
        return True
    else:
        return False


# 计算一个棋子周围的棋型（five、four）
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
        x1 = pos[0]+k
        y1 = pos[1]+k
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


# 直接决定下一步的动作（堵/连四/连五）
def pre_process(board):
    probOfPosition = probablePosition(board)
    rank = {2:0, 3:0, 4:0}
    for pos in probOfPosition:
        board_copy_my = copy.deepcopy(board)
        board_copy_my[pos[0]][pos[1]] = 1
        type_list_my = pos_type_count(board_copy_my, pos, 'my')
        if type_list_my['FIVE'] != 0:
            return pos  # rank 1 直接返回
        if type_list_my['FOUR'] != 0:
            rank[3] = pos

        board_copy_opponent = copy.deepcopy(board)
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
