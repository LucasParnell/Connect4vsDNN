import random
from collections import deque
from os.path import exists

import numpy
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from tensorflow.keras import backend


class Memory:
    def __init__(self, hyperparams, capacity=10000):
        self.buffer = deque(maxlen=capacity)
        self.hp = hyperparams

    def put(self, state, action, reward, next_state, done):
        self.buffer.append([state, action, reward, next_state, done])

    def sample(self):
        sample = random.sample(self.buffer, self.hp["batch_size"])
        states, actions, rewards, next_states, done = map(np.asarray, zip(*sample))
        states = np.array(states).reshape((self.hp["batch_size"], 1, 6, 7))
        tensor_states = tf.convert_to_tensor(states)
        tensor_states = tf.expand_dims(tensor_states, 0)
        tensor_states = tf.reshape(tensor_states, (self.hp["batch_size"], 1, 6, 7))

        next_states = np.array(next_states)
        tensor_next_states = tf.convert_to_tensor(states)
        tensor_next_states = tf.expand_dims(tensor_states, 0)
        tensor_next_states = tf.reshape(tensor_next_states, (self.hp["batch_size"], 1, 6, 7))
        return tensor_states, actions, rewards, tensor_next_states, done

    def length(self):
        return len(self.buffer)


class Model:
    # Create a callback that saves the model's weights

    def __init__(self, state_dim, action_dim, hyperparams, save=False):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hp = hyperparams
        self.save = save
        self.model = self.new_model()

    def new_model(self):
        model = keras.Sequential([
            layers.Conv2D(32, (2, 2), activation='relu', data_format='channels_first', input_shape=(1, 6, 7)),
            layers.Conv2D(64, (2, 2), activation='relu'),
            layers.Conv2D(64, (2, 2), activation='relu'),
            layers.Flatten(),
            layers.Dense(512, activation="relu"),
            layers.Dense(self.action_dim, activation='linear')
        ])
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=self.hp["learning_rate"]))


        return model

    def predict(self, state):
        state = state.reshape(1, 6, 7)
        state_tensor = tf.convert_to_tensor(state)
        state_tensor = tf.expand_dims(state_tensor, 0)
        return self.model.predict(state_tensor, verbose=0)

    def state_action(self, state):
        self.hp["epsilon"] *= self.hp["epsilon_decay"]
        self.hp["epsilon"] = max(self.hp["epsilon"], self.hp["epsilon_min"])
        q_val = self.predict(state)
        if np.random.random() < self.hp["epsilon"]:
            # If random float (0-1) is less than epsilon (Discovery Factor)
            # then return a random action as this indicates discoverye
            a = random.randint(0, self.action_dim - 1)
            return a
        # Filter q_val array by 0s
        filtered_q = q_val.copy()
        for i in range(0, filtered_q.shape[0]):
            for j in range(0, filtered_q.shape[1]):
                if state[i][j] != 0:
                    filtered_q[i][j] = -1

        # Remove all zero rows
        filtered_q = filtered_q[~np.all(filtered_q == 0, axis=1)]

        q_sum = filtered_q.sum(axis=0)
        return np.argmax(q_sum)


    def enemy_move(self, state):
        self.hp["epsilon"] *= self.hp["epsilon_decay"]
        self.hp["epsilon"] = max(self.hp["epsilon"], self.hp["epsilon_min"])
        q_val = self.predict(state)
        if np.random.random() < self.hp["epsilon"]:
            # If random float (0-1) is less than epsilon (Discovery Factor)
            # then return a random action as this indicates discoverye
            a = random.randint(0, self.action_dim - 1)
            return a
        # Filter q_val array by 0s
        filtered_q = q_val.copy()
        for i in range(0, filtered_q.shape[0]):
            for j in range(0, filtered_q.shape[1]):
                if state[i][j] != 0:
                    filtered_q[i][j] = -1

        # Remove all zero rows
        filtered_q = filtered_q[~np.all(filtered_q == 0, axis=1)]

        q_sum = filtered_q.sum(axis=0)
        return np.argmin(q_sum)

    def train(self, states, targets):
        self.model.fit(states, targets, epochs=1, verbose=0)


class Agent:
    def __init__(self, environment, hyperparams, player_id, save=False):
        self.hp = hyperparams
        self.environment = environment
        self.state_dim = (1, 6, 7)
        self.action_dim = 7
        self.player_id = player_id
        self.save = save
        self.model = Model(self.state_dim, self.action_dim, hyperparams, save=self.save)
        self.model_target = Model(self.state_dim, self.action_dim, hyperparams)

        # Target Update
        self.target_update()

        self.buffer = Memory(hyperparams)

    def replay(self):
        for _ in range(10):
            states, actions, rewards, next_states, done = self.buffer.sample()
            # Create array of targets, Iterate through states by x and add predictions to target array
            targets = self.model_target.model.predict(states, verbose=0)
            next_q_values = self.model_target.model.predict(next_states, batch_size=self.hp["batch_size"],
                                                            verbose=0).max(axis=1)
            targets[range(self.hp["batch_size"]), actions] = rewards + (1 - done) * next_q_values * self.hp["gamma"]
            self.model.train(states, targets)

    def target_update(self):
        weights = self.model.model.get_weights()
        self.model_target.model.set_weights(weights)
