

import unittest

from fillomino import Board, Display

class test_Display(unittest.TestCase):
  
  # perform all tests in this class
  TEST_ALL = True
  
  @classmethod
  def setUpClass(cls):
    pass
  
  def setUp(self):
    self.board   = Board(rows=2, columns=10)
    self.display = Display(self.board)
  
  #@unittest.skipIf(True, " ToDo")
  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_view(self):
    """  """
    
    self.display.view()
    
    