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
        print("piece: " + self.name + ", " + str(self.loc))
    
    #def getMoves()