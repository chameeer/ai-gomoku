# 判断棋盘上的棋型（20*20）并计算相应的值函数

import pisqpipe as pp
import copy

# values of type
# 待调整
SIX = 10000000
FIVE = 2000000
FOUR = 100000
BROKEN_FOUR = 1000
THREE = 1000
BROKEN_THREE = 50
TWO = 50
BROKEN_TWO = 5
ONE = 5
BROKEN_ONE = 1

values = {'SIX':SIX, 'FIVE':FIVE, 'FOUR':FOUR, 'BROKEN_FOUR':BROKEN_FOUR, 'THREE':THREE, 'BROKEN_THREE':BROKEN_THREE,
            'TWO':TWO, 'BROKEN_TWO':BROKEN_TWO, 'ONE':ONE, 'BROKEN_ONE':BROKEN_ONE}

# evalute the board
# 已完成
def evaluate(board):
    type_my = board_type_count(board, 'my', attack = True)
    type_opponent = board_type_count(board, 'opponent', attack = True)
    value = type_value(type_my) - type_value(type_opponent)*2
    return value

# compute the value of given types
# 待调整:同时出现XXX和XXX，分数提高
def type_value(types):
    value = 0
    for type, num in types.items():
        value += num * values[type]
    type1 = types['BROKEN_FOUR'] + types['THREE']
    type2 = types['BROKEN_THREE'] + types['TWO']
    if type1 >= 2:  # 同时出现冲四和活三
        value += values['FOUR']*(type1-1)
    #if type2 >= 2:  # 同时出现眠三和活二
    #    value += values['THREE']*(type2-1)
    return value

# compute the number of types of a given board
# 已完成
# attack = False: 防守
# attack = True: 进攻
def board_type_count(board, turn, attack):

    height = pp.height
    width = pp.width
    if turn == 'my':
        M = 1
        P = 2
    else:
        M = 2
        P = 1
    types = {'SIX': 0, 'FIVE': 0, 'FOUR': 0, 'BROKEN_FOUR': 0, 'THREE': 0, 'BROKEN_THREE': 0,
             'TWO': 0, 'BROKEN_TWO': 0, 'ONE': 0, 'BROKEN_ONE': 0}
    item_list = list()

    # search types in row
    for y in range(height):
        row = list()
        for x in range(width):
            row.append(board[x][y])
        if row.count(M) == 0:
            continue
        items = str(row)[1:-1].replace(', ','').split(str(P)) # 以2为分隔符，得到由0、1组成的序列
        item_list  = item_list + items

    # search types in column
    for x in range(width):
        column = list()
        for y in range(height):
            column.append(board[x][y])
        if column.count(M) == 0:
            continue
        items = str(column)[1:-1].replace(', ','').split(str(P)) # 以2为分隔符，得到由0、1组成的序列
        item_list = item_list + items

    # search types from lower_right to top_left
    for k in range(4, width): # k=4 k=19
        row = list()
        for i in range(k+1):
            row.append(board[k-i][i])
        if row.count(M) == 0:
            continue
        items = str(row)[1:-1].replace(', ', '').split(str(P))  # 以2为分隔符，得到由0、1组成的序列
        item_list = item_list + items
    for k in range(width, 2*width-5):
        row = list()
        for i in range(2*width-k-1):
            row.append(board[width-1-i][k-width+1+i])
        if row.count(M) == 0:
            continue
        items = str(row)[1:-1].replace(', ', '').split(str(P))  # 以2为分隔符，得到由0、1组成的序列
        item_list = item_list + items

    # search types from lower_left to top_right
    for k in range(0, width-4):
        row = list()
        for i in range(width-k):
            row.append(board[i+k][i])
        if row.count(M) == 0:
            continue
        items = str(row)[1:-1].replace(', ', '').split(str(P))  # 以2为分隔符，得到由0、1组成的序列
        item_list = item_list + items
    for k in range(1, width-4):
        row = list()
        for i in range(width - k):
            row.append(board[i][i+k])
        if row.count(M) == 0:
            continue
        items = str(row)[1:-1].replace(', ', '').split(str(P))  # 以2为分隔符，得到由0、1组成的序列
        item_list = item_list + items

    for item in item_list:
        if len(item) < 5 or item.count(str(M)) == 0:
            continue
        else:
            if attack == True:
                item_type_count(item, str(M), types)
            else:
                item_type_easy_count(item, str(M), types)
    return types


# 判断是否可以直接形成连五或活四
def item_type_easy_count(item, my, type_list):
    five = my * 5
    four = '0' + my * 4 + '0'
    broken_four = [my*3 + '0' +my, my*2+'0'+my*2, my*4+'0', '0'+my*4, my +'0'+my*3]
    three = ['0' + my * 3 + '00', '0' + my*2 + '0' + my + '0', '00'+my*3+'0']
    if five in item:
        type_list['FIVE'] += 1
    if four in item:
        type_list['FOUR'] += 1
    for i in three:
        if i in item:
            type_list['THREE'] += 1
    for i in broken_four:
        if i in item:
            type_list['THREE'] += 1


# compute the number of types of a given item
# 已完成
def item_type_count(item, my, type_list):
    length = len(item)
    num = item.count(my)
    left_flag = False
    right_flag = False
    if item.startswith(my):
        left_flag = True
    if item.endswith(my):
        right_flag = True
    strip_item = item.strip('0')

    if num == 1:
        if length == 5 or left_flag or right_flag:
            type_list['BROKEN_ONE'] += 1
        else:
            type_list['ONE'] += 1

    if num == 2:
        if length == 5:
            type_list['BROKEN_TWO'] += 1
        else:
            if len(strip_item) <= 5:
                if left_flag or right_flag:
                    type_list['BROKEN_TWO'] += 1
                else:
                    type_list['TWO'] += 1
            else:
                if left_flag and right_flag:
                    type_list['BROKEN_ONE'] += 2
                elif left_flag or right_flag:
                    type_list['BROKEN_ONE'] += 1
                    type_list['ONE'] += 1
                else:
                    type_list['ONE'] += 2

    if num == 3:
        if length == 5:
            type_list['BROKEN_THREE'] += 1
        else:
            if len(strip_item) <= 4:
                if left_flag or right_flag:
                    type_list['BROKEN_THREE'] += 1
                else:
                    type_list['THREE'] += 1
            elif len(strip_item) == 5:
                type_list['BROKEN_THREE'] += 1
            elif len(strip_item) <= 10:
                if left_flag and right_flag:
                    type_list['BROKEN_ONE'] += 1
                    type_list['BROKEN_TWO'] += 1
                elif left_flag:
                    if item[:5].count(my) == 1:
                        type_list['BROKEN_ONE'] += 1
                        type_list['TWO'] += 1
                    else:
                        type_list['BROKEN_TWO'] += 1
                        type_list['ONE'] += 1
                elif right_flag:
                    if item[-5:].count(my) == 1:
                        type_list['BROKEN_ONE'] += 1
                        type_list['TWO'] += 1
                    else:
                        type_list['BROKEN_TWO'] += 1
                        type_list['ONE'] += 1
                else:
                    type_list['ONE'] += 1
                    type_list['TWO'] += 1
            else:
                if left_flag:
                    if item[:5].count(my) == 2:
                        type_list['BROKEN_TWO'] += 1
                    else:
                        type_list['BROKEN_ONE'] += 1
                else:
                    if item[:5].count(my) == 2:
                        type_list['TWO'] += 1
                    else:
                        type_list['ONE'] += 1
                if right_flag:
                    if item[-5:].count(my) == 2:
                        type_list['BROKEN_TWO'] += 1
                    else:
                        type_list['BROKEN_ONE'] += 1
                else:
                    if item[-5].count(my) == 2:
                        type_list['TWO'] += 1
                    else:
                        type_list['ONE'] += 1
                if item[:5].count(my) == 1 and item[-5].count(my) == 1:
                    type_list['ONE'] += 1

    if num == 4:
        if length == 5:
            type_list['BROKEN_FOUR'] += 1
        else:
            if len(strip_item) == 4:
                if left_flag or right_flag:
                    type_list['BROKEN_FOUR'] += 1
                else:
                    type_list['FOUR'] += 1
            elif len(strip_item) == 5:
                type_list['BROKEN_FOUR'] += 1
            else:
                long_item_type_count(item, my, type_list)

    if num == 5:
        if length == 5:
            type_list['FIVE'] += 1
        else:
            if len(strip_item) == 5:
                type_list['FIVE'] += 1
            else:
                long_item_type_count(item, my, type_list)

    if num >= 6:
        long_item_type_count(item, my, type_list)

# 未完成(4,5,6)
def long_item_type_count(item, my, type_list):
    # count the type number of items whose length is more than 5 and have more than 3 '1'# 未完成(4,5,6)
    #
    # 111001,110011,110101
    # 1110001, 1101001, 1100101, 1100011, 1011001, 1010101
    # 11100001, 11010001, 11001001, 11000101, 11000011, 10110001, 10101001, 10100101, 10011001
    # ...
    #
    # 111011,111101
    # 1111001,1110011,1101011,1011011,1010111,1011101
    # ...
    #
    # 111111, 1011111,
    # ...
    six = my * 6
    five = my * 5
    four = '0' + my * 4 + '0'
    three = ['0' + my * 3 + '0' + '0', '0' + my*2 + '0' + my + '0']
    broken_three1 = [my * 3, my * 2 + '0' + my, my + '0' + my * 2]
    broken_three2 = [my * 2 + '0' * 2 + my, my + '0' + my + '0' + my]

    if six in item:
        type_list['SIX'] += item.count(six)
        return 0
    if five in item:
        type_list['FIVE'] += item.count(five)
        return 0
    if four in item:
        type_list['FOUR'] += item.count(four)
        return 0
    for i in three:
        if i in item:
            type_list['THREE'] += item.count(i)
    for i in broken_three2:
        if i in item:
            type_list['BROKEN_THREE'] += item.count(i)
    for i in broken_three1:
        if item.startswith(i):
            type_list['BROKEN_THREE'] += 1
        if item.endswith(i):
            type_list['BROKEN_THREE'] += 1

# Five(连五): 11111
# Straight Four(活四): 011110
# Four(冲四): 211110, 11101, 11011
# Three(活三): 011100, 011010
# Broken three(眠三): 211100, 211010, 210110, 11001, 10101, 2011102
# Two(活二): 001100, 011000, 001010, 010010
# Broken two(眠二): 211000, 210100, 210010, 10001, 2001102, 2010102
# One: 0010000, 010000
# Broken one: 210000, 2010002, 2001002 不考虑
