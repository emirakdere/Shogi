from piece import Piece
from board import Board
from globalVars import *

# Class built for the communication of Board and Piece classes.
class Game:
    def __init__(self, buildInstructions):
        self.finished = NO_CHECKMATE
        self.numOfMoves = 0
        self.turn = LOWER
        self.state = Board()
        self.captured = [[], []]
        self.prevMove = None
        self.buildBoard(buildInstructions)

    def buildBoard(self, buildInstructions):
        # INPUT: a dictionary parsed by util.py (or an analogous variant)
        for piecePositionDic in buildInstructions['initialPieces']:

            pieceStr = piecePositionDic['piece']
            positionStr = piecePositionDic['position']

            x, y = self.translateBoardLoc(positionStr)

            pieceObject = Piece(pieceStr)

            self.state._board[x][y] = pieceObject

        for pieceStr in buildInstructions['lowerCaptures']:
            self.captured[LOWER].append(Piece(pieceStr))
        for pieceStr in buildInstructions['upperCaptures']:
            self.captured[UPPER].append(Piece(pieceStr))


    def print(self):
        # print relevant board state to be read by the player
        print(self.state.__repr__())
        print("Captures UPPER:", end='')
        for piece in self.captured[UPPER]:
            print(" " + piece.name, end='')
        print('')
        print("Captures lower:", end='')
        for piece in self.captured[LOWER]:
            print(" " + piece.name, end='')
        print('\n')


    
    def executeAction(self, action):
        # check for the validity of the input syntactically, and if it is correct
        # hands the action instruction to the relevant authorities bellow 
        actionArgv = action.split(" ")
        if len(actionArgv) == 4 and actionArgv[0] == "move" and actionArgv[3] == "promote" \
           and self.validMoveDropSyntax(MOVE, actionArgv[1], actionArgv[2]):

            self.move(actionArgv[1], actionArgv[2], True)

        elif len(actionArgv) == 3 and actionArgv[0] == "move" \
           and self.validMoveDropSyntax(MOVE, actionArgv[1], actionArgv[2]):

            self.move(actionArgv[1], actionArgv[2], False)

        elif len(actionArgv) == 3 and actionArgv[0] == "drop"\
           and self.validMoveDropSyntax(DROP, actionArgv[1], actionArgv[2]):

            self.drop(actionArgv[1], actionArgv[2])

        else:

            self.setIllegalMoveVariables()

    def validMoveDropSyntax(self, moveOrDrop, arg1, arg2):
        # checks whether action args are in "char char-num" or "charNum charNum" syntax
        arg1Correct = False
        arg2Correct = False
        if moveOrDrop == MOVE:
            arg1Correct = len(arg1) == 2 and arg1[0] in COLUMNS and arg1[1] in ROWS
        elif moveOrDrop == DROP:
            arg1Correct = len(arg1) == 1 and arg1 in PIECE_CHARS
        arg2Correct = len(arg2) == 2 and arg2[0] in COLUMNS and arg2[1] in ROWS

        return (arg1Correct and arg2Correct)

    def getActionsWhenChecked(self, player):
        # INPUT: LOWER or UPPER 
        # finds actions that player can do that will result in a board state they are not in check
        possibleActions = []
        currPlayersPieces = PIECE_CHARS.upper() if player == UPPER else PIECE_CHARS
        # MOVE
        for char in COLUMNS:
            for num in ROWS:
                pieceInSquare = self.getPieceInLoc(char + num)
                if pieceInSquare != None:
                    if pieceInSquare.name[-1] in currPlayersPieces:
                        legalMoves = self.getLegalMoves(char + num)
                        for move in legalMoves:
                            moveAsStr = self.translateArrayIndex(move)
                            if not self.inCheckAfterAction(MOVE, [char + num, moveAsStr], player):
                                possibleActions.append("move " + char + num + " " + moveAsStr)
        # DROP
        for capturedPiece in self.captured[player]:
            legalDrops = self.getLegalDrops(capturedPiece.name)
            for dropAction in legalDrops:
                dropAsStr = self.translateArrayIndex(dropAction)
                if not self.inCheckAfterAction(DROP, [capturedPiece.name, dropAsStr], player):
                    possibleActions.append("drop " + capturedPiece.name.lower() + " " + dropAsStr)
        return sorted(possibleActions)






    def move(self, oldLoc, newLoc, promote):
        # INPUT: "char-num", "char-num", Boolean
        # try to move, and set the game.finished variable accordingly if a move is illegal
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
            self.setIllegalMoveVariables()
            return

        if self.inCheckAfterAction(MOVE, [oldLoc, newLoc], self.turn): # moving pinned piece
            self.setIllegalMoveVariables()
            return

        # PROMOTION
        mvmtInvolvingPromotionZone = (newLoc in promotionZones[self.turn] or oldLoc in promotionZones[self.turn])
        # have to promote P if moved into the zone
        if pieceToMove.name.upper() == "P" and mvmtInvolvingPromotionZone: 
            pieceToMove.name = "+" + pieceToMove.name
        
        elif promote:
            if pieceToMove.name[0] != "+" and \
               mvmtInvolvingPromotionZone and \
               pieceToMove.name.upper() != "D" and pieceToMove.name.upper() != "S":

                pieceToMove.name = "+" + pieceToMove.name
            else:
                self.setIllegalMoveVariables()
                return

        # in case of a capture, move piece to the capturer's grave
        if pieceInDesiredLoc != None: 
            
            if self.turn == LOWER:
                pieceInDesiredLoc.name = pieceInDesiredLoc.name[-1].lower()
                self.captured[self.turn].append(pieceInDesiredLoc)
            else:
                pieceInDesiredLoc.name = pieceInDesiredLoc.name[-1].upper()
                self.captured[self.turn].append(pieceInDesiredLoc)


        self.changeSquare(oldLoc, None)
        self.changeSquare(newLoc, pieceToMove)
        self.numOfMoves += 1
            


    def drop(self, pieceChar, locStr):
        # INPUT: char in PIECE_CHARS, "char-num"
        # try to drop, and set the game.finished variable accordingly if a move is illegal

        pieceChar = pieceChar.upper() if self.turn == UPPER else pieceChar

        # dropping piece that you have not captured
        matchingPiecesInGrave = list(filter(lambda elt: elt.name == pieceChar, self.captured[self.turn]))

        if matchingPiecesInGrave == []:
            self.setIllegalMoveVariables()
            return

        legalDrops = self.getLegalDrops(pieceChar)
        desiredLoc = tuple(self.translateBoardLoc(locStr))

        if desiredLoc not in legalDrops:
            self.setIllegalMoveVariables()
            return

        pieceToDrop = matchingPiecesInGrave[0]
        self.changeSquare(locStr, pieceToDrop)
        self.captured[self.turn].remove(pieceToDrop)
        self.numOfMoves += 1


    def setIllegalMoveVariables(self):
        if self.turn == LOWER:
            self.finished = UPPER_WON_ILLEGAL_MOVE
        elif self.turn == UPPER:
            self.finished = LOWER_WON_ILLEGAL_MOVE
        
    def translateBoardLoc(self, charNum): 
        # translates the board location (i.e. e5) into array-index format
        char, num = charNum
        y = int(num) - 1
        x = ord(char) - ord("a")
        return [x, y]

    def translateArrayIndex(self, coordinate):
        # translates array-index (i.e. [0,0]) into a string representing board location
        x, y = coordinate
        return COLUMNS[x] + ROWS[y]
        
    
    def getPieceInLoc(self, charNum):
        x, y = self.translateBoardLoc(charNum)
        return self.state._board[x][y]
    
    def changeSquare(self, charNum, newPiece):
        # replace square with the new piece
        x, y = self.translateBoardLoc(charNum)
        self.state._board[x][y] = newPiece
    
    def getLegalMoves(self, locOfPieceToMove):
        # given board, extend until you hit an obstacle in all directions.
        # return set of all squares you are allowed to move.
        piece = self.getPieceInLoc(locOfPieceToMove)
        x, y = self.translateBoardLoc(locOfPieceToMove)
        legalMoves = set()

        for direction in piece.maxRange(): 
        # for instance, Up direction for Notes. I will continue 
        # extending in the direction until I hit an obstacle
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
                        break # move to another direction, for instance Left
        return legalMoves

    def inCheckAfterAction(self, action, arguments, player):
        # INPUT: MOVE or DROP; valid arguments for the actions; LOWER or UPPER
        # given Game state, and action, see if executing the action
        # causes the player to be in check. 
        # return True if so

        # I don't have to consider promoting
        checkAfterAction = False
        if action == MOVE:
            startLoc, endLoc = arguments
            pieceToMove = self.getPieceInLoc(startLoc)
            pieceInDestination = self.getPieceInLoc(endLoc)

            # temporarily change board state to simulate action and check for check
            self.changeSquare(startLoc, None)
            self.changeSquare(endLoc, pieceToMove)

            checkAfterAction = self.check(player)

            # UNDO the temporary changes above
            self.changeSquare(endLoc, pieceInDestination)
            self.changeSquare(startLoc, pieceToMove)

        elif action == DROP:
            pieceChar, endLoc = arguments

            # temporarily change board state to simulate action and check for check
            self.changeSquare(endLoc, Piece(pieceChar))

            checkAfterAction = self.check(player)

            # UNDO the temporary change above
            self.changeSquare(endLoc, None)

        return checkAfterAction

    def findColumnWithP(self, player):
        # find the column that player has a P in, if any.
        columnWithP = -1
        for x in range(5):
            for y in range(5):
                pieceInSquare = self.state._board[x][y]
                if pieceInSquare != None and pieceInSquare.name[-1] == "pP"[player]: # p if LOWER, P if UPPER
                    columnWithP = x
        return columnWithP

    def getLegalDrops(self, pieceChar):
        # checks for all the legal drops given a piece.
        # considers the restrictions for P

        legalDrops = set()
        columnWithP = self.findColumnWithP(self.turn)

        for x in range(5):
            for y in range(5):
                pieceInSquare = self.state._board[x][y]
                if pieceInSquare == None:
                    if pieceChar.upper() == "P":

                        droppingPInPromotionZone = self.translateArrayIndex((x, y)) in promotionZones[self.turn]
                        droppingPResultsInCheckmate = self.inCheckAfterAction(DROP, [pieceChar, self.translateArrayIndex((x, y))], (not self.turn) * 1)
                        otherPInColumn = columnWithP == x

                        if not (droppingPInPromotionZone or droppingPResultsInCheckmate or otherPInColumn):
                            legalDrops.add((x, y))

                    else:
                        legalDrops.add((x, y))

        return legalDrops


    def check(self, player):
        # is player in check?

        controledAndDriveLocs = self.allControlledSquares()
        if controledAndDriveLocs[player + 2] in controledAndDriveLocs[player]:
            return True
        else:
            return False

    def allControlledSquares(self):
        # return a list of the controlled squares by both of the players, 
        # and the locations of their drive pieces. Useful for check detection.
        lowerControls = set()
        upperControls = set()
        lowerDLocation = None
        upperDLocation = None
        for char in COLUMNS:
            for num in ROWS:
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

