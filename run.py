
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from fillomino import Board, Display

#board   = Board(10,10)
display = Display(Board(10,10))
display.run()