#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 14:31:41 2022

@author: varun
"""

import random

def nim_sum(arr): # calculates the nim sum of all the elements in an array
    ret = 0
    for i in arr:
        ret ^= i
    return ret

# states are represented as arrays (ex: [2, 2, 2] means 3 piles each with 2 stones)
# actions are represented as arrays of length 2 (ex: [1, 4] means removing 4 stones from the 1st pile)
# q tables are represented as 2D dictionaries, where q[state][action] is a number between -1 and 1
class nim: # nim environment (controls the mechanics of the game)
    def __init__(self, initial_stones_per_pile, piles): # initializes a nim game 
        self.n = piles
        self.m = initial_stones_per_pile
        self.state = []
        self.state = [self.m] * self.n
        self.player = 1
        self.template = {}
        
    def getState(self): # returns the current state of the game
        return self.state.copy()
        
    def getPossActions(self, state): # returns the possible actions from a given state
        ret = []
        for i in range(0, self.n):
            for j in range (1, state[i] + 1):
                ret.append([i, j])
        return ret
    
    def getNewActions(self, state, table): # returns the unvisited actions from a given state
        ret = []
        for i in range(0, self.n):
            for j in range (1, state[i] + 1):
                if table[tuple(state)][tuple([i, j])] == 0.0:
                    ret.append([i, j])
        return ret
    
    def playMove(self, action): # "plays" an action by updating the state
        self.state[action[0]] -= action[1]
    
    def gameOver(self): # returns true if the game is over, false otherwise
        return self.state == [0] * self.n
    
    def getPlayer(self): # returns the player whose turn it is
        return self.player
    
    def switchPlayer(self): # switches the player whose turn it is
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
    
    def recursion(self, ind, s): # recursive function called in getTemplate
        if ind == 0:
            self.template[tuple(s)] = {}
            for a in self.getPossActions(s):
                self.template[tuple(s)][tuple(a)] = 0.0
            return

        for i in range(0, self.m + 1):
            t = s.copy()
            t.append(i)    
            self.recursion(ind-1, t)
        
    def getTemplate(self): # returns a template for the q table (given the possible states) with everything set to 0
        for i in range(0, self.m + 1):
            arr = []
            arr.append(i)
            self.recursion(self.n - 1, arr)       
        return self.template

    def reset(self): # resets the game so we can play again
        self.state = [self.m] * self.n
        self.player = 1

    def getPiles(self):  # returns number of piles
        return self.n

    def getInitialStonesPerPile(self): # returns initial stone per pile
        return self.m


class q_agent: # q agent
    def __init__(self, game, learning_rate): # initializes a q agent which can play in a specified game
        self.game = game
        self.qtable = self.game.getTemplate().copy()
        self.alpha = learning_rate
        self.epsilon = 1.0
        self.wins = []
        self.strat_error = []
    
    def setTable(self, qtable): # sets the agent's qtable (default is all 0's)
        self.qtable = qtable
    
    def getTable(self): # returns the agent's qtable
        return self.qtable

    def bestAction(self, state): # returns the best action from a given state according to the q table
        best_actions = []
        max_val = -2.0
        for action in self.game.getPossActions(state):
            if self.qtable[tuple(state)][tuple(action)] > max_val:
                best_actions.clear()
                best_actions.append(action)
                max_val = self.qtable[tuple(state)][tuple(action)]
            
            elif self.qtable[tuple(state)][tuple(action)] == max_val:
                best_actions.append(action)
        k = len(best_actions)
        ind = random.randint(0, k-1)      
        return best_actions[ind]
    
    def getAction(self, state): # chooses an action based on exploration(random action) vs exploitation(bestAction) 
        x = random.random()
        
        if x < self.epsilon:
            #print("explore")
            poss_actions = self.game.getNewActions(state, self.qtable)
            if len(poss_actions) == 0:
                poss_actions = self.game.getPossActions(state) 
            k = len(poss_actions)
            ind = random.randint(0, k-1)
            #print(self.qtable[tuple(state)][tuple(poss_actions[ind])])
            return poss_actions[ind]
        else:
            #print("exploit")
            return self.bestAction(state)
    
    def updateTable(self, state, action, new_state, reward): # updates the q table using the Bellman learning equation
        old = self.qtable[tuple(state)][tuple(action)]
        new = reward
        if new_state != [0] * self.game.n:
            new += self.qtable[tuple(new_state)][tuple(self.bestAction(new_state))]
        self.qtable[tuple(state)][tuple(action)] = old + self.alpha * (new - old)
        #print("updating: state = {0}, action = {1}, new state = {2}".format(state, action, new_state))
        #print("          old = {0}, q[ns][na] = {1}, reward = {2}, new = {3}".format(old, new - reward, reward, self.qtable[tuple(state)][tuple(action)]))
    
    def setEpsilon(self, new_exploration_rate): # sets the tendency to explore rather than exploit
        self.epsilon = new_exploration_rate
    
    def getEpsilon(self): # returns the exploration rate
        return self.epsilon
    
    def isQ(self): # tells us that this agent is a q agent
        return True
    
    # the following four methods deal with making win rate and strategy graphs
    def addWin(self, win): 
        if win:
            self.wins.append(1.0)
        else:
            self.wins.append(0.0)
    
    def getWins(self):
        return self.wins
    
    def addStratError(self, state, action, new_state):
        if nim_sum(new_state) == 0:
            self.strat_error.append(1.0)
        elif nim_sum(state) != 0:
            self.strat_error.append(0.0)
    
    def getStratError(self):
        return self.strat_error

class opp_agent: # all agents that do not learn, similar to the q agent but the q table does not change
    
    def __init__(self, game): # initializes an opponent agent which plays in a specified game
        self.game = game    
        self.qtable = self.game.getTemplate().copy()

    def setTable(self, qtable): # sets the agent's q table
        self.qtable = qtable
    
    def getTable(self): # returns the agent's q table
        return self.qtable
    
    def getAction(self, state): # chooses the best action according to the q table
        best_actions = []
        max_val = 0
        for action in self.game.getPossActions(state):
            if self.qtable[tuple(state)][tuple(action)] > max_val:
                best_actions.clear()
                best_actions.append(action)
                max_val = self.qtable[tuple(state)][tuple(action)]
            elif self.qtable[tuple(state)][tuple(action)] == max_val:
                best_actions.append(action)
        k = len(best_actions)
        ind = random.randint(0, k-1)      
        return best_actions[ind]
    
    def isQ(self): # tells us that this agent is not a q agent
        return False

def playGame(game, agent1, agent2): # playing one game between two agents
    # this decides which player starts with equal probability
    swap_starter = random.random()
    if swap_starter < 0.5:
        game.switchPlayer()
    
    agent = agent1
    old_agent = -1
    old_state = -1
    old_action = -1
    while True: # in each iteration of this loop an agent plays a move and learns if necessary
        # discerns which player is playing the game
        if game.getPlayer() == 1:
            agent = agent1
        else:
            agent = agent2
        
        state = game.getState() # gets the current state from the environment     
        action = agent.getAction(state) # gets the chosen action by the agent 
        game.playMove(action) # the environment plays the action
        new_state = game.getState() # gets the new state
        #print("player {0} made move {1} from state {2} to state {3}".format(game.getPlayer(), action, state, new_state))
        
        # graphing stuff
        if agent.isQ():
            agent.addStratError(state, action, new_state)
        
        # breaks out of the loop of the game is over
        if game.gameOver():
            break
        
        # the old agent updates its q table if it is a q agent
        if old_agent != -1 and old_agent.isQ():
            old_agent.updateTable(old_state, old_action, new_state, 0)
        
        game.switchPlayer() # the player whose turn it is changes
        old_state = state
        old_action = action
        old_agent = agent
    
    # once the game is over, the winner learns from a positive reward and the loser from a negative one
    if game.getPlayer() == 1:
        #print("gg: player 1 won")
        if agent1.isQ():
            agent1.updateTable(state, action, new_state, 1)
            agent1.addWin(True)
        if agent2.isQ():
            agent2.updateTable(old_state, old_action, new_state, -1)
            agent2.addWin(False)
    else:
        #print("gg: player 2 won")
        if agent2.isQ():
            agent2.updateTable(state, action, new_state, 1)
            agent2.addWin(True)
        if agent1.isQ():
            agent1.updateTable(old_state, old_action, new_state, -1)
            agent1.addWin(False)
    
    game.reset() # game's state is reset