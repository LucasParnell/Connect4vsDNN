import ipaddress
import json
import time
from urllib.parse import unquote

import players

from flask import Flask, request, abort
from flask_cors import CORS
app = Flask(__name__)

CORS(app)

playerManager = players.PlayerManager()
handle = playerManager.hypervise()
handle.start()
@app.route('/initPlayer', methods = ['POST'])
def initPlayer():
    data = request.get_json()
    uuid = data["uuid"]
    playerSide = data["playerSide"]
    player = playerManager.hasIdentifier(uuid)
    if not player or not uuid:
        player = players.Player()
        #Store player side incase refresh
        player.side = playerSide
        playerManager.register(player)

    print("New Player: " + str(player.identifier))
    return {"uuid": player.identifier, "grid": player.game.grid, "playerSide": player.side}

@app.route('/gameTurn', methods = ['POST'])
def gameTurn():
    data = request.get_json()
    uuid = data["uuid"]
    lastMove = data["lastMove"]

    if not playerManager.playerValid(uuid):
        print("Player with invalid identifier attempted to request a turn, Aborting")
        abort(403)
        return

    print("Update Player: " + uuid)




    win = 0


    aiMove: [int, int] = playerManager.playerUpdate(uuid, lastMove)
    win = playerManager.playerCheckWin(uuid)

    if win != 0:
        playerManager.removePlayer(uuid)

    return {"win": win, "newGrid": aiMove}








if __name__ == '__main__':
    app.run()
