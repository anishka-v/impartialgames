import numpy as np
import random
from nim_env import NimEnv
from nim_rl import QAgent

# 1 - Optimal, 2 - Mal, 3 - Population
# 4 - Random


"""
YouTube Approach

{
a - Percentage of times where youtube recommends the same "side" engine or player to q1
b - Percentage of times where youtube recommends something random to q1

[a, b]

[a, a+b]

random = np.random.rand()
if random < youtube_probability[0]:
    QvQ(env, q1, q1.get_side())
else:
    QvQ(env, q1, (not q1.get_side()))
}
"""


def population_train(people, num_pile, rounds=50000, probability=[0, 0, 1], discern_rate=0):
    for i in range(1, len(probability)):
        probability[i] = probability[i - 1] + probability[i]

    print(probability)

    for r in range(rounds):
        if r % 1000 == 0:
            print('Round: ', r)
            if r + 20000 >= rounds:
                RL1.set_epsilon(0)
                RL2.set_epsilon(0)
                RL3.set_epsilon(0)

        trained = 0

        rand = np.random.rand()
        piles = [3, 5, 7]

        p1 = np.random.randint(0, len(people))
        q1 = people[p1]
        env = NimEnv(len(piles), piles)
        q1.set_env(env)

        if rand < probability[0]:
            QvQ(env, q1, 'optimal')
            continue

        if rand < probability[1]:
            QvQ(env, q1, 'mal')
            continue

        while trained < len(people) // 2:
            p2 = np.random.randint(0, len(people))
            while p1 == p2:
                p2 = np.random.randint(0, len(people))

            q2 = people[p2]
            q2.set_env(env)

            QvQ(env, q1, q2)
            trained += 2

    for q in people:
        q.plot(q.get_name() + ' performance')


def QvQ(env, q1, oppo):
    env.reset()
    reward_q1 = 0

    while True:
        state = env.get_state()
        q1_action = q1.get_action(state)
        next_state = env.update(q1_action)

        if np.sum(next_state) == 0:
            ### q1 won
            reward_q1 = 1
            break

        state2 = next_state.copy()

        if oppo == 'random':
            actions = env.get_possible_actions(state2)
            action = random.choice(actions)
        elif oppo == 'optimal':
            actions = env.get_optimal_action(state2)
            action = random.choice(actions)
        elif oppo == 'mal':
            actions = env.get_mal_random_action(state2)
            action = random.choice(actions)
        else:
            raise Exception("Nim opponent strategy is not known: " + oppo)

        next_state = env.update(action)

        if np.sum(next_state) == 0:
            ### q1 lost
            reward_q1 = -1
            break

        q1.update_q_table(state, q1_action, reward_q1, next_state)

    ### HERE
    # Reward < 0, q1 loses, reward > 0, q1 wins
    # if q2 was mal
    # random float between 0 and 1
    # if random < dicerning rate, flagged

    ### this following update is after the game is won or lost
    q1.update_q_table(state, q1_action, reward_q1, next_state)

    q1.add_points()


def play(q, pile):
    env = NimEnv(len(pile), pile)
    env.reset()
    while True:
        print('Current Pile: ' + str(env.get_state()))

        pile = input('Enter Pile: ')
        amt = input('Enter Amount: ')

        env.update([int(pile) - 1, int(amt)])

        if np.sum(env.get_state()) == 0:
            print('Game Over You Win!')
            break

        print('Current Pile: ' + str(env.get_state()))

        action = q.get_action(env.get_state(), play=True)

        print('Computer chooses from pile ' + str(action[0] + 1) + ' with amount ' + str(action[1]))

        env.update(action)

        if np.sum(env.get_state()) == 0:
            print('Game Over Computer Wins')
            break

#
# probabilities:
#   0: random
#   1: optimal
#   2: mal-optimal
#
def train_qlearner(qagent, piles, rounds=50000, probability=[0, 0.5, 0.5]):
    for i in range(1, len(probability)):
        probability[i] = probability[i - 1] + probability[i]

    qlearner = QAgent('Q-Learner', discount_rate=0.9, learning_rate=0.5, epsilon=0.1, side=0)
    for r in range(rounds+1):
        if r % 5000 == 0: print('Round: ', r)

        env = NimEnv(len(piles), piles)
        qagent.set_env(env)

        rand = np.random.rand()
        if (rand <= probability[0]):
            QvQ(env, qagent, 'random')
        elif (rand <= probability[1]):
            QvQ(env, qagent, 'optimal')
        elif (rand <= probability[2]):
            QvQ(env, qagent, 'mal')

if __name__ == '__main__':
    RL1 = QAgent('Q1', discount_rate=0.9, learning_rate=0.5, epsilon=0.1, side=0)
    RL2 = QAgent('Q2', discount_rate=0.9, learning_rate=0.5, epsilon=0.1, side=1)
    RL3 = QAgent('Q3', discount_rate=0.9, learning_rate=0.5, epsilon=0.1, side=0)
    # population_train([RL1, RL2, RL3], 3, rounds=60000, probability=[0, 0.5, 0.5])

    piles = [3, 5, 7]
    train_qlearner(RL1, piles, rounds=10000, probability=[1.0, 0.00, 0.0])
    RL1.plot(RL1.get_name() + ': against random actions: ' + str(piles))
    train_qlearner(RL2, piles, rounds=10000, probability=[0, 1.00, 0.0])
    RL2.plot(RL2.get_name() + ': against optimal agents: ' + str(piles))
    train_qlearner(RL3, piles, rounds=10000, probability=[0, 0.00, 1.0])
    RL3.plot(RL3.get_name() + ': against mal-optimal agents: ' + str(piles))

    # while True:
    #     play(RL1, piles)
