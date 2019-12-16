LOWER = 0
UPPER = 1
MOVE = 0
DROP = 1
NO_CHECKMATE = 0
LOWER_WON_CHECKMATE = 1
UPPER_WON_CHECKMATE = 2
LOWER_WON_ILLEGAL_MOVE = 3
UPPER_WON_ILLEGAL_MOVE = 4
TIE_GAME = 5
BOARD_SIZE = 5

PIECE_CHARS = "dngsrp"
ROWS = "12345"
COLUMNS = "abcde"
promotionZones = {UPPER:{"a1", "b1", "c1", "d1", "e1"}, \
                  LOWER:{"a5", "b5", "c5", "d5", "e5"}}
