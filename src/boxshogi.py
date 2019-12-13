from piece import Piece
from board import Board

PLAYER1 = 0
PLAYER2 = 1

class Game:
    def __init__(self):
        self.state = Board()
        self.pieces = [set(), set()]
        self.grave = [set(), set()]
        self._firstConfig()

    
    def _firstConfig(self):
        for i, p in enumerate("dsrgn"):
            pieceObject = Piece(p, [i, 0], PLAYER1)
            self.pieces[PLAYER1].add(pieceObject)
            self.state._board[i][0] = pieceObject
            
            pieceObject = Piece(p.upper(), [4 - i, 4], PLAYER2)
            self.pieces[PLAYER2].add(pieceObject)
            self.state._board[4 - i][4] = pieceObject
        
        pieceObject = Piece("p", [0, 1], PLAYER1)
        self.pieces[PLAYER1].add(pieceObject)
        self.state._board[0][1] = pieceObject
        
        pieceObject = Piece("P", [4, 3], PLAYER2)
        self.pieces[PLAYER2].add(pieceObject)
        self.state._board[4][3] = pieceObject
    
            
    def move(self, oldLoc, newLoc):
        pieceToMove = self.getPieceInLoc(oldLoc)
        pieceInDesiredLoc = self.getPieceInLoc(newLoc)
        
        if pieceToMove == None: # move nonexistent piece
            raise Exception("No piece to be moved")
        
        # I actually want to abstract this further, 
        # I don't ever want to use translateBoardLoc
        desiredLoc = self.translateBoardLoc(newLoc)
        legalMoves = self.getLegalMoves(pieceToMove)
        
        if desiredLoc not in legalMoves: # move to illegal location
            raise Exception("Illegal move")
        
        # in case of a capture, move piece to the original owner's grave
        if pieceInDesiredLoc != None: 
            self.grave[pieceInDesiredLoc.originalOwner].add(pieceInDesiredLoc)
            
        self.changeSquare(oldLoc, None)
        self.changeSquare(newLoc, pieceToMove)
            
        
    
    
    def translateBoardLoc(self, charNum): 
    #translates the board location (i.e. 5 e) into array-index format
        char, num = charNum
        y = int(num) - 1
        x = ord(char) - ord("a")
        return [x, y]
    
    def getPieceInLoc(self, charNum):
        x, y = self.translateBoardLoc(charNum)
        return self.state._board[x][y]
    
    def changeSquare(self, charNum, newPiece):
        x, y = self.translateBoardLoc(charNum)
        self.state._board[x][y] = newPiece
    
    def getLegalMoves(self, pieceToMove):
        return [[0, 2]]
        pass #return set of all legal moves


gameBoard = Game()
gameBoard.move("a2", "a3")

print(gameBoard.state)









