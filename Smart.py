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
        foeHill = hills[1] if (myHill is hills[0]) else hills[0]
        myInv = getCurrPlayerInventory(currentState)
        enemyInv = getEnemyInv(self, currentState)
        me = currentState.whoseTurn
        #0-1 = |-1|, 1 - 1 - 0
        enemy = abs(me - 1)
        moves = listAllLegalMoves(currentState)
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        foods = getConstrList(currentState, None, (FOOD,))
        
        #TODO: Figure out a way for agents to go around each other. 
        #AI agent handling workers.
        myWorkers = getAntList(currentState, me, (WORKER,))
        #workerNumber = 0
        for w in myWorkers:
          #Make sure that we haven't already moved
          if not w.hasMoved:
            #If we are carrying food, bring it back to the tunnel
            if w.carrying:
              #we must check every worker and the distance between the anthill and the tunnel. 
              #in order to decide which one is quicker to go to. 
              distanceToTunnel = stepsToReach(currentState, w.coords, myTunnel.coords)
              distanceToHill = stepsToReach(currentState, w.coords, myHill.coords)
              if distanceToTunnel > distanceToHill:
                pathToHill = createPathToward(currentState, w.coords, myHill.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, self.checkPath(currentState, pathToHill, w), None)
              else:
                pathToTunnel = createPathToward(currentState, w.coords, myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, self.checkPath(currentState, pathToTunnel, w), None)
            #Otherwise, we want to move toward the food
            else:
              distanceToFood = []
              for f in foods:
                distanceToFood.append(stepsToReach(currentState, w.coords, f.coords))
              min_dist = 1000
              idx = 0
              for i in range(len(distanceToFood)):
                if distanceToFood[i] < min_dist:
                  min_dist = distanceToFood[i]
                  idx = i
              pathToFood = createPathToward(currentState, w.coords, foods[idx].coords, UNIT_STATS[WORKER][MOVEMENT])
              return Move(MOVE_ANT, self.checkPath(currentState, pathToFood, w), None)
              
        #AI agent handling Soldiers
        mySoldiers = getAntList(currentState, me, (SOLDIER,))
        myDrones = getAntList(currentState, me, (DRONE,)) 
        enemyAnts = getAntList(currentState, enemy, (WORKER, DRONE, SOLDIER, R_SOLDIER,))
        #Sends the soldiers to the foe's tunnel to try and interrupt food collection
        tunnelCount = 0
        for s in mySoldiers:
          if s.hasMoved:
            tunnelCount += 1
          else:
            #path = createPathToward(currentState, s.coords, foeTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
            #if tunnelCount >= 2:
            path = createPathToward(currentState, s.coords, foeHill.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)

        #put ranged soldiers next to queen; should only be 2. 
        enemyAnt = self.enemyAtOurBase(currentState, enemyAnts)
        for ant in myDrones:
          if not ant.hasMoved:
            if enemyAnt != None:
              #create a path towards the enemy ants. 
              path = createPathToward(currentState, ant.coords, enemyAnt.coords, UNIT_STATS[DRONE][MOVEMENT])
              return Move(MOVE_ANT, path, None)
            else:
              path = createPathToward(currentState, ant.coords, (0, 1), UNIT_STATS[DRONE][MOVEMENT])
              return Move(MOVE_ANT, path, None)

        #deal with queen
        if (not myInv.getQueen().hasMoved) and (not myInv.getQueen().coords == (0, 0)):
          path = createPathToward(currentState, myInv.getQueen().coords, (0, 0), UNIT_STATS[QUEEN][MOVEMENT])
          return Move(MOVE_ANT, path, None)

        #create a worker if we have enough food and we have less than 2 workers
        if myInv.foodCount >= 1 and len(myWorkers) < 2 and getAntAt(currentState, myHill.coords) == None:
          return Move(BUILD, [myHill.coords], WORKER)

        #create a drone to protect queen. 
        if myInv.foodCount >= 2 and len(myDrones) < 1 and getAntAt(currentState, myHill.coords) == None:
          return Move(BUILD, [myHill.coords], DRONE)
        
        if myInv.foodCount >= 2 and len(myDrones) == 1 and len(mySoldiers) < 10 and getAntAt(currentState, myHill.coords) == None:
          return Move(BUILD, [myHill.coords], SOLDIER)

        return Move(END, None, None)

    #TODO: Deal with wall collisions
    #w = worker
    def checkPath(self, currentState, path, w):
      next_path = path[1::]
      if len(next_path) == 0:
        next_move = (w.coords[0], w.coords[1] - 1)
        if getAntAt(currentState, next_move) is None and legalCoord(next_move):
          return [w.coords, next_move]
        next_move = (w.coords[0], w.coords[1] + 1)
        if getAntAt(currentState, next_move) is None and legalCoord(next_move):
          return [w.coords, next_move]
        next_move = (w.coords[0] - 1, w.coords[1])
        if getAntAt(currentState, next_move) is None and legalCoord(next_move):
          return [w.coords, next_move]
        next_move = (w.coords[0] + 1, w.coords[1])
        if getAntAt(currentState, next_move) is None and legalCoord(next_move):
          return [w.coords, next_move]
      return path


    #Method for returning an ant that is in our territory. 
    #Paramaters 
    def enemyAtOurBase(self, currentState, enemyAnts):
      for ant in enemyAnts:
        if ant.coords[0] <= 9 and ant.coords[1] <= 3:
          return ant
        else:
          return None
    
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
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]


    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
