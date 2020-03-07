import concurrent.futures as futures
import logging
import os
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from fillomino.controller import Controller

from fillomino.database import DatabaseSetup

# test imports
try:
  import yaml
  import numpy
  import PyQt5
except ImportError as err:
  print("ERROR: Importing failed. Run 'pip3 install -r requirements.txt' to install requirements")
  raise err

#try:
#  os.remove("boards.db")
#except FileNotFoundError:
#  pass
#DatabaseSetup.createDatabase("boards.db")

app = Controller("config.yaml")
app.run()
