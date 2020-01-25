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
            return [(1, 1), (6, 2), (0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 2), (2, 2), (0, 3), (1, 3)]
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
        bestFood = foods[0]     #why did you name this best food? (Gabe)
        shortest = 1000
        for food in foods:
          dist = stepsToReach(currentState, myTunnel.coords, food.coords)
          if (dist < shortest):
            self.myFood = food
            shortest = dist
        
        #TODO: Figure out a way for agents to go around each other. 
        #AI agent handling workers.
        myWorkers = getAntList(currentState, me, (WORKER,))
        #nextState = getNextStateAdversarial(currentState, )
        #workerNumber = 0
        for w in myWorkers:
          #Make sure that we haven't already moved
          if not w.hasMoved:
            #If we are carrying food, bring it back to the tunnel
            if w.carrying:
              #we must check every worker and the distance between the anthill and the tunnel. 
              #in order to decide which one is quicker to go to. 
              distanceToTunnel = stepsToReach(currentState, w, myTunnel.coords)
              distanceToHill = stepsToReach(currentState, w, myHill.coords)
              if distanceToTunnel > distanceToHill:
                pathToHill = createPathToward(currentState, w.coords, myHill.coords, UNIT_STATS[WORKER][MOVEMENT])
                pathToTunnel = createPathToward(currentState, w.coords, myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, pathToHill, None)
              else:
                pathToTunnel = createPathToward(currentState, w.coords, myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                pathToHill = createPathToward(currentState, w.coords, myHill.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, pathToTunnel, None)
              #path = createPathToward(currentState, w.coords, myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
              #return Move(MOVE_ANT, path, None)
            #Otherwise, we want to move toward the food
            else:
              distanceToFood1 = stepsToReach(currentState, w, foods[0])
              distanceToFood2 = stepsToReach(currentState, w, foods[1])
              if distanceToFood1 > distanceToFood2:
                pathToFood = createPathToward(currentState, w.coords, foods[1].coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, pathToFood, None)
              else:
                pathToFood = createPathToward(currentState, w.coords, foods[0].coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, pathToFood, None)
              
        #AI agent handling Soldiers
        mySoldiers = getAntList(currentState, me, (SOLDIER,))
        for s in mySoldiers:
          if not s.hasMoved:
            path = createPathToward(currentState, s.coords, foeTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)
        if (not myInv.getQueen().hasMoved) and (not myInv.getQueen().coords == (0, 0)):
          path = createPathToward(currentState, myInv.getQueen().coords, (0, 0), UNIT_STATS[QUEEN][MOVEMENT])
          return Move(MOVE_ANT, path, None)
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
        #Will check what ants the opponent has. 
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]
        #myPlayerID = currentState.whoseTurn

        '''
        if myPlayerID == 0:
            numberOfSoldiers = getAntList(currentState, 1, SOLDIER,)  #3
            numberOfWorkers = getAntList(currentState, 1, WORKER,)   #1
            numberOfDrones = getAntList(currentState, 1, DRONE,)    #2
            numberOfRanged = getAntList(currentState, 1, R_SOLDIER,)    #4
        else:
            numberOfSoldiers = getAntList(currentState, 0, SOLDIER,)
            numberOfWorkers = getAntList(currentState, 0, WORKER,)
            numberOfDrones = getAntList(currentState, 0, DRONE,)
            numberOfRanged = getAntList(currentState, 0, R_SOLDIER,)
        '''

        '''
         if attackingAnt == SOLDIER:
            for ant in enemyLocations:
                if ant == QUEEN:
                    return enemyLocations[ant]
                elif ant == SOLDIER or DRONE:
                    return enemyLocations[ant]
                elif ant == R_SOLDIER or WORKER:
                    return enemyLocations[ant]
       '''



       #return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
