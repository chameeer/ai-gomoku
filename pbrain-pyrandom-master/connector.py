import random
import time
import copy
import sys
import pisqpipe as pp
import math
from pisqpipe import DEBUG_EVAL, DEBUG
from Board import Board
from CriticNetwork import CriticNetwork
import pickle
import os
# from HMCTS import HMCTS_value
# from UCT import UCT
# sys.setrecursionlimit(100)

pp.infotext = 'name="pbrain-MCTS-ADP", author="xm", version="1.0", country="SH, China", www="https://github.com/stranskyjan/pbrain-pyrandom"'


## ADP部分，要调用一些外置py文件
from Board import Board
from CriticNetwork import CriticNetwork
import pickle

MAX_BOARD = 20
board = Board(MAX_BOARD)
critic_network = CriticNetwork(params=[len(board.features)*5 + 2, 60, 1], pattern_finder=board.pattern_finder)

# 读取之前训练好的layer
critic_network.layers = pickle.load(open(r"C:\Users\XMiPh\Desktop\ai-gomoku18\ai-gomoku\pbrain-pyrandom-master\critic_network_big", 'rb'))
adjacent = []  # 邻近1格的空点

# 下面是一个使用的例子

'''
data = {}
availables = Adjacent(board) # 选取邻近的点
for move in availables:  # 遍历代入神经网络计算选择胜率最高的着法
    board_copy = copy.deepcopy(board)
    board_copy[move[0]][move[1]] = 1
    data[move] = critic_network.forward(board_copy) # forward方法返回的是一个数值
sorted_data = sorted(data.items(), key = lambda item:item[1], reverse = True) # 按照value大小排序，从大到小
move, win_prob = sorted_data[0]
x, y = move # 给出下一步位移

'''

###############################################
# Basic function 可以不用看
def check_board(board):
    for i in range(MAX_BOARD):
        for j in range(MAX_BOARD):
            if isFree(i,j) != 1:
                return False
    return True

def isCrossing(x, y):
    return x < 0 or y < 0 or x >= pp.width or y >= pp.height

def oppsite_who(who):
    if who == 1:
        return 2
    if who == 2:
        return 1

def check_win(board, x, y, who):
    # row
    left = 0
    right = 0
    while x-left-1 >= 0 and board[x-left-1][y] == who:
        left += 1
    while x+right+1 < MAX_BOARD and board[x+right+1][y] == who:
        right += 1
    if right + left + 1 >= 5:
        return True
    
    # col
    down = 0
    up = 0
    while y-down-1 >= 0 and board[x][y-down-1] == who:
        down += 1
    while y+up+1 < MAX_BOARD and board[x][y+up+1] == who:
        up += 1
    if up + down + 1 >= 5:
        return True

    # 主对角线
    upperLeft = 0
    lowerRight = 0
    while x-upperLeft-1 >= 0 and y+upperLeft+1 < MAX_BOARD and board[x-upperLeft-1][y+upperLeft+1] == who:
        upperLeft += 1
    while x+lowerRight+1 < MAX_BOARD and y-lowerRight-1 >= 0 and board[x+lowerRight+1][y-lowerRight-1] == who:
        lowerRight += 1
    if lowerRight + upperLeft + 1 >= 5:
        return True

    # 次对角线
    lowerLeft = 0
    upperRight = 0
    while x-lowerLeft-1 >= 0 and y-lowerLeft-1 >= 0 and board[x-lowerLeft-1][y-lowerLeft-1] == who:
        lowerLeft += 1
    while x+upperRight+1 < MAX_BOARD and y+upperRight+1 < MAX_BOARD and board[x+upperRight+1][y+upperRight+1] == who:
        upperRight += 1
    if upperRight + lowerLeft + 1 >= 5:
        return True
    
    return False

###############################################
# Heuristic function

# def HMCT_heuristic(board, x, y):
#     return HMCTS_value(board, (x, y))

# def confront_heuristic(board, x, y, who): 
#     """The function calculate the confront_heuristic after adding an adjacent point"""
#     """delete each old heuristic value in 8 directions"""
    
#     beta = 1/6
    
#     # return beta * my_heuristic(board, x, y, who) + (1-beta) * my_heuristic(board, x, y, oppsite_who(who))/10
    

#     #log('Calculate heuristic at coordinate (%s, %s) for %s'% (x, y, 'ME' if who==1 else 'OPPONENT'))
#     board[x][y] = who
#     ADP_heuristic = critic_network.forward(board)
#     if who == 2:
#         ADP_heuristic = 1 - ADP_heuristic
#     ADP_heuristic *= 1000
#     board[x][y] = 0
#     return beta * ADP_heuristic + (1 - beta) * HMCT_heuristic(board, x, y, who)



###############################################
# Adjacent function

def Adjacent(board):
    """It is a function for choosing the adjacent free point of full point in the board"""   
    adjacent = []
    for x in range(MAX_BOARD):
        for y in range(MAX_BOARD):
            if isFree(x, y):
                tag = 0
                for i in range(-2, 3, 1):
                    for j in range(-2, 3, 1):
                        if isCrossing(x+i,y+j):
                            continue
                        if isFree(x+i,y+j):
                            continue
                        else:
                            tag = 1
                if tag == 1:
                    adjacent.append((x,y))                      
    #logDebug('adjacents: '+str(adjacent))  
    return adjacent

def Adjacent_1(board, old_adjacent, x, y):
    """It is a function for choosing the 1 point adjacent free points of full point in the board"""   
    adjacent = []
    adjacent = old_adjacent
    adjacent.remove((x,y))
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            if isFree(x+i,y+j):
                if isCrossing(x+i,y+j):
                    continue
                if (x+i,y+j) in adjacent:
                    continue
                else:
                    adjacent.append((x+i,y+j))
            else:
                continue                           
    return adjacent

def Adjacent_2(board, old_adjacent, x, y):
    """It is a function for choosing the 2 point adjacent free points of full point in the board"""   
    adjacent = []
    adjacent = old_adjacent
    adjacent.remove((x,y))
    for i in range(-2, 3, 1):
        for j in range(-2, 3, 1):
            if isFree(x+i,y+j):
                if isCrossing(x+i,y+j):
                    continue
                if (x+i,y+j) in adjacent:
                    continue
                else:
                    adjacent.append((x+i,y+j))
            else:
                continue                           
    return adjacent

# def Pruning_Adjacent(board, adjacent, who):  #  现在取的是前4的点
#     """It is a function for choosing the adjacent free point of full point in the board"""   
#     Pruning_Adjacent = []
#     score = {}
#     for (x,y) in adjacent:
#         score[(x,y)] = confront_heuristic(board, x, y, who)
#     rank = sorted(score.items(), key = lambda item:item[1], reverse = True)
#     for i in range(0, 4):
#         Pruning_Adjacent.append(rank[i][0])
#     return Pruning_Adjacent

# def Simulate_Pruning_Adjacent(board, adjacent, who):  #  现在取的是前2的点
#     """It is a function for choosing the adjacent free point of full point in the board"""   
#     Pruning_Adjacent = []
#     score = {}
#     for (x,y) in adjacent:
#         score[(x,y)] = confront_heuristic(board, x, y, who)
#     rank = sorted(score.items(), key = lambda item:item[1], reverse = True)
#     for i in range(0, 2):
#         Pruning_Adjacent.append(rank[i][0])
#     return Pruning_Adjacent




###############################################
# Orginal Function 
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

def brain_turn():
    if pp.terminateAI:
        return
    i = 0
    while True:
        global board
        global adjacent
        if check_board(board):
            x = int(pp.width/2)
            y = int(pp.height/2)
        else:
            
            # play_turn = [1,2]
            # UCT = MCTS_UCT(board, play_turn, time=30, max_actions=7)
            # move = UCT.get_action()
            
            data = {}
            availables = Adjacent_1(board)
            for move in availables:  # 选择胜率最高的着法
            # data[move] = (self.wins.get((1, move), 0) /
            # self.plays.get((1, move), 1)) + confront_heuristic(board, move[0], move[1], 1)/1000
                board_copy = copy.deepcopy(board)
                board_copy[move[0]][move[1]] = 1
                data[move] = critic_network.forward(board_copy)
            sorted_data = sorted(data.items(), key = lambda item:item[1], reverse = True)
            
            # after_MCTS_data = {}
            # for i in range(0,4):
            #     move, win_probability = sorted_data[i]
            #     # after_MCTS_data[move] = HMCT_heuristic(board, move[0], move[1])
            #     after_MCTS_data[move] = UCT(board, move)
            # sorted_after_MCTS_data = sorted(after_MCTS_data.items(), key = lambda item:item[1], reverse = True)
            # final_move, win_prob = sorted_after_MCTS_data[0]
            # final_move, win_prob = sorted_data[0]
            x, y = random.randint(0, 20), random.randint(0, 20)
            # x, y = final_move
        # logDebug((x,y))
        # heuristic = confront_heuristic(board, x, y, 1)
        # logDebug(my_heuristic(board, x, y, 1))
        # logDebug(opponents_heuristic(board, x, y, 1))
        # logDebug(heuristic)
        i += 1
        if pp.terminateAI:
            return
        if isFree(x,y):
            break
    if i > 1:
        pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
    pp.do_mymove(x, y)

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
pp.brain_turn = brain_turn 
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval

def main():
	pp.main()

if __name__ == "__main__":
	main()

