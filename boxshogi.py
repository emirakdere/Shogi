from piece import Piece
from board import Board
from game import Game
from globalVars import *
import utils
import sys
import os

def executeTurn(gameBoard, isInteractive, rules):
    # INPUT: Game object; Boolean; list of moves (if file mode) or None (if interactive)
    
    inCheck = gameBoard.check(gameBoard.turn)
    playerStr = "lower" if gameBoard.turn == LOWER else "UPPER"

    if isInteractive:
        gameBoard.print()
    
    # check for checkmate
    if inCheck:

        possibleActions = gameBoard.getActionsWhenChecked(gameBoard.turn)
        if possibleActions != []:
            if isInteractive:
                print(playerStr + " player is in check!" + '\n' + "Available moves:")
                for act in possibleActions:
                    print(act)
        else:
            gameBoard.finished = UPPER_WON_CHECKMATE if gameBoard.turn == LOWER else LOWER_WON_CHECKMATE
        
    # if gameBoard is finished, don't take input; exit the while loop in driver()
    if gameBoard.finished == NO_CHECKMATE:
        
        if isInteractive:
            print(playerStr + "> ", flush=True, end="")            
            action = input()
            
        else:
            action = rules[gameBoard.numOfMoves]
            
        gameBoard.prevMove = action

        # check for the validity of the action the player entered
        if inCheck:
            if action not in possibleActions:
                gameBoard.finished = UPPER_WON_ILLEGAL_MOVE if gameBoard.turn == LOWER else UPPER_WON_ILLEGAL_MOVE
        if gameBoard.finished == NO_CHECKMATE:
            
            gameBoard.executeAction(action)
            gameBoard.turn = (not gameBoard.turn) * 1 # next person's turn


def driver(isInteractive, dicOfInitialState):
    # INPUT: Boolean, a dictionary parsed by util.py (or an analogous variant)
    gameBoard = Game(dicOfInitialState)
    moveList = None if isInteractive else dicOfInitialState['moves']
    
    while (not gameBoard.finished) and (isInteractive or gameBoard.numOfMoves < len(moveList)):
        executeTurn(gameBoard, isInteractive, moveList)
        if gameBoard.numOfMoves == 400:
            gameBoard.finished = TIE_GAME

    # in file mode, print the last standing for a game that ended
    if not isInteractive and gameBoard.finished != NO_CHECKMATE:
        lastMovedPlayer = (not gameBoard.turn) * 1
        playerStr = "lower" if lastMovedPlayer == LOWER else "UPPER"
        print(playerStr + " player action: " + gameBoard.prevMove)
        gameBoard.print()
        

    # game state
    if gameBoard.finished == UPPER_WON_CHECKMATE:
        print("UPPER player wins.  Checkmate.", end='')
    elif gameBoard.finished == LOWER_WON_CHECKMATE:
        print("lower player wins.  Checkmate.", end='')
    elif gameBoard.finished == UPPER_WON_ILLEGAL_MOVE:
        print("UPPER player wins.  Illegal move.", end='')
    elif gameBoard.finished == LOWER_WON_ILLEGAL_MOVE:
        print("lower player wins.  Illegal move.", end='')
    else:
        # in file mode, if we ran out of moves in moveList
        # in interactive mode, we ran out of available moves
        lastMovedPlayer = (not gameBoard.turn) * 1
        
        inCheck = gameBoard.check(gameBoard.turn)
        playerStr = "lower" if lastMovedPlayer == LOWER else "UPPER"
        currPlayerStr = "lower" if lastMovedPlayer == UPPER else "UPPER"
        lastLine = False
        
        if gameBoard.finished == TIE_GAME:
            if inCheck:

                possibleActions = gameBoard.getActionsWhenChecked(gameBoard.turn)
                if possibleActions == []:
                    print(playerStr + " player wins.  Checkmate.", end='')
            else:
                print("Tie game.  Too many moves.", end='')

        else:
            print(playerStr + " player action: " + gameBoard.prevMove)
            gameBoard.print()
            if inCheck:
                possibleActions = gameBoard.getActionsWhenChecked(gameBoard.turn)
                if possibleActions != []:
                    
                    print(currPlayerStr + " player is in check!")
                    print("Available moves:")
                    for act in possibleActions:
                        print(act)
                else:
                    lastLine = True
                    if gameBoard.turn == LOWER:
                        print("UPPER player wins.  Checkmate.", end='')
                    elif gameBoard.turn == UPPER:
                        print("lower player wins.  Checkmate.", end='')
                        
            if not lastLine:
                print(currPlayerStr + "> ", flush=True, end="")
    

def main():
    # Interactive Mode
    if len(sys.argv) == 2 and sys.argv[1] == "-i":
        # in a normal game, this is how the board is set up
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
    
    # File Mode
    elif len(sys.argv) == 3 and sys.argv[1] == "-f" and os.path.exists(sys.argv[2]) and os.path.isfile(sys.argv[2]):
            testCase = utils.parseTestCase(sys.argv[2])
            driver(False, testCase)

    else:
        raise Exception("Invalid game mode specification.")
        
if __name__ == "__main__":
    main()
