"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import gtp_connection
import numpy as np
import re
import time
import random


# from alphabeta import callAlphabetaDL

class GtpConnectionGo2(gtp_connection.GtpConnection):
    def __init__(self, go_engine, board, outfile='gtp_log', debug_mode=False):
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
        self.number=0
        self.start=None
        self.timelimit = 1
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        self.commands["go_safe"] = self.safety_cmd
        self.argmap["go_safe"] = (1, 'Usage: go_safe {w,b}')
        self.commands["solve"] = self.solve_cmd
        self.commands["timelimit"]=self.timelimit_cmd

    def safety_cmd(self, args):
        try:
            color = GoBoardUtil.color_to_int(args[0].lower())
            safety_list = self.board.find_safety(color)
            safety_points = []
            for point in safety_list:
                x, y = self.board._point_to_coord(point)
                safety_points.append(GoBoardUtil.format_point((x, y)))
            self.respond(safety_points)
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))

    def timelimit_cmd(self, args):
        self.timelimit = int(args[0])
        self.respond()

    def solve_cmd(self, args):
        self.move=[]
        self.start=time.process_time()
        self.time=False
        win = self.negamaxBoolean(0)
        if self.time:
            self.respond("unknown")
            return False
        elif win :
            self.respond(GoBoardUtil.int_to_color(self.board.current_player) + ' ' + GoBoardUtil.format_point(self.board._point_to_coord(self.move[0])))
            return True
        else:
            self.respond(GoBoardUtil.int_to_color(GoBoardUtil.opponent(self.board.current_player)))
    def negamaxBoolean(self,depth):
        duration=time.process_time() - self.start
        if duration > self.timelimit:
            self.time=True
            return True
        elif self.board.end_of_game():
            self.board.winner=self.board.score(self.go_engine.komi)[0]
            if self.board.winner==self.board.current_player:
                return True
            else:
                return False
        else:
            moves=legalmoves(self.board,self.board.current_player)
            if len(moves)==0:
                moves=[None]
            for m in moves:
                self.board.move(m,self.board.current_player)
                success = not self.negamaxBoolean(depth+1)
                self.board.undo_move()
                if success:
                    if depth==0:
                        self.move.append(m)
                    return True
                else:
                    continue
            return False

    def return_moves(self):
        self.time = False
        win = self.negamaxBoolean(0)
        if self.time:
            return GoBoardUtil.generate_random_move(self.board,self.board.current_player,True)
        elif win:
            self.board.move(self.move[0], self.board.current_player)
        else:
            return GoBoardUtil.generate_random_move(self.board, self.board.current_player, True)

def legalmoves(board,color):
    moves = board.get_empty_points()
    num_moves = len(moves)
    illegal_moves = []

    for i in range(num_moves):
        if board.check_legal(moves[i],color) and not board.is_eye(moves[i],color):
            continue
        else:
            illegal_moves.append(i)
    legal_move = np.delete(moves,illegal_moves)
    return legal_move


