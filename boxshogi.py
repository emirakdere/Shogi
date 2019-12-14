from piece import Piece
from board import Board
import utils
import sys

PLAYER1 = 0
PLAYER2 = 1
PLAYER1_WON_CHECKMATE = 1
PLAYER2_WON_CHECKMATE = 2
PLAYER1_WON_ILLEGAL_MOVE = 3
PLAYER2_WON_ILLEGAL_MOVE = 4

# TODO: do you need coordinates in piece object?

class Game:
    def __init__(self, buildInstructions):
        self.finished = 0
        self.numOfMoves = 0
        self.turn = PLAYER1
        self.state = Board()
        self.grave = [[], []]
        self.buildBoard(buildInstructions)

    def buildBoard(self, buildInstructions):
        for piecePositionDic in buildInstructions['initialPieces']:

            pieceStr = piecePositionDic['piece']
            positionStr = piecePositionDic['position']

            owner = pieceStr[-1].isupper() * 1
            x, y = self.translateBoardLoc(positionStr)

            pieceObject = Piece(pieceStr)

            self.state._board[x][y] = pieceObject

        for pieceStr in buildInstructions['lowerCaptures']:
            self.grave[PLAYER1].append(Piece(pieceStr))
        for pieceStr in buildInstructions['upperCaptures']:
            self.grave[PLAYER2].append(Piece(pieceStr))


    def print(self):
        print(self.state)
        print("Captures UPPER:", end="")
        for piece in self.grave[PLAYER2]:
            print(" " + piece.name, end="")
        print("")
        print("Captures lower:", end="")
        for piece in self.grave[PLAYER1]:
            print(" " + piece.name, end="")
        print("")


    def executeAction(self, action):

        actionArgv = action.split(" ")
        if actionArgv[0] == "move":
            if len(actionArgv) == 3 and actionArgv[2] == "promote":
                pass
            else:
                self.move(actionArgv[1], actionArgv[2]) #move
        elif actionArgv[0] == "drop":
            pass
        else:
            self.setIllegalMoveVariables()
            return


    def move(self, oldLoc, newLoc):

        pieceToMove = self.getPieceInLoc(oldLoc)
        pieceInDesiredLoc = self.getPieceInLoc(newLoc)
        
        if pieceToMove == None: # move nonexistent piece
            self.setIllegalMoveVariables()
            return

        ownerOfMovedPiece = pieceToMove.ownerOfPiece()

        if ownerOfMovedPiece != self.turn:
            self.setIllegalMoveVariables()
            return

        desiredLoc = tuple(self.translateBoardLoc(newLoc))
        legalMoves = self.getLegalMoves(oldLoc)
        
        if desiredLoc not in legalMoves: # move to illegal location
            self.setIllegalMoveVariables
            return
        
        # in case of a capture, move piece to the capturer's grave
        if pieceInDesiredLoc != None: 
            
            if ownerOfMovedPiece == PLAYER1:
                pieceInDesiredLoc.name = pieceInDesiredLoc.name.lower()
                self.grave[ownerOfMovedPiece].append(pieceInDesiredLoc)
            else:
                pieceInDesiredLoc.name = pieceInDesiredLoc.name.upper()
                self.grave[ownerOfMovedPiece].append(pieceInDesiredLoc)
            
        self.changeSquare(oldLoc, None)
        self.changeSquare(newLoc, pieceToMove)
        self.numOfMoves += 1
            
    def setIllegalMoveVariables(self):
        if self.turn == PLAYER1:
            self.finished = PLAYER2_WON_ILLEGAL_MOVE
        elif self.turn == PLAYER2:
            self.finished = PLAYER1_WON_ILLEGAL_MOVE
        
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
    
    def getLegalMoves(self, locOfPieceToMove):
        piece = self.getPieceInLoc(locOfPieceToMove)
        x, y = self.translateBoardLoc(locOfPieceToMove)
        legalMoves = set()

        for direction in piece.maxRange(): 
        # for instance, Up direction for Notes. I will continue 
        # expanding in the direction until I hit an obstacle
            for displacement in direction: 
                deltaX, deltaY = displacement
                newX, newY = (x + deltaX), (y + deltaY)
                if (0 <= newX <= 4) and (0 <= newY <= 4):
                    pieceInDestination = self.state._board[newX][newY]
                    if pieceInDestination == None:
                        legalMoves.add((newX, newY))
                    elif piece.isOpponentPiece(pieceInDestination):
                        legalMoves.add((newX, newY))
                        break
                    else:
                        break # move to the next direction, for instance Left
        return legalMoves




def driver(isInteractive, dicOfInitialState):
    gameBoard = Game(dicOfInitialState)
    while (not gameBoard.finished) and (gameBoard.numOfMoves < 200):

        if isInteractive:
            gameBoard.print()

        if gameBoard.turn == PLAYER1:
            action = input("lower> ")
            gameBoard.executeAction(action)
            gameBoard.turn = PLAYER2
        elif gameBoard.turn == PLAYER2:
            action = input("UPPER> ")
            gameBoard.executeAction(action)
            gameBoard.turn = PLAYER1



def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == "-i":

            initialBoardState = {'initialPieces': [\
                                    {'piece': 'd', 'position': 'a1'}, \
                                    {'piece': 'p', 'position': 'a2'}, \
                                    {'piece': 's', 'position': 'b1'}, \
                                    {'piece': 'r', 'position': 'c1'}, \
                                    {'piece': 'g', 'position': 'd1'}, \
                                    {'piece': 'n', 'position': 'e1'}, \
                                    {'piece': 'D', 'position': 'e5'}, \
                                    {'piece': 'P', 'position': 'e4'}, \
                                    {'piece': 'S', 'position': 'd5'}, \
                                    {'piece': 'R', 'position': 'c5'}, \
                                    {'piece': 'G', 'position': 'b5'}, \
                                    {'piece': 'N', 'position': 'a5'}], \
                                    'upperCaptures': [], 'lowerCaptures': []}

            driver(True, initialBoardState)
            gameBoard.print()   

            
    elif len(sys.argv) == 3:
        if sys.argv[1] == "-f":
            testCase = utils.parseTestCase(sys.argv[2])
            
            driver(False, testCase)
            gameBoard.print()

    else:
        raise Exception("Invalid game mode specification.")


    if gameBoard.finished == PLAYER2_WON_CHECKMATE:
        print("UPPER player wins. Checkmate.")
    elif gameBoard.finished == PLAYER1_WON_CHECKMATE:
        print("lower player wins. Checkmate.")
    elif gameBoard.finished == PLAYER2_WON_ILLEGAL_MOVE:
        print("UPPER player wins. Illegal move.")
    elif gameBoard.finished == PLAYER1_WON_ILLEGAL_MOVE:
        print("lower player wins. Illegal move.")
    else:
        print("Tie game. Too many moves.")



if __name__ == "__main__":
    main()

