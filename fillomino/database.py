import json
import sqlite3
from sqlite3 import Error

import os

class DatabaseSetup(object):
  
  @staticmethod
  def createDatabase(fileLocation):
    """ Create a new, blank database """
    
    if os.path.exists(fileLocation):
      raise FileExistsError("database file {} already exists".format(fileLocation))
    
    # connect to the database
    db = Database(fileLocation)
    db.connect()
    
    # create the tables
    for tableDefinition in DatabaseSetup.getBoardTables():
      db._executeCommand(tableDefinition)
    
    # close the database connection
    db.close()
  
  @staticmethod
  def getBoardTables():
    """ SQL table definitions """
    
    boardLayouts = [
      (10,10),
      (20,20)
    ]
    
    definitions = []
    
    for rows, columns in boardLayouts:
      # ticker:              ticker symbol
      # stock_exchange:      Stock exchange this instrument uses via the broker
      # conversion_factor:   factor to divide table prices by to get the actual prices (table values are stored as ints)
      # instrument_id:       id matching the instrument in the INSTRUMENTS table
      # name:                name for this instrument
      #
      definition = """
        create table IF NOT EXISTS boards{}x{}(
          id            INT UNSIGNED,
          initial_board JSON,
          final_board   JSON,
          stats         JSON,
          PRIMARY KEY (id)
        );
      """.format(rows, columns)
      definitions.append(definition)
    
    return definitions
    
class Database(object):
  

      
  def __init__(self, dbFile):
    self.dbFile = dbFile
    self.conn = None
    self.cursor = None
  
  def __del__(self):
    if self.conn:
      self.close()
  
  def connect(self):
    self.conn   = sqlite3.connect(self.dbFile)
    self.cursor = self.conn.cursor()
  
  def close(self):
    self.conn.close()
  
  def _executeCommand(self, cmd):
    #print(cmd)
    self.cursor.execute(cmd)
    self.conn.commit()

    return self.cursor.fetchall()
    
    
  def loadRandomBoard(self, rows, columns):
    cmd  = """SELECT * FROM boards{}x{} ORDER BY RANDOM() LIMIT 1""".format(rows, columns)
    ret = self._executeCommand(cmd)
    
    if len(ret) != 1:
      raise SystemError("No boards in the {}x{} table".format(rows, columns))

    board = ret[0]
    return {
      "id":           board[0],
      "initialBoard": json.loads(board[1]),
      "finalBoard":   json.loads(board[2]),
      "stats":        json.loads(board[3])
    }
    
  
  def loadBoard(self, rows, columns, boardID):
    """ Load a board from the rows x columns table with the given id """
    
    # get the board
    cmd = """SELECT * FROM boards{}x{} WHERE id = {};""".format(rows, columns, boardID)
    ret = self._executeCommand(cmd)
    
    # return the board if it exists
    if len(ret) != 1:
      return None
    else:
      board = ret[0]
      return {
        "id":           board[0],
        "initialBoard": json.loads(board[1]),
        "finalBoard":   json.loads(board[2]),
        "stats":        json.loads(board[3])
      }
  
  
  def storeBoard(self, rows, columns, boardID, initialBoard, finalBoard, stats):
    """ Store a board in the rows x columns table """
  
    # get the board with the given boardID to see if it already exists
    cmd  = """SELECT * FROM boards{}x{} WHERE id = {};""".format(rows, columns, boardID)
    ret = self._executeCommand(cmd)
  
    # if the board already exists
    if len(ret) != 0:
      raise SystemError("Board with id {} already exists".format(boardID))
    
    # insert the new board
    cmd = """INSERT INTO boards{}x{}(id, initial_board, final_board, stats) VALUES({},'{}','{}','{}')"""\
          .format(rows,
                  columns,
                  boardID,
                  json.dumps(initialBoard),
                  json.dumps(finalBoard),
                  json.dumps(stats))
    self._executeCommand(cmd)
    return self.cursor.lastrowid

  
  
  
  