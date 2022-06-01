from breezypythongui import EasyFrame, EasyCanvas
from tkinter import *
import math
import random
import pickle
import os
import datetime

class GameBoardCanvas(EasyCanvas):
    def __init__(self, parent, size, playerturn, winner, draw):
        #print("Starting GameBoardCanvas Init")
        EasyCanvas.__init__(self, parent, width=300, height=300, background="brown")
        self._items = list()

        self.fnWinner = winner
        self.fnDraw = draw
        self.fnPlayerTurn = playerturn

        self.TTT = TicTacToe(size)
        self.state = {}
        for i in range(1, (size*size) + 1):
            self.state[i] = str(i)
        
        self.currentTurn = "o"
        self.isActive = False

        self.squareSide = 300 / size

        for c in range(size):
            colOffset = c * self.squareSide
            for r in range(size):
                rowOffset = r * self.squareSide

                item = self.drawRectangle(rowOffset, colOffset, \
                                     rowOffset + self.squareSide, colOffset + self.squareSide, \
                                     outline = "black", fill = "lightgrey")
                self.itemconfigure(item, width=2)
                # Add tag
                self.itemconfigure(item, tags="sqr"+str(item))
                # Add events
                self.tag_bind(item, '<Button-1>',self.object_click_event)
                self.tag_bind(item, '<Enter>', self.object_enter_event)
                self.tag_bind(item, '<Leave>', self.object_leave_event)

                self._items.append(item)

    def getPlayerColor(self):
        if self.currentTurn == "x":
            return "blue"
        else:
            return "red"

    def getNextPlayer(self):
        if self.currentTurn == "x":
            return "o"
        else:
            return "x"
        
    def getCurrentPlayer(self):
        return self.currentTurn

    def setCurrentPlayer(self, player):
        self.currentTurn = player

    def setNextPlayer(self):
        tmp = self.getNextPlayer()
        self.currentTurn = tmp
        self.fnPlayerTurn(tmp)

    def setSquare(self, square, player = ''):
        if player == '':
            player = self.getCurrentPlayer()

        # Update the State
        self.state[square] = player

        # Set the square colors
        self.itemconfigure(square, fill=self.getPlayerColor())
        self.itemconfigure(square, outline="black")

        # Add text graphic to square
        cords = self.coords(square)
        self.create_text(cords[0] + (self.squareSide/2), cords[1] + (self.squareSide/2), \
                             text = player.upper(), fill="black", \
                             font=('Helvetica 24 bold'))

        # Check to see if the current player has won/draw/next player
        self.isActive = False
        tmp = self.getCurrentPlayer()
        if self.TTT.checkWinnerN(self.state, tmp) == True:
            self.fnWinner(tmp)
        elif self.TTT.checkDraw(self.state) == True:
            self.fnDraw()
        else:
            self.isActive = True
            self.setNextPlayer()

    def takeComputerTurn(self, cpuai):
        if self.TTT.hasEmptySpace(self.state):
            #print(cpuai)
            if cpuai == "Easy":
                space = self.TTT.pickEmptySpace(self.state)
            else:
                space = self.TTT.computerPickAdvanced(self.state, self.getCurrentPlayer(), self.getNextPlayer())
            #print("Space: ", space)
            self.setSquare(space, self.getCurrentPlayer())        

    def object_click_event(self, event):
        if self.isActive == False: return
        current = event.widget.find_withtag('current')        
        if self.state[current[0]] != 'x' and self.state[current[0]] != 'o':
            self.setSquare(current[0])
            #print("Current State: ", self.state)

    def object_enter_event(self, event):
        if self.isActive == False: return
        current = event.widget.find_withtag('current')
        if self.state[current[0]] != 'x' and self.state[current[0]] != 'o':
            self.itemconfigure(current, outline="green")
            #print("Entered: tags", self.gettags(current))

    def object_leave_event(self, event):
        if self.isActive == False: return
        current = event.widget.find_withtag('current')
        if self.state[current[0]] != 'x' and self.state[current[0]] != 'o':
            self.itemconfigure(current, outline="black")
            #print("Leaving: tags", self.gettags(current))
            
class GameBoard(EasyFrame):

    def __init__(self):
        #print("Starting GameBoard")
        EasyFrame.__init__(self, width=640, height=480, resizable = False, title="Tic Tac Toe")


        self.winsX = 0
        self.winsO = 0
        self.draws = 0

        self.highScores = {}
        # load the high scores file.
        self.loadScores()


        self.pTop = self.addPanel(0, 0, rowspan = 1, columnspan = 3)#, background = "lightgrey")
        self.pLeft = self.addPanel(1, 0, rowspan = 1, columnspan = 1)#, background = "white")
        
        self.pRight = self.addPanel(1, 2, rowspan = 1, columnspan = 1)#, background = "white")
        self.pBottom = self.addPanel(2, 0, rowspan = 1, columnspan = 3)#, background = "lightgrey")

        #pTop
        self.lblStatus = self.pTop.addLabel(text = "Welcome to Tic Tac Toe!", row = 0, column = 0, \
                                            sticky = "nsew", foreground = "black", background = "lightgrey", \
                                            font=('Helvetica 24 bold'))
        self.lblPlayer = self.pTop.addLabel(text = "Player's turn will show here.", row = 1, column = 0, \
                                            sticky = "nsew", foreground = "black", font=('Helvetica 16 bold'))

        #pLeft
        tmp = self.pLeft.addLabel(text = "Player X Name", row = 0, column = 0, \
                            sticky = "sw")
        self.cmbPlayerX = self.pLeft.addCombobox("Player X", ["Player X","Computer"], row = 1, column = 0, \
                                                 sticky = "new")
        self.cmbPlayerX.bind("<KeyRelease>", self.comboLengthCheck)

        self.pLeft.addLabel(text = "Player O Name", row = 2, column = 0, \
                            sticky = "sw")
        self.cmbPlayerO = self.pLeft.addCombobox("Player O", ["Player O","Computer"], row = 3, column = 0, \
                                                 sticky = "new")
        self.cmbPlayerO.bind("<KeyRelease>", self.comboLengthCheck)

        #print(self.cmbPlayerX.getText(), self.cmbPlayerO.getText())

        self.pLeft.addLabel(text = "Board Size", row = 4, column = 0, sticky = "sw")
        # Had to edit ln 502 of breezypythongui.py for this to work properly!
        self.boardSize = self.pLeft.addRadiobuttonGroup(row = 5, column = 0)
        self.boardSize.config(bg = "white")
        defaultRB = self.boardSize.addRadiobutton("3 x 3")
        defaultRB.config(bg = "white")
        self.boardSize.addRadiobutton("5 x 5").config(bg = "white", state="normal")
        self.boardSize.addRadiobutton("7 x 7").config(bg = "white", state="normal")
        self.boardSize.setSelectedButton(defaultRB)
        

        self.pLeft.addLabel(text = "Computer Level", row = 6, column = 0, sticky = "sw")
        # Had to edit ln 502 of breezypythongui.py for this to work properly!
        self.difficulty = self.pLeft.addRadiobuttonGroup(row = 7, column = 0)
        self.difficulty.config(bg = "white")
        defaultRB = self.difficulty.addRadiobutton("Easy")
        defaultRB.config(bg = "white")
        self.difficulty.addRadiobutton("Hard").config(bg = "white")
        self.difficulty.setSelectedButton(defaultRB)

        #pRight
        self.pRight.addLabel(text = "Total Games Won", row = 0, column = 0, \
                            sticky = "sw")
        self.taScores = self.pRight.addTextArea(text = '', row = 1, column = 0, \
                                                width = 12, height = 15, wrap=WORD)
        self.taScores.config(state="disabled")
        self.taScores.grid(padx=0,pady=0)
        self.taScores.master.config(bg="white")

      

        #pBottom

        self.btnPlay = self.pBottom.addButton(text="Start Game", row = 0, column = 0, command = lambda: self.startGame(enable = True), state = NORMAL)
        self.btnPlay.grid(sticky = N+S+E+W)


        self.lblCounts = self.pBottom.addLabel(text = "", row = 0, column = 1, \
                                            sticky = "nsew", foreground = "black", font=('Helvetica 12 bold'))
        self.setCounts()

        self.btnExit = self.pBottom.addButton(text="Exit", row = 0, column = 2, command = lambda: self.on_closing(), state = NORMAL)
        self.btnExit.grid(sticky = N+S+E+W)
        
        self.lblStatus = self.pBottom.addLabel(text = "Status Text goes here!", row = 1, column = 0, columnspan = 3, \
                                            sticky = "nsew", foreground = "black", background = "lightgrey", font=('Helvetica 16 bold'))

        # Center board canvas.
        self.clearBoard(enable = False, size = 3)

    def startGame(self, enable):
        # don't let them just pass in empty names - update them...
        if self.cmbPlayerX.getText().strip() == '':
            self.cmbPlayerX.setText("Player X")            
        if self.cmbPlayerO.getText().strip() == '':
            self.cmbPlayerO.setText("Player O")

        boardSize = int(self.boardSize.getSelectedButton()["value"][0])
            
        self.clearBoard(enable, size = boardSize)

    def comboLengthCheck(self, event):
        tmp = event.widget.getText()
        if len(tmp) >= 12:
            event.widget.setText(tmp[0:11])

    def on_closing(self):
        # save the scores before closing window.
        self.saveScores()
        self.master.destroy()

    def setCounts(self):
        self.lblCounts.config(text = "Wins X: " + str(self.winsX) + \
                                     "   Draws: " + str(self.draws) + \
                                     "   Wins O: " + str(self.winsO))

        self.taScores.config(state="normal")
        self.taScores.setText("")
        mkl = sorted(self.highScores.items(), key=lambda x:x[0])
        sdic = dict(mkl)
        for (key, value) in sdic.items(): #self.highScores.items():
            self.taScores.appendText(str(key) + "\n  " + str(value) + " Wins\n")
        self.taScores.config(state="disabled")

    def updateScores(self, player):
        tmp = self.getPlayerName(player)
        if tmp in self.highScores:
            self.highScores[tmp] += 1
        else:
            self.highScores[tmp] = 1

    def saveScores(self):
        filename = "scores.dat"
        fileObj = open(filename, "wb")
        pickle.dump(self.highScores, fileObj)
        fileObj.close()

    def loadScores(self):
        filename = "scores.dat"
        if os.path.isfile(filename):
            fileObj = open(filename, "rb")
            while True:
                try:
                    self.highScores = pickle.load(fileObj)
                except EOFError:
                    fileObj.close()
                    break


    def getPlayerName(self, player):
        
        if player == "x":
            tmpX = self.cmbPlayerX.getText()
            if tmpX == "Computer":
                return "Computer X"
            else:
                return tmpX
        else:
            tmpO = self.cmbPlayerO.getText()
            if tmpO == "Computer":
                return "Computer O"
            else:
                return tmpO

    def clearBoard(self, enable = True, size = 3):        
        self.cBoard = self.addCanvas(canvas = GameBoardCanvas(self, size = size, \
                                                              playerturn = self.playerTurn, \
                                                              winner = self.winner, \
                                                              draw = self.draw), \
                                     row = 1, column = 1, rowspan = 1, columnspan = 1, \
                                     width = 300, height = 300, background = "yellow")
        self.cBoard.grid(sticky = "")
        self.cBoard.isActive = enable

        tmp = size
        if size > 3: tmp = 4
        self.lblStatus.config(text = "Place " + str(tmp) + " in a row.")

        self.cBoard.setNextPlayer()

        if enable == False:
            self.lblPlayer.config(text = "Click Start Game to begin!")


    def winner(self, player):
        tmp = player.upper()
        #print("Winner! ", tmp)
        if tmp == "X":
            self.winsX += 1
        else:
            self.winsO += 1
        self.updateScores(player)
        self.setCounts()
        self.lblPlayer.config(text = "Click Start Game to play again!")
        self.lblStatus.config(text = self.getPlayerName(player) + " is the Winner!")
        self.update()        

    def draw(self):
        #print("Draw!")
        self.draws += 1
        self.setCounts()
        self.lblPlayer.config(text = "Click Start Game to play again!")
        self.lblStatus.config(text = "It's a Draw!")
        self.update()

    def playerTurn(self, player):
        #print("It is " + player.upper() + "'s Turn!")
        self.lblPlayer.config(text = "It is " + self.getPlayerName(player) + "'s Turn!")
        self.update()
        
        # is this turn a computer player? if so - take the turn for the computer!
        if (self.cmbPlayerX.getText() == "Computer" and player == "x") or \
           (self.cmbPlayerO.getText() == "Computer" and player == "o"):
            cpuai = self.difficulty.getSelectedButton()["value"]
            self.cBoard.takeComputerTurn(cpuai)


class TicTacToe():

    def __init__(self, size = 3):

        self.scoreLines = self.setScoreLines(size)

        self.winSize = size
        if size > 3: self.winSize = 4

    def setScoreLines(self, size):
        lst = list()

        #output list of list of row spaces
        for r in range(0, size):
            rowstart = ((size * r) + 1)
            tmp = list()
            for c in range(rowstart, rowstart + size):
                tmp.append(c)
            lst.append(tmp)

        #output list of list of column spaces
        for c in range(0, size):
            colstart =  c + 1
            tmp = list()
            for r in range(0, size):
                colspace = (colstart + (size * r))
                tmp.append(colspace)
            lst.append(tmp)

        #output list of list of left diagonal spaces
            tmp = list()
        for c in range(0, size):
            rowstart = ((size * c) + 1)    
            tmp.append(rowstart + c)
        lst.append(tmp)

        #output list of list of right diagonal spaces
        tmp = list()
        for c in range(size, 0, - 1):
            rowstart = ((size * c) + 1)    
            tmp.append(rowstart - c)
        lst.append(tmp)

        return lst

    def getEmptySpaces(self, state):
        """ take the state list and display only numbered (empty spaces)"""
        tmp = ''
        for i in state.values():
            if i != 'x' and i != 'o':
                tmp = tmp + i + '|'
        return tmp


    def isEmptySpace(self, state, space):
        return state[space] != 'x' and state[space] != 'o'


    def hasEmptySpace(self, state):
        return self.countEmptySpaces(state) != 0

    def countEmptySpaces(self, state):
        """return the number of spaces left to pick"""
        s = 0
        for i in state.values():
            if i != 'x' and i != 'o':
                s += 1
        return s

    
    def pickEmptySpace(self, state):
        """pick a random empty space"""
        s = 0
        if self.hasEmptySpace(state) == False: return s

        top = len(state)
        while str(s) not in state.values():
            s = random.randint(1, top)
        return s

    def convertRunToFlatState(self, state, run, addspaces = False):
        lst = list()
        tmpspc = ""
        if addspaces: tmpspc = " "
        for space in run:
            tmp = state[space]
            if tmp != "x" and tmp != "o":
                tmp = tmpspc
            lst.append(tmp)
        return lst

    def pickMoveRunN(self, state, player):
        """pick a space based on player id find token run or split run H/V/D"""
        s = 0

        runLen = math.sqrt(len(state))
        enemy = "x"
        if player == "x":
            enemy = "o"

        plrpat = list()
        for c in range(4):
            tmps = ""
            for r in range(4):
                if r == c:
                    tmps = tmps + " "
                else:
                    tmps = tmps + player
            plrpat.append(tmps)

        for run in self.scoreLines:

            if s != 0:
                break
            
            lst = self.convertRunToFlatState(state, run, addspaces=True)

            # Find a line where player fills all but 1 space

            if " " in lst and player in lst:
                if runLen <= 3:
                    # If there are no free spaces, or more than one, or enemy in line, or player not in line
                    if lst.count(" ") > 1 or enemy in lst:
                        continue

                    i = lst.index(" ")
                    s = run[i]
                else: # board Size over 3 only need 4 in a row
                    tmp = "".join(map(str, lst))

                    for match in plrpat:
                        i = tmp.find(match)
                        if i == -1:
                            continue
                        else:
                            tf = match.index(" ")
                            #print(match, tmp, run[i + tf])
                            s = run[i + tf]
                            break

        #if s != 0: print("pickMoveRunN:", s, "Player:",player)
        return s

    def pickEmptyRowSpaceN(self, state):
        """pick a space in the middle of an empty run"""
        s = 0

        runLen = int(math.sqrt(len(state)))

        for run in self.scoreLines:

            if s != 0:
                break
            
            lst = self.convertRunToFlatState(state, run)

            if lst.count("") != runLen:
                continue

            i = runLen // 2
            s = run[i]

        #if s != 0: print("pickEmptyRowSpaceN:", s, "Player:",player)
        return s        

    def computerPickAdvanced(self, state, player, nextplayer):
        """return a blocking move, winning move, an empty row move, or a random move based on state"""
        p1 = player
        p2 = nextplayer
        s = 0

        # check for a winning move space for player 1 (run missing 1)
        s = self.pickMoveRunN(state, p1)
        if s == 0:
            # check for a blocking move - pass in player 2 to find the space to block
            s = self.pickMoveRunN(state, p2)
            if s == 0:
                # check for an empty row move
                s = self.pickEmptyRowSpaceN(state)
                if s == 0:
                    # pick a random move
                    s = self.pickEmptySpace(state)
        return s


    def checkDraw(self, state):
        """check if no empty spaces are left"""
        return self.countEmptySpaces(state) == 0

    def getWinSize(self):
        return self.winSize

    def checkWinnerN(self, state, player):
        """Check for a winning row"""
        runLen = int(math.sqrt(len(state)))

        for run in self.scoreLines:

            lst = self.convertRunToFlatState(state, run, addspaces=True)

            if runLen <= 3:
                if lst.count(player) != runLen:
                    continue
            else:
                tmp = "".join(map(str, lst))
                #print(tmp)
                if player*4 not in tmp:
                    continue

            return True

        return False




def main():
    #print("Starting up!")
    root = GameBoard()
    root.master.protocol("WM_DELETE_WINDOW", root.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
