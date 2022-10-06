import random
import threading
from threading import Thread
import numpy as np
import tensorflow as tf
import PySimpleGUI as sg
from scipy.interpolate import interp1d

from scipy.signal import convolve2d

from agent import Agent
from dqn.abGame import Minimax
from game import Game

import json


class Window(Thread):
    def __init__(self, grid):
        self.grid = np.array(grid)
        Thread.__init__(self)

    def _update(self, grid):
        for circle in range(len(self.ui_grid)):
            if np.array(grid).flatten()[circle] == -1:
                c_fill = "Red"
            elif np.array(grid).flatten()[circle] == 1:
                c_fill = "Orange"
            else:
                c_fill = "White"
            self.window['canvas'].TKCanvas.itemconfig(self.ui_grid[circle], fill=c_fill)
            event, values = self.window.read(timeout=0)

    def run(self):
        self.layout = [
            [sg.Canvas(size=(280, 240), background_color='blue', key='canvas')]
        ]
        self.window = sg.Window('Connect 4 Test', self.layout, finalize=True)
        self.ui_grid = []
        for x in range(0, 6):
            for i in range(0, 7):
                self.ui_grid.append(
                    self.window['canvas'].TKCanvas.create_oval(i * 40, x * 40, 39 + i * 40, 39 + x * 40, width=2,
                                                               outline="Blue"))
        while True:
            self._update(self.grid)


class TimeStep:
    def __init__(self, reward, observation):
        self.reward = reward
        self.observation = observation


class NeuralNetwork:
    hyperparams = {
        "num_iterations": 20000,
        "initial_collect_steps": 100,
        "collect_steps_per_iteration": 1,
        "replay_buffer_max_length": 100000,

        "batch_size": 512,
        "learning_rate": 1e-3,
        "log_interval": 200,

        "num_eval_episodes": 10,
        "eval_interval": 1000,
        "epsilon": 1.0,
        "epsilon_decay": 0.999,
        "epsilon_min": 0.01,
        "gamma": 0.5
    }

    # Observation - Array of 42 ints
    # Reward - 0 - 1 Float
    # Action - 7 integers (columns)

    # https://colab.research.google.com/github/tensorflow/agents/blob/master/docs/tutorials/1_dqn_tutorial.ipynb#scrollTo=TgkdEPg_muz

    def __init__(self):
        self.game = Game()
        self.abGame = Minimax(self.game.grid)
        self.environment = np.array(self.game.grid).flatten()
        self.env_shape = (None, 42)
        print(self.environment)

    def env_calculate_reward(self, player):
        self.environment = np.array(self.game.grid)
        horizontal_kernel = np.array([[1, 1, 1, 1]])
        vertical_kernel = np.transpose(horizontal_kernel)
        diag1_kernel = np.eye(4, dtype=np.uint8)
        diag2_kernel = np.fliplr(diag1_kernel)
        detection_kernels = [horizontal_kernel, vertical_kernel, diag1_kernel, diag2_kernel]

        kernels = self.game.detection_kernels
        kernel_max = []
        for i in range(0, len(kernels)):
            k_max = np.max(convolve2d(self.environment == player, kernels[i], mode="valid"))
            kernel_max.append(k_max)

        kernel_max_2 = []
        for i in range(0, len(kernels)):
            k_max = np.max(convolve2d(self.environment == -player, kernels[i], mode="valid"))
            kernel_max_2.append(k_max)

        kernel_max = np.array(kernel_max).max()
        kernel_max_2 = np.array(kernel_max_2).max()
        total_board_pieces = np.count_nonzero(self.environment)
        # Reward increases when there are less pieces on the board and when there are more than 2 pieces in a row
        reward = 0
        reward += kernel_max * 0.20
        reward -= total_board_pieces / 42
        reward -= kernel_max_2 * 0.30
        reward = np.clip(reward, -1, 1)

        return reward, kernel_max, kernel_max_2

    def env_reset(self):
        self.game = Game()
        state = np.array(self.game.grid)
        return state

    def time_step(self, action, player_id):

        self.game.update_only(self.abGame.bestMove(3,self.game.grid, -player_id), -player_id)
        self.game.update_only(action, player_id)
        reward, max_connects, max_connects_2 = self.env_calculate_reward(player_id)
        #self.game.update_ai(player_id)
        state = np.array(self.game.grid)
        done = (max_connects == 4 or max_connects_2 == 4 or not np.all((self.environment[0] == 0)))

        return state, reward, done

    def train(self, agent: Agent):
        th = Window(self.game.grid)
        th.start()

        for ep in range(self.hyperparams["num_iterations"]):
            done, total_reward = False, 0
            state = self.env_reset()
            while not done:
                th.grid = self.game.grid
                action = agent.model.state_action(state)
                next_state, reward, done = self.time_step(action, agent.player_id)
                agent.buffer.put(state, action, reward * 0.01, next_state, done)
                total_reward += reward
                state = next_state

            if agent.buffer.length() >= self.hyperparams["batch_size"]:
                agent.replay()
            agent.target_update()
            print('EP{} EpisodeReward={}'.format(ep, total_reward))

            if ep % 100 == 0:
                with open('C:/DQNC4/models/model.save/data.json', 'w', encoding='utf-8') as f:
                    json.dump(self.hyperparams, f, ensure_ascii=False, indent=4)
                    agent.model.model.save("C:/DQNC4/models/model.save")



if __name__ == "__main__":
    # Training mode
    neuralNetwork = NeuralNetwork()
    agent = Agent(neuralNetwork.environment, neuralNetwork.hyperparams, 1, save=True)

    neuralNetwork.train(agent)
