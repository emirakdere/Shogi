class Piece:
    """
    Class that represents a BoxShogi piece
    """

    def __init__(self, name, arrayLoc, originalOwner):
        self.name = name
        self.arrayLoc = arrayLoc
        #self.controller = originalOwner
        self.originalOwner = originalOwner

    def __repr__(self):
        return self.name# + ", " + str(self.arrayLoc)
    
    #def getMoves()
    def isOpponentPiece(self, otherPiece):
        if self.name.islower():
            return otherPiece.name.isupper()
        else:
            return otherPiece.name.islower()

    def maxRange(self):
        drive = [[(0, 1)],[[1, 0]],[[0, -1]],[[-1, 0]],[[1, 1]],[[1, -1]],[[-1, -1]],[[-1, 1]]]

        notes = [[[1, 0], [2, 0], [3, 0], [4, 0]],\
                 [[-1,0], [-2,0], [-3,0], [-4,0]],\
                 [[0, 1], [0, 2], [0, 3], [0, 4]],\
                 [[0,-1], [0,-2], [0,-3], [0,-4]]]

        governence = [[[1,  1], [2,  2], [3,  3], [4,  4]],\
                      [[1, -1], [2, -2], [3, -3], [4, -4]],\
                      [[-1,-1], [-2,-2], [-3,-3], [-4,-4]],\
                      [[-1, 1], [-2, 2], [-3, 3], [-4, 4]]]
 
        shield = [[[-1,0]], [[-1,1]], [[0,1]], [[1,1]], [[1,0]], [[0,-1]]]

        relay = [[[-1,-1]], [[-1,1]], [[0,1]], [[1,1]], [[1,-1]]]


        if self.name[-1].upper() == "D": # Queen
            return drive
        if self.name[-1].upper() == "N": # Rook
            return notes if self.name[0] != '+' else notes + drive
        if self.name[-1].upper() == "G": # Bishop
            return governence if self.name[0] != '+' else governence + drive
        if self.name[-1].upper() == "S":
            return shield
        if self.name[-1].upper() == "R":
            return relay if self.name[0] != '+' else shield
        if self.name[-1].upper() == "P":
            return [[[0, 1]]] if self.name[0] != '+' else shield







