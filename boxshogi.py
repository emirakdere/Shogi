from piece import Piece
from board import Board
import utils
import sys

LOWER = 0
UPPER = 1
MOVE = 0
DROP = 1
NO_CHECKMATE = 0
LOWER_WON_CHECKMATE = 1
UPPER_WON_CHECKMATE = 2
LOWER_WON_ILLEGAL_MOVE = 3
UPPER_WON_ILLEGAL_MOVE = 4



promotionZones = {UPPER:{"a1", "b1", "c1", "d1", "e1"}, \
                  LOWER:{"a5", "b5", "c5", "d5", "e5"}}

class Game:
    def __init__(self, buildInstructions):
        self.finished = 0
        self.numOfMoves = 0
        self.turn = LOWER
        self.state = Board()
        self.grave = [[], []]
        self.buildBoard(buildInstructions)

    def buildBoard(self, buildInstructions):
        for piecePositionDic in buildInstructions['initialPieces']:

            pieceStr = piecePositionDic['piece']
            positionStr = piecePositionDic['position']

            x, y = self.translateBoardLoc(positionStr)

            pieceObject = Piece(pieceStr)

            self.state._board[x][y] = pieceObject

        for pieceStr in buildInstructions['lowerCaptures']:
            self.grave[LOWER].append(Piece(pieceStr))
        for pieceStr in buildInstructions['upperCaptures']:
            self.grave[UPPER].append(Piece(pieceStr))


    def print(self):
        #print("") # TODO: DELETE THIS!!!!!!!!!!
        print(self.state)
        print("Captures UPPER:", end="")
        for piece in self.grave[UPPER]:
            print(" " + piece.name, end="")
        print("")
        print("Captures lower:", end="")
        for piece in self.grave[LOWER]:
            print(" " + piece.name, end="")
        print("")


    def executeAction(self, action):

        actionArgv = action.split(" ")
        if actionArgv[0] == "move":
            if len(actionArgv) == 4 and actionArgv[3] == "promote":
                self.move(actionArgv[1], actionArgv[2], True)
            else:
                self.move(actionArgv[1], actionArgv[2], False) #move
        elif actionArgv[0] == "drop":
            self.drop(actionArgv[1], actionArgv[2])
        else:
            self.setIllegalMoveVariables()
            return
    def getActionsWhenChecked(self):
        possibleActions = []
        currPlayersPieces = "DNGSRP" if self.turn == UPPER else "dngsrp"
        # MOVE and DROP
        for char in "abcde":
            for num in "12345":
                pieceInSquare = self.getPieceInLoc(char + num)
                if pieceInSquare != None:
                    if pieceInSquare.name in currPlayersPieces:
                        legalMoves = self.getLegalMoves(char + num)
                        for move in legalMoves:
                            moveAsStr = self.translateArrayIndex(move)
                            if not self.inCheckAfterAction(MOVE, [char + num, moveAsStr]):
                                possibleActions.append("move " + char + num + " " + moveAsStr)
        for capturedPiece in self.grave[self.turn]:
            legalDrops = self.getLegalDrops(capturedPiece.name)
            for drop in legalDrops:
                dropAsStr = self.translateArrayIndex(drop)
                if not self.inCheckAfterAction(DROP, [capturedPiece.name, char + num]):
                    possibleActions.append("drop " + capturedPiece.name.lower() + " " + dropAsStr)

        #print(possibleActions)
        return possibleActions






    def move(self, oldLoc, newLoc, promote):

        pieceToMove = self.getPieceInLoc(oldLoc)
        pieceInDesiredLoc = self.getPieceInLoc(newLoc)
        
        if pieceToMove == None: # move nonexistent piece
            #print(1)
            self.setIllegalMoveVariables()
            return

        ownerOfMovedPiece = pieceToMove.ownerOfPiece()

        if ownerOfMovedPiece != self.turn:
            #print(2)
            self.setIllegalMoveVariables()
            return

        desiredLoc = tuple(self.translateBoardLoc(newLoc))
        legalMoves = self.getLegalMoves(oldLoc)
        
        if desiredLoc not in legalMoves: # move to illegal location
            #print(3)
            self.setIllegalMoveVariables()
            return


        # PROMOTION
        mvmtInvolvingPromotionZone = (newLoc in promotionZones[self.turn] or oldLoc in promotionZones[self.turn])
        if promote:
            if pieceToMove.name[0] != "+" and \
               mvmtInvolvingPromotionZone and \
               pieceToMove.name.upper() != "D" and pieceToMove.name.upper() != "S":

                pieceToMove.name = "+" + pieceToMove.name
            else:
                #print(4)
                self.setIllegalMoveVariables()
                return

        # have to promote P if moved into the zone
        elif pieceToMove.name.upper() == "P" and mvmtInvolvingPromotionZone: 
            pieceToMove.name = "+" + pieceToMove.name


        
        # in case of a capture, move piece to the capturer's grave
        if pieceInDesiredLoc != None: 
            
            if self.turn == LOWER:
                pieceInDesiredLoc.name = pieceInDesiredLoc.name[-1].lower()
                self.grave[self.turn].append(pieceInDesiredLoc)
            else:
                pieceInDesiredLoc.name = pieceInDesiredLoc.name[-1].upper()
                self.grave[self.turn].append(pieceInDesiredLoc)


        self.changeSquare(oldLoc, None)
        self.changeSquare(newLoc, pieceToMove)
        self.numOfMoves += 1
            


    def drop(self, pieceChar, locStr):
        

        pieceChar = pieceChar.upper() if self.turn == UPPER else pieceChar

        # dropping piece that you have not captured
        matchingPiecesInGrave = list(filter(lambda elt: elt.name == pieceChar, self.grave[self.turn]))
        if matchingPiecesInGrave == []: # CHECK THIS
            #print(5)
            self.setIllegalMoveVariables()
            return
        legalDrops = self.getLegalDrops(pieceChar)
        desiredLoc = tuple(self.translateBoardLoc(locStr))
        if desiredLoc not in legalDrops:
            #print(6)
            self.setIllegalMoveVariables()
            return
        else:
            pieceToDrop = matchingPiecesInGrave[0]
            self.changeSquare(locStr, pieceToDrop)
            self.grave[self.turn].remove(pieceToDrop)



    def setIllegalMoveVariables(self):
        if self.turn == LOWER:
            self.finished = UPPER_WON_ILLEGAL_MOVE
        elif self.turn == UPPER:
            self.finished = LOWER_WON_ILLEGAL_MOVE
        
    def translateBoardLoc(self, charNum): 
    #translates the board location (i.e. 5e) into array-index format
        char, num = charNum
        y = int(num) - 1
        x = ord(char) - ord("a")
        return [x, y]

    def translateArrayIndex(self, coordinate):
        x, y = coordinate
        return "abcde"[x] + "12345"[y]
        
    
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

    def inCheckAfterAction(self, action, arguments):

        # I don't have to consider promoting
        checkAfterAction = False

        if action == MOVE:
            startLoc, endLoc = arguments
            pieceToMove = self.getPieceInLoc(startLoc)
            pieceInDestination = self.getPieceInLoc(endLoc)

            # temporarily change board state to simulate action and check for check
            self.changeSquare(startLoc, None)
            self.changeSquare(endLoc, pieceToMove)

            checkAfterAction = self.check(self.turn)

            # UNDO the temporary changes above
            self.changeSquare(endLoc, pieceInDestination)
            self.changeSquare(startLoc, pieceToMove)

        elif action == DROP:
            pieceChar, endLoc = arguments

            # temporarily change board state to simulate action and check for check
            self.changeSquare(endLoc, Piece(pieceChar))

            checkAfterAction = self.check(self.turn)

            # UNDO the temporary change above
            self.changeSquare(endLoc, None)

        return checkAfterAction

    def findColumnWithP(self):
        columnWithP = -1
        for x in range(5):
            for y in range(5):
                pieceInSquare = self.state._board[x][y]
                if pieceInSquare != None and pieceInSquare.name[-1] == "pP"[self.turn]: # p if LOWER, P if UPPER
                    columnWithP = x
        return columnWithP

    def getLegalDrops(self, pieceChar):

        legalDrops = set()
        columnWithP = self.findColumnWithP()

        for x in range(5):
            for y in range(5):
                pieceInSquare = self.state._board[x][y]
                if pieceInSquare == None:
                    if pieceChar.upper() == "P":

                        droppingPInPromotionZone = self.translateArrayIndex((x, y)) in promotionZones[self.turn]
                        droppingPResultsInCheckmate = self.inCheckAfterAction(DROP, [pieceChar, self.translateArrayIndex((x, y))]) != False
                        otherPInColumn = columnWithP == x

                        if not (droppingPInPromotionZone or droppingPResultsInCheckmate or otherPInColumn):
                            legalDrops.add((x, y))

                    else:
                        legalDrops.add((x, y))

        return legalDrops


    def check(self, player):
        controledAndDriveLocs = self.allControlledSquares()
        if controledAndDriveLocs[player + 2] in controledAndDriveLocs[player]:
            return True # TODO
        else:
            return False



    def allControlledSquares(self):
        lowerControls = set()
        upperControls = set()
        lowerDLocation = None
        upperDLocation = None
        for char in "abcde":
            for num in "12345":
                piece = self.getPieceInLoc(char + num)
                if piece != None:

                    if piece.name[-1].islower():
                        lowerControls |= self.getLegalMoves(char + num)
                        if piece.name == "d":
                            lowerDLocation = tuple(self.translateBoardLoc(char + num))
                    else:
                        upperControls |= self.getLegalMoves(char + num)
                        if piece.name == "D":
                            upperDLocation = tuple(self.translateBoardLoc(char + num))
        return [upperControls, lowerControls, lowerDLocation, upperDLocation]



def driver(isInteractive, dicOfInitialState):
    gameBoard = Game(dicOfInitialState)
    while (not gameBoard.finished) and (gameBoard.numOfMoves < 200):
        possibleActions = []

        if isInteractive:
            gameBoard.print()

        if gameBoard.turn == LOWER:
            lowerInCheck = gameBoard.check(LOWER)
            if lowerInCheck:
                if possibleActions != []:
                    possibleActions = gameBoard.getActionsWhenChecked()
                    print("lower player is in check!")
                    print("Available moves:")
                    for act in possibleActions:
                        print(act)
                else:
                    gameBoard.finished == UPPER_WON_CHECKMATE
                    break
            action = input("lower> ")
            if lowerInCheck:
                if action not in possibleActions:
                    gameBoard.finished = UPPER_WON_ILLEGAL_MOVE
                    break
            gameBoard.executeAction(action)
            gameBoard.turn = UPPER
        elif gameBoard.turn == UPPER:
            upperInCheck = gameBoard.check(UPPER)
            if upperInCheck:
                possibleActions = gameBoard.getActionsWhenChecked()
                if possibleActions != []:
                    possibleActions = gameBoard.getActionsWhenChecked()
                    print("UPPER player is in check!")
                    print("Available moves:")
                    for act in possibleActions:
                        print(act)
                else:
                    gameBoard.finished == LOWER_WON_CHECKMATE
                    break
            action = input("UPPER> ")
            if upperInCheck:
                if action not in possibleActions:
                    #print(8)
                    gameBoard.finished = LOWER_WON_ILLEGAL_MOVE
                    break
            gameBoard.executeAction(action)
            gameBoard.turn = LOWER

    if gameBoard.finished == UPPER_WON_CHECKMATE:
        print("UPPER player wins. Checkmate.")
    elif gameBoard.finished == LOWER_WON_CHECKMATE:
        print("lower player wins. Checkmate.")
    elif gameBoard.finished == UPPER_WON_ILLEGAL_MOVE:
        print("UPPER player wins. Illegal move.")
    elif gameBoard.finished == LOWER_WON_ILLEGAL_MOVE:
        print("lower player wins. Illegal move.")
    else:
        print("Tie game. Too many moves.")


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
            #gameBoard.print()   

            
    elif len(sys.argv) == 3:
        if sys.argv[1] == "-f":
            testCase = utils.parseTestCase(sys.argv[2])
            
            driver(False, testCase)
            #gameBoard.print()

    else:
        raise Exception("Invalid game mode specification.")





if __name__ == "__main__":
    main()

