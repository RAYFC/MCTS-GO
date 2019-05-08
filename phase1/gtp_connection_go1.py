"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
from board_util import *
import gtp_connection
import numpy as np
from simple_board import *
import re

class GtpConnectionGo1(gtp_connection.GtpConnection):

    def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
        """
        GTP connection of Go1

        Parameters
        ----------
        go_engine : GoPlayer
            a program that is capable of playing go by reading GTP commands
        komi : float
            komi used for the current game
        board: GoBoard
            SIZExSIZE array representing the current board state
        """
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        self.commands["score"] = self.score_cmd
    def score_cmd(self,args):
        newboard=self.board.copy()
        newboard1=self.board.copy()
        b_score=0
        w_score =0
        points=[]
        empty_list = []
        b_t=[]
        w_t=[]
        for y in range(1,newboard.size+1,1):
            for x in range(1,newboard.size+1,1):
                point = newboard._coord_to_point(x,y)
                points.append(point)
        for p in points:
            if newboard.board[p] == EMPTY:
                list = []
                list.append(p)
                newboard.board[p]=FLOODFILL
                pointstack = [p]
                while pointstack:
                    current_point = pointstack.pop()
                    neighbors = newboard._neighbors(current_point)
                    for n in neighbors:
                        if newboard.board[n] == EMPTY:
                            list.append(n)
                            pointstack.append(n)
                            newboard.board[n] = FLOODFILL
                for i in list:
                    neighbors = newboard._neighbors(i)
                    for n in neighbors:
                        if newboard.board[n] == WHITE:
                            w_t=w_t+list
                            break
        for p in points:
            if newboard1.board[p] == EMPTY:
                list = []
                list.append(p)
                newboard1.board[p]=FLOODFILL
                pointstack = [p]
                while pointstack:
                    current_point = pointstack.pop()
                    neighbors = newboard1._neighbors(current_point)
                    for n in neighbors:
                        if newboard1.board[n] == EMPTY:
                            list.append(n)
                            pointstack.append(n)
                            newboard1.board[n] = FLOODFILL
                for i in list:
                    neighbors = newboard1._neighbors(i)
                    for n in neighbors:
                        if newboard.board[n] == BLACK:
                            b_t=b_t+list
                            break
        b_t =sorted(set(b_t))
        w_ter=[]
        b_ter=[]
        for n in w_t:
            if n not in b_t:
                w_ter.append(n)
        for n in b_t:
            if n not in w_t:
                b_ter.append(n)
        for p in points:
            if p in w_ter:
                newboard.board[p] =5
            elif p in b_ter:
                newboard.board[p] = 6
        for p in points:
            if newboard.board[p]==1 or newboard.board[p] == 6:
                 b_score +=1
            elif newboard.board[p]==2 or newboard.board[p]==5:
                w_score +=1
        w_score+=self.komi
        if b_score > w_score :
            self.respond("B+%.1f" % (b_score - w_score))
        elif w_score > b_score:
            self.respond("W+%.1f" % (w_score - b_score))
        else:
            self.respond("0")