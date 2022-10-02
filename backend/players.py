import ipaddress
import time
import uuid
from game import Game
import threading

class Player:
    def __init__(self):
        self.address = None
        self.game = Game()
        self.identifier = str(uuid.uuid4())
        self.lastPostTime = int(time.time())
        self.side = 0

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        return thread
    return wrapper


global playersSigned
playersSigned = []

class PlayerManager:


    def hasIdentifier(self, identifier):
        for entry in playersSigned:
            if entry.identifier == identifier:
                entry.lastPostTime = int(time.time())
                return entry
        return False

    def register(self, player):
        playersSigned.append(player)
        player.lastPostTime = int(time.time())

    def playerValid(self, identifier):
        for entry in playersSigned:
            if str(entry.identifier) == str(identifier):
                entry.lastPostTime = int(time.time())
                return True
        return False

    def playerUpdate(self, identifier, last):
        for entry in playersSigned:
            if entry.identifier == identifier:
                newGrid = entry.game.update(last)
                entry.lastPostTime = int(time.time())
                return newGrid

    def playerCheckWin(self, identifier):
        for entry in playersSigned:
            if entry.identifier == identifier:
                win = 0 #No win
                if entry.game.checkWin(1):
                    win = -1
                if entry.game.checkWin(-1):
                    win = 1
                return win

    def removePlayer(self, identifier):
        for entry in playersSigned:
            if entry.identifier == identifier:
                playersSigned.remove(entry)

    @threaded
    def hypervise(self):
        #Monitor player idle times
        while True:
            currentTime = int(time.time())
            for player in playersSigned:

                if currentTime - player.lastPostTime > 1800:
                    print("Removing Player for Idling, UUID: " + player.identifier)
                    playersSigned.remove(player)

                    #If player has not made a post request in 30 minutes (1800 seconds) remove them from the playersSigned list