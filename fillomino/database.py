
import logging
logger = logging.getLogger(__name__)

import os
import json
import sqlite3

from fillomino.board import Board


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
    for rows, columns in [(10, 10), (15,15), (20,20)]:
      tableDefinition = DatabaseSetup.getBoardTableDefinition(rows, columns)
      db._executeCommand(tableDefinition)
    
    # close the database connection
    db.close()
  
  @staticmethod
  def getBoardTableDefinition(rows, columns):
    """ SQL table definition for a board table """
    
    # id:             unique ID for this board
    # initial_board:  layout for unsolved board
    # final_board:    layout for solved board
    # creation_date:  date board was created
    # shortest_solve: shortest solve time
    # longest_solve:  longest solve time
    # mean_solve:     average solve time
    # std_solve:      standard deviation of average solve time
    # solve_count:    number of times board was solved
    # stats:          miscellaneous board stats
    #
    definition = """
      create table IF NOT EXISTS boards{}x{}(
        id             INT UNSIGNED,
        initial_board  JSON,
        final_board    JSON,
        creation_date  DATETIME,
        shortest_solve INT UNSIGNED DEFAULT NULL,
        longest_solve  INT UNSIGNED DEFAULT NULL,
        mean_solve     FLOAT UNSIGNED DEFAULT NULL,
        std_solve      FLOAT UNSIGNED DEFAULT NULL,
        solve_count    INT UNSIGNED DEFAULT 0,
        stats          JSON,
        PRIMARY KEY (id)
      );
    """.format(rows, columns)
    
    return definition
    
class Database(object):
  
  class Decorators(object):
  
    @classmethod
    def openAndClose(cls, func):
      def wrapper(*args, **kwargs):
        self = args[0]
        self.connect()
        result = func(*args, **kwargs)
        self.close()
        return result
      return wrapper
      
  def __init__(self, dbFile):
    self.dbFile = dbFile
    self.conn = None
    self.cursor = None
  
  def __del__(self):
    if self.conn is not None:# and self.conn.is_connected():
      self.close()
  
  def connect(self):
    self.conn   = sqlite3.connect(self.dbFile)
    self.cursor = self.conn.cursor()
  
  def close(self):
    self.conn.close()
  
  @Decorators.openAndClose
  def _executeCommand(self, cmd):
    #print(cmd)
    self.cursor.execute(cmd)
    self.conn.commit()

    return self.cursor.fetchall()
    
    
  def loadRandomBoard(self, rows, columns):
    """ Retrieve a random <rows> x <columns> board from the database and return it """
    
    # columns to load
    columnNames = ["id", "initial_board", "final_board", "creation_date",
                   "shortest_solve", "longest_solve", "mean_solve",
                   "std_solve", "solve_count", "stats"]
    
    cmd  = """SELECT * FROM boards{}x{} ORDER BY RANDOM() LIMIT 1""".format(rows, columns)
    ret = self._executeCommand(cmd)
    
    if len(ret) != 1:
      return None
      #raise SystemError("No boards in the {}x{} table".format(rows, columns))
    
    # create and return the board
    boardDict = dict(zip(columnNames, ret[0]))
    for jsonKey in ["initial_board", "final_board", "stats"]:
      boardDict[jsonKey] = json.loads(boardDict[jsonKey])
    return Board.createBoard(rows, columns, **boardDict)
    
  
  def loadBoard(self, rows, columns, boardID):
    """ Load a board from the <rows> x <columns> table with the given ID """

    # columns to load
    columnNames = ["id", "initial_board", "final_board", "creation_date",
                   "shortest_solve", "longest_solve", "mean_solve",
                   "std_solve", "solve_count", "stats"]
    
    # get the board
    cmd = """SELECT * FROM boards{}x{} WHERE id = {};""".format(rows, columns, boardID)
    ret = self._executeCommand(cmd)
    
    # return the board if it exists
    if len(ret) != 1:
      return None
    else:
      boardDict = dict(zip(columnNames, ret[0]))
      for jsonKey in ["initial_board", "final_board", "stats"]:
        boardDict[jsonKey] = json.loads(boardDict[jsonKey])
      return Board.createBoard(rows, columns, **boardDict)
  
  
  def storeBoard(self, rows, columns, boardID, initialBoard, finalBoard, creationDate, stats):
    """ Store a board in the <rows> x <columns> table """
    
    # create the table if it doesn't exist
    self._createBoardTable(rows, columns)
    
    # get the board with the given boardID to see if it already exists
    cmd  = """SELECT * FROM boards{}x{} WHERE id = {};""".format(rows, columns, boardID)
    ret = self._executeCommand(cmd)
  
    # if the board already exists
    if len(ret) != 0:
      raise SystemError("Board with id {} already exists".format(boardID))
    
    
    
    # insert the new board
    cmd  = """INSERT INTO boards{}x{}(id, initial_board, final_board, creation_date, stats) """ \
          .format(rows, columns)
    cmd += """VALUES({},'{}','{}','{}','{}')"""\
          .format(boardID,
                  json.dumps(initialBoard),
                  json.dumps(finalBoard),
                  json.dumps(creationDate),
                  json.dumps(stats))
    self._executeCommand(cmd)
    
    return self.cursor.lastrowid

  def getBoardsInfo(self):
    """
    # Get general information on all of the board types in the database
    #  -row and column lengths
    #  -number of each type of board
    #
    """
    
    # get the names of all the boards
    cmd = """SELECT name FROM sqlite_master WHERE type='table';"""
    results = self._executeCommand(cmd)
    
    boardsInfo = {}
    
    for result in results:
      try:
        
        # get the table name and ignore any tables other than boards
        tableName = result[0]
        if not tableName.startswith("boards"):
          continue
        
        # get the number of rows and columns
        rows, columns = map(int, tableName.replace("boards", "").split("x"))
        
        # get information about this table
        boardsInfo[(rows, columns)] = {
          "length": self._getTableLength(tableName)
        }
        
      # problem parsing board data
      except Exception as err:
        raise SystemError("Problem retrieving board info\nResults: {}\nError: {}".format(results, err))
    
    return boardsInfo
  
  
  def _createBoardTable(self, rows, columns):
    """ Create a board table if it doesn't alread exist """
    
    if self.getBoardsInfo().get((rows, columns), None) is None:
      tableDefinition = DatabaseSetup.getBoardTableDefinition(rows, columns)
      self._executeCommand(tableDefinition)

  def _getTableLength(self, tableName):
    """ Return the number of entries in the given table """
    
    cmd = """select count(*) from {};""".format(tableName)
    res = self._executeCommand(cmd)
    if len(res) != 1:
      raise SystemError("Unable to get the table length for {}".format(tableName))
    
    return int(res[0][0])