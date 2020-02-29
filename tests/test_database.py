import os
import unittest

from fillomino.database import Database, DatabaseSetup

class test_Database(unittest.TestCase):
  
  # perform all tests in this class
  TEST_ALL = True
  
  @classmethod
  def setUpClass(cls):
    pass
  
  def setUp(self):
    self.dbName = "testDB.db"
    
    # make sure the test database already exists
    if os.path.exists(self.dbName):
      raise FileExistsError("test database {} already exists")

    # create a test database
    DatabaseSetup.createDatabase(self.dbName)
    self.db = Database(self.dbName)
    self.db.connect()
  
  
  def tearDown(self):
    
    # close the database
    if self.db:
      self.db.close()
    
    # delete the test database
    if os.path.exists(self.dbName):
      os.remove(self.dbName)
  
  
  # @unittest.skipIf(True, " ToDo")
  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_dbOperations(self):
    """  """
    
    # tests:
    #  -store X boards and retrieve X boards
    #  -can't store a board with a duplicate id
    #  -can't load a board with an ID that doesn't exist
    

    rows         = 20
    columns      = 20
    boardID      = 777
    initialBoard = {"a":1}
    finalBoard   = {"b":2}
    stats        = {"c":20, "d":30}
    ret = self.db.storeBoard(rows         = rows,
                             columns      = columns,
                             boardID      = boardID,
                             initialBoard = initialBoard,
                             finalBoard   = finalBoard,
                             stats        = stats)
    
    ret2 = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
    
    print(ret)
    
    print(ret2)