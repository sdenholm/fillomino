
import datetime
import math
import sys

#import numpy as np
#import pandas as pd
#import Tkinter as tk
#import tkSimpleDialog

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
#import pyqtgraph as pg

import numpy as np

from datetime import timedelta

import threading
import time

import PyQt5.QtWidgets as QtWidgets
#from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication



class MainApp(QtCore.QObject):
  """
  """
  
  CELL_STYLE_NORMAL      = "border-style: outset; border-width: 1px; border-color: black; background: white;"
  CELL_STYLE_HIGHLIGHTED = "border-style: outset; border-width: 1px; border-color: yellow; background: yellow;"

  # initial setup
  def __init__(self):
    """ Setup the main window """
    
    QtCore.QObject.__init__(self)
    
    ###self.funcCall.connect(self.entryUpdated)
    
    # dictionary of all of the function timers we add
    #self.timers = {}
    
    # dictionary of all of our info widgets
    #self.widgets = {}
    
    #self.currentRow = 0
    
    # =========================================================================
    # GUI
    # =========================================================================
    
    # application object
    self.app = QtWidgets.QApplication(sys.argv)
    self.mainWindow = QtWidgets.QWidget()
    
    # set window size and title
    self.mainWindow.resize(600, 600)
    self.mainWindow.setWindowTitle("Fillomino v0.1")

    self.mainWindow.keyPressEvent = self._keyPressed
    
    #cell.mousePressEvent = lambda event: self._cellClicked(event, x, y)
    
    # use a box layout for the other layouts
    self.mainLayout = QtWidgets.QVBoxLayout()
    self.mainWindow.setLayout(self.mainLayout)
    
    # menu bar
    menuLayout = self._createMenuBar()
    self.mainLayout.addLayout(menuLayout, 1)
    
    # game grid
    self.gameGrid, gridLayout = self._createGrid(rows=20, columns=20)
    self.mainLayout.addLayout(gridLayout, 100)
    
    # controls
    self.controls = MainApp._createControls()
    self.mainLayout.addLayout(self.controls, 1)
    # =========================================================================
    
    
    self.currentCell = None
    
    
  def _keyPressed(self, event):
    
    # ignore anything that's not a number
    key = event.key()
    if key < 49 or key > 57:
      return
    
    # set the current cell to this number
    if self.currentCell:
      self.currentCell.setText(chr(key))
  
  def _cellClicked(self, event, x, y):
    """ Called whenever a cell is clicked """
  
    #sender = x.sender()
    #print(sender.text())
    
    # set the current cell to normal
    if self.currentCell:
      self.currentCell.setStyleSheet(MainApp.CELL_STYLE_NORMAL)

    # make this cell the current cell
    self.currentCell = self.gameGrid[x][y]
    self.gameGrid[x][y].setStyleSheet(MainApp.CELL_STYLE_HIGHLIGHTED)
    
    #print(x, y)
    
    """
    cell = self.gameGrid[0][0]
    print(cell.width())
    print(cell.height())

    print(event.x(), event.y())
    print(event.globalX(), event.globalY())
    """

  @QtCore.pyqtSlot()
  def _menuClicked(self):
    """ Called whenever a menu item is clicked """
    
    menuAction = self.sender()
    
    actionMap = {
      "New":   lambda: print("New"),
      "Save":  lambda: print("Save"),
      "Load":  lambda: print("Load"),
      "Quit":  lambda: sys.exit(),
      "About": lambda: print("About"),
    }
    
    action = actionMap.get(menuAction.text(), None)
    if action is not None:
      action()
    
  def _createMenuBar(self):
    """ Create the menu bar GUI elements"""
    
    # layout
    menuLayout = QtWidgets.QVBoxLayout()
    menuLayout.setAlignment(QtCore.Qt.AlignTop)
    
    # menu bar itself
    menubar = QtWidgets.QMenuBar()
    menubar.setNativeMenuBar(False)
    menubar.setStyleSheet("padding: 1px;")
    menuLayout.addWidget(menubar)
    
    # file
    fileMenu = menubar.addMenu("File")
    fileMenu.addAction("New",  self._menuClicked)
    fileMenu.addAction("Save", self._menuClicked)
    fileMenu.addAction("Load", self._menuClicked)
    fileMenu.addSeparator()
    fileMenu.addAction("Quit", self._menuClicked)
    
    # help
    helpMenu = menubar.addMenu("Help")
    helpMenu.addAction("About",  self._menuClicked)
    
    return menuLayout
  
  
  def _createGrid(self, rows, columns):
    """ Create the number grid, composed of individual cells """
    
    gridLayout = QtWidgets.QGridLayout()
    gridLayout.setSpacing(0)
  
    options = [""] + [str(x) for x in range(1, 10)]
  
    grid = {}
    for x in range(rows):
      grid[x] = {}
      for y in range(columns):
        grid[x][y] = self._createCell(np.random.choice(options), x, y)
        gridLayout.addWidget(grid[x][y], x, y)
        
    return grid, gridLayout
  

  #@staticmethod
  def _createCell(self, contents, x, y):
    """ Create an individual grid cell """

    cell = QtWidgets.QLabel(contents)
    cell.setAlignment(QtCore.Qt.AlignCenter)
    cell.setScaledContents(True)
    # cell.setStyleSheet("margin-left: 10px; border-radius: 25px; background: white; color: #4A0C46;")
    cell.setStyleSheet(MainApp.CELL_STYLE_NORMAL)#"border-style: outset; border-width: 1px; border-color: black; background: white;")
    
    font = QtGui.QFont()
    #font.setFamily("FreeMono")
    font.setPointSize(14)
    cell.setFont(font)

    cell.mousePressEvent = lambda event: self._cellClicked(event, x, y)
    
    return cell

  @staticmethod
  def _createControls():
    """ Create the control buttons at the bottom of the window """
  
    controlsGrid = QtWidgets.QGridLayout()
    controlsGrid.setAlignment(QtCore.Qt.AlignLeft)
    button = QtWidgets.QPushButton("Clear")
  
    controlsGrid.addWidget(button, 0, 1)
  
    return controlsGrid
  
  # display the gui
  def run(self):
    """ Enter the main loop of the GUI """
    self.mainWindow.show()
    sys.exit(self.app.exec_())


  def _newBoard(self):
    
    pass