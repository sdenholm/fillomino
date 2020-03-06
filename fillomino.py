
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from fillomino.controller import Controller

from fillomino.database import DatabaseSetup

os.remove("boards.db")
DatabaseSetup.createDatabase("boards.db")

app = Controller("config.yaml")
app.run()
