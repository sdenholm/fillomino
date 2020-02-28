

class Display(object):
  
  def __init__(self, board):
    self.board = board
  
  def view(self):
    
    vals = self.board.getValues()

    for row in range(self.board.rows):
      for col in range(self.board.columns):
        print("{}  ".format(vals[row, col]), end="")
      print("")

    #print(vals)