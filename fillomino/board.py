

import numpy as np

class Board(object):
  
  def __init__(self, rows, columns):
    
    self.rows    = rows
    self.columns = columns
    self.values  = np.zeros((rows, columns), np.int8)
  
  def getValues(self):
    return self.values