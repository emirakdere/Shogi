import os
import piece
from globalVars import BOARD_SIZE


class Board:
    """
    Class that represents the BoxShogi board
    """
    def __init__(self):
        self._board = self._initEmptyBoard()
        

    def _initEmptyBoard(self):  
        return [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    def __repr__(self):
        return self._stringifyBoard()

    def _stringifyBoard(self):
        """
        Utility function for printing the board
        """
        s = ''
        for row in range(len(self._board) - 1, -1, -1):

            s += '' + str(row + 1) + ' |'
            for col in range(0, len(self._board[row])):
                s += self._stringifySquare(self._board[col][row])

            s += os.linesep

        s += '    a  b  c  d  e' + os.linesep
        return s

    def _stringifySquare(self, sq):
        """
       	Utility function for stringifying an individual square on the board

        :param sq: Array of strings.
        """

        if sq == None:
            return '__|'
        elif len(sq.name) == 1:
            return ' ' + sq.name + '|'
        if len(sq.name) == 2:
            return sq.name + '|'
        


            
            
        
        
        
        
        