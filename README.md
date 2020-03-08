Fillomino 
---

####Instructions

Install the python requirements with pip:
```bash
pip3 install -r requirements.txt
```

From the main directory, run the game using:
```bash
python3 fillomino.py
```

####How to Play
1. Fill in the blanks using the digits 1-9 to create regions, called polyominoes.
2. A region must contain as many cells as its number value e.g., three number 3s together will
make a region, or four number 4s together, five number 5s, etc.
3. Regions with the same number cannot touch. For example, two regions of four 4s cannot
be neighbours.
4. When the board is filled, you win!


####Generating Boards
To play, you must first generate boards. This is done in-game, and may take a while for very large boards, depending on your processor. 20x20 boards are typically the largest boards used, and take a few seconds to generate.

Generation is parallelised at the board level, so generating multiple boards at the same time is the best way to go.
