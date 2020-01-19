import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Smart")
    
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            return [(0, 0), (4, 2), (0, 3), (0, 2), (0, 1), (1, 2), (1, 1), (1, 0), (2, 1), (2, 0), (3, 0)]
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            tunnels = getConstrList(currentState, types = (TUNNEL,))
            foeTunnel = tunnels[0] if (tunnels[0].coords[1] > 5) else tunnels[1]
            fTx = foeTunnel.coords[0]
            fTy = foeTunnel.coords[1]
            x = 0 if fTx > 4 else 9
            y = 6 if fTy > 7 else 9
            moves = []
            foodToPlace = 2
            while foodToPlace > 0:
              if currentState.board[x][y].constr == None:
                moves.append((x, y))
                x += 1 if (x == 0) else -1
                foodToPlace -= 1
              else:
                x += 1 if (x == 0) else -1
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        tunnels = getConstrList(currentState, types = (TUNNEL,))
        myTunnel = tunnels[1] if (tunnels[0].coords[1] > 5) else tunnels[0]
        foeTunnel = tunnels[0] if (myTunnel is tunnels[1]) else tunnels[1]
        hills = getConstrList(currentState, types = (ANTHILL,))
        myHill = hills[1] if (hills[0].coords[1] > 5) else hills[0]
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn
        moves = listAllLegalMoves(currentState)
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        foods = getConstrList(currentState, None, (FOOD,))
        bestFood = foods[0]
        shortest = 1000
        for food in foods:
          dist = stepsToReach(currentState, myTunnel.coords, food.coords)
          if (dist < shortest):
            self.myFood = food
            shortest = dist
        myWorkers = getAntList(currentState, me, (WORKER,))
        for w in myWorkers:
          #Make sure that we haven't already moved
          if not w.hasMoved:
            #If we are carrying food, bring it back to the tunnel
            if w.carrying:
              path = createPathToward(currentState, w.coords, myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
              return Move(MOVE_ANT, path, None)
            #Otherwise, we want to move toward the food
            else:
              path = createPathToward(currentState, w.coords, bestFood.coords, UNIT_STATS[WORKER][MOVEMENT])
              return Move(MOVE_ANT, path, None)
        mySoldiers = getAntList(currentState, me, (SOLDIER,))
        for s in mySoldiers:
          if not s.hasMoved:
            path = createPathToward(currentState, s.coords, foeTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)
        if (not myInv.getQueen().hasMoved):
          return moves[0]
        if myInv.foodCount >= 1 and len(myWorkers) < 2:
          return Move(BUILD, [myHill.coords], WORKER)
        if myInv.foodCount >= 2 and len(mySoldiers) < 2:
          return Move(BUILD, [myHill.coords], SOLDIER)
        return Move(END, None, None)
    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass