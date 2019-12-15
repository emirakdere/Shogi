class Piece:
    """
    Class that represents a BoxShogi piece
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name
    
    def isOpponentPiece(self, otherPiece):
        if self.name.islower():
            return otherPiece.name.isupper()
        else:
            return otherPiece.name.islower()

    def ownerOfPiece(self):
        return self.name[-1].isupper() * 1
        

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
 
        shieldLower = [[[-1,0]], [[-1,1]], [[0, 1]], [[1,  1]], [[1, 0]], [[0,-1]]]
        shieldUpper = [[[1, 0]], [[1,-1]], [[0,-1]], [[-1,-1]], [[-1,0]], [[0, 1]]]
        shieldOptions = [shieldLower, shieldUpper]

        relayLower = [[[-1,-1]], [[-1,1]], [[0, 1]], [[1,  1]], [[1,-1]]]
        relayUpper = [[[1,  1]], [[1,-1]], [[0,-1]], [[-1,-1]], [[-1,1]]]
        relayOptions = [relayLower, relayUpper]
        
        player = self.name[-1].isupper()

        if self.name[-1].upper() == "D": # King
            return drive
        if self.name[-1].upper() == "N": # Rook
            return notes if self.name[0] != '+' else notes + drive
        if self.name[-1].upper() == "G": # Bishop
            return governence if self.name[0] != '+' else governence + drive
        if self.name[-1].upper() == "S":
            return shieldOptions[player]
        if self.name[-1].upper() == "R":
            return relayOptions[player] if self.name[0] != '+' else shieldOptions[player]
        if self.name[-1].upper() == "P":
            return [[[[0, 1]]],[[[0, -1]]]][player] if self.name[0] != '+' else shieldOptions[player]







