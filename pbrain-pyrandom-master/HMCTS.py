# functions of Heuristic Monte Carlo Tree Search (HMCTS)

# 使用说明：
# 调用 HMCTS_value(board, pos)函数，其中board和pos为待模拟的棋盘和动作，输出reward

# ADP + HMCTS 思路：
# 先用board_evaluation/Neutral Network找出【k】个value最高的动作，
# 对每个动作进行HMCTS【n】次计算reward，最后将value和reward进行加权求和排序
# （需要调整合适的值的相对大小）（待调整）

# 待改进：
# 现在模拟的速度大概为10次模拟3s，还是不能大量模拟（于是参考价值就很小）
# 已经精简了很多流程，不知道还能不能再提升

import random
import itertools
import copy
import time
import pisqpipe as pp

simulation_times = 100

# 该函数可忽略
# HMCTS主函数，输入棋盘，返回查询后最优的动作及reward；此函数无法与value函数连接
def HMCTS(board):
    probOfPosition = probablePosition(board)
    probOfPosition_copy1 = copy.deepcopy(probOfPosition)
    candidate = dict()
    for pos in probOfPosition:
        starttime = time.time()
        total_reward = 0
        times = 0
        updateProbablePosition(pos, probOfPosition_copy1)
        while times < simulation_times:
            board_copy = copy.deepcopy(board)
            probOfPosition_copy2 = copy.deepcopy(probOfPosition_copy1)
            reward = simulation(board_copy, pos, 1, probOfPosition_copy2)
            print(reward)
            total_reward += reward
            times += 1
        print((pos, total_reward))
        endtime = time.time()
        print(round(endtime - starttime, 4))
        candidate[pos] = total_reward
    candidate = sorted(candidate.items(), key=lambda x: x[1])
    return candidate[0]  # (action, reward)


# 给定棋盘和动作，对该动作进行查询，返回reward；此函数可与value函数连接
def HMCTS_value(board, pos):
    total_reward = 0
    times = 0
    probOfPosition = probablePosition(board)
    while times < simulation_times:
        board_copy = copy.deepcopy(board)
        probOfPosition_copy = copy.deepcopy(probOfPosition)
        reward = simulation(board_copy, pos, 1, probOfPosition_copy)
        total_reward += reward
        times += 1
    return total_reward


# 模拟函数，输入棋盘的待估值的动作，返回reward
def simulation(board, pos, turn, probOfPosition):
    board[pos[0]][pos[1]] = turn
    if is_win(board, pos, turn):
        if turn == 1:
            return 1
        else:
            return -1  # 原论文中取值为0
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
def pre_process(board, turn):
    probOfPosition = probablePosition(board)
    turn_name = {1: 'my', 2: 'opponent'}
    rank = {3:0, 4:0}
    for pos in probOfPosition:
        board_copy_my = copy.deepcopy(board)
        board_copy_my[pos[0]][pos[1]] = turn
        type_list_my = pos_type_count(board_copy_my, pos, turn_name[turn])
        if type_list_my['FIVE'] != 0:
            return pos  # rank 1 直接返回
        if type_list_my['FOUR'] != 0:
            rank[3] = pos

        board_copy_opponent = copy.deepcopy(board)
        board_copy_opponent[pos[0]][pos[1]] = 3 - turn
        type_list_opponent = pos_type_count(board_copy_opponent, pos, turn_name[3 - turn])
        if type_list_opponent['FIVE'] != 0:
            return pos  # rank 2 直接返回
        if type_list_my['FOUR'] != 0:
            rank[4] = pos

    if rank[3] != 0:
        return rank[3]
    elif rank[4] != 0:
        return rank[4]
    else:
        return None

