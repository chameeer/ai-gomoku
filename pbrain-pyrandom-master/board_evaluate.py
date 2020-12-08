# functions to evaluate a given board by calculating types * score
# usage: evaluate(board)

# functions to count the number of different types
# usage: board_type_count(board, turn, attack = True)
# parameters:
#   board:
#           the board to count types
#   turn:
#           'my' or 'opponent', decide to count types for which player
#   attack:
#           default True.
#           If False, count the types for pre_process

import pisqpipe as pp
import copy

# scores of different types
FIVE = 20000000
FOUR = 100000
BROKEN_FOUR = 1000
THREE = 1000
BROKEN_THREE = 50
TWO = 50
BROKEN_TWO = 5

# type-score dict
scores = {'FIVE': FIVE, 'FOUR': FOUR, 'BROKEN_FOUR': BROKEN_FOUR, 'THREE': THREE,
          'BROKEN_THREE': BROKEN_THREE, 'TWO': TWO, 'BROKEN_TWO': BROKEN_TWO}


# function to evaluate the board
def evaluate(board):
    type_my = board_type_count(board, 'my')  # count the number of types for 'my'
    type_opponent = board_type_count(board, 'opponent')  # count the number of types for 'opponent'
    value = type_value(type_my) - type_value(type_opponent) * 10  # calculate the final value
    return value


# function to calculate the whole value of given type list
def type_value(types):
    value = 0
    for type, num in types.items():
        value += num * scores[type]
    # it is a winning type if there exists two 'broken four' or 'three' like a 'four'
    special_type = types['BROKEN_FOUR'] + types['THREE']
    if special_type >= 2:
        value += scores['FOUR'] * (special_type - 1)
    return value


# function to count the number of types of a given board
# parameters:
#   board:
#           the board to count types
#   turn:
#           'my' or 'opponent', decide to count types for which player
#   attack:
#           Default True.
#           If False, count the types for pre_process
def board_type_count(board, turn, attack=True):
    height = pp.height
    width = pp.width
    if turn == 'my':
        M = 1
        P = 2
    else:
        M = 2
        P = 1
    types = {'FIVE': 0, 'FOUR': 0, 'BROKEN_FOUR': 0, 'THREE': 0, 'BROKEN_THREE': 0, 'TWO': 0, 'BROKEN_TWO': 0}
    item_list = list()

    # search types in row
    for y in range(height):
        row = list()
        for x in range(width):
            row.append(board[x][y])
        if row.count(M) == 0:
            continue
        # get the items containing '1' and '0' by splitting '2'
        items = str(row)[1:-1].replace(', ', '').split(str(P))
        item_list = item_list + items

    # search types in column
    for x in range(width):
        column = list()
        for y in range(height):
            column.append(board[x][y])
        if column.count(M) == 0:
            continue
        # get the items containing '1' and '0' by splitting '2'
        items = str(column)[1:-1].replace(', ', '').split(str(P))
        item_list = item_list + items

    # search types from lower_right to top_left
    for k in range(4, width):
        row = list()
        for i in range(k + 1):
            row.append(board[k - i][i])
        if row.count(M) == 0:
            continue
        # get the items containing '1' and '0' by splitting '2'
        items = str(row)[1:-1].replace(', ', '').split(str(P))
        item_list = item_list + items
    for k in range(width, 2 * width - 5):
        row = list()
        for i in range(2 * width - k - 1):
            row.append(board[width - 1 - i][k - width + 1 + i])
        if row.count(M) == 0:
            continue
        # get the items containing '1' and '0' by splitting '2'
        items = str(row)[1:-1].replace(', ', '').split(str(P))
        item_list = item_list + items

    # search types from lower_left to top_right
    for k in range(0, width - 4):
        row = list()
        for i in range(width - k):
            row.append(board[i + k][i])
        if row.count(M) == 0:
            continue
        # get the items containing '1' and '0' by splitting '2'
        items = str(row)[1:-1].replace(', ', '').split(str(P))
        item_list = item_list + items
    for k in range(1, width - 4):
        row = list()
        for i in range(width - k):
            row.append(board[i][i + k])
        if row.count(M) == 0:
            continue
        # get the items containing '1' and '0' by splitting '2'
        items = str(row)[1:-1].replace(', ', '').split(str(P))
        item_list = item_list + items

    for item in item_list:
        if len(item) < 5 or item.count(str(M)) <= 1:
            continue
        else:
            if attack:
                item_type_count(item, str(M), types)  # count all types
            else:
                item_type_easy_count(item, str(M), types)  # only count 'five' and 'four'
    return types


# only count the number of types: five, four, three, broken four
def item_type_easy_count(item, my, type_list):
    if my == '1':
        five = '11111'
        four = '011110'
        broken_four = ['11101', '10111', '11011', '11110', '01111']
        three = ['011100', '001110', '011010', '010110']
    else:
        five = '22222'
        four = '022220'
        broken_four = ['22202', '20222', '22022', '22220', '02222']
        three = ['022200', '002220', '022020', '020220']

    if five in item:
        type_list['FIVE'] += 1
    if four in item:
        type_list['FOUR'] += 1
    for i in three:
        if i in item:
            type_list['BROKEN_FOUR'] += 1
    for i in broken_four:
        if i in item:
            type_list['THREE'] += 1


# count the number of types of a given item
# parameter:
#   item:
#           a sequence containing '1' and '0'
#   my:
#          '1'(my) or '2'(opponent)
#   type_list:
#           store the number of different types
def item_type_count(item, my, type_list):
    length = len(item)
    num = item.count(my)
    left_flag = False  # If left_flag is True, then the item begins with 'my', otherwise with '0'
    right_flag = False  # If right_flag is True, then the item ends with 'my', otherwise with '0'
    if item.startswith(my):
        left_flag = True
    if item.endswith(my):
        right_flag = True
    strip_item = item.strip('0')

    # count the number of types for items containing two 'my'
    if num == 2:
        if length == 5:
            type_list['BROKEN_TWO'] += 1
        else:
            if len(strip_item) <= 5:
                if left_flag or right_flag:
                    type_list['BROKEN_TWO'] += 1
                else:
                    type_list['TWO'] += 1

    # count the number of types for items containing three 'my'
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
                    type_list['BROKEN_TWO'] += 1
                elif left_flag:
                    if item[:5].count(my) == 1:
                        type_list['TWO'] += 1
                    else:
                        type_list['BROKEN_TWO'] += 1
                elif right_flag:
                    if item[-5:].count(my) == 1:
                        type_list['TWO'] += 1
                    else:
                        type_list['BROKEN_TWO'] += 1
                else:
                    type_list['TWO'] += 1
            else:
                if item[:5].count(my) == 2:
                    if left_flag:
                        type_list['BROKEN_TWO'] += 1
                    else:
                        type_list['TWO'] += 1
                if item[-5:].count(my) == 2:
                    if right_flag:
                        type_list['BROKEN_TWO'] += 1
                    else:
                        type_list['TWO'] += 1

    # count the number of types for items containing four 'my'
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

    # count the number of types for items containing five 'my'
    if num == 5:
        if length == 5:
            type_list['FIVE'] += 1
        else:
            if len(strip_item) == 5:
                type_list['FIVE'] += 1
            else:
                long_item_type_count(item, my, type_list)

    # count the number of types for items containing six 'my'
    if num >= 6:
        long_item_type_count(item, my, type_list)


# count the type number of items whose length is more than 5, begin and end with 'my' and have more than 3 'my'
# such case seldom happens, so we list all the possible types
def long_item_type_count(item, my, type_list):
    if my == '1':
        five = '11111'
        four = '011110'
        broken_four = ['11101', '10111', '11011', '11110', '01111']
        three = ['011100', '001110', '011010', '010110']
        broken_three = ['11100', '00111', '11010', '01011', '10110', '01101', '11001', '10011', '10101']
        two = ['001100', '011000', '000110', '001010', '010100', '010010']
        broken_two = ['11000', '00011', '10100', '00101', '10001']
    else:
        five = '22222'
        four = '022220'
        broken_four = ['22202', '20222', '22022', '22220', '02222']
        three = ['022200', '002220', '022020', '020220']
        broken_three = ['22200', '00222', '22020', '02022', '20220', '02202', '22002', '20022', '20202']
        two = ['002200', '022000', '000220', '002020', '020200', '020020']
        broken_two = ['22000', '00022', '20200', '00202', '20002']

    if five in item:
        type_list['FIVE'] += item.count(five)
    if four in item:
        type_list['FOUR'] += item.count(four)
    for i in broken_four:
        if i in item:
            type_list['BROKEN_FOUR'] += item.count(i)
    for i in three:
        if i in item:
            type_list['THREE'] += item.count(i)
    for i in broken_three:
        if i in item:
            type_list['BROKEN_THREE'] += item.count(i)
    for i in two:
        if i in item:
            type_list['TWO'] += item.count(i)
    for i in broken_two:
        if i in item:
            type_list['BROKEN_TWO'] += item.count(i)
