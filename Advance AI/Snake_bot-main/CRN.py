import pygame
import numpy as np
from collections import deque

# Game settings
GRID_SIZE = 20
WIDTH = 400
HEIGHT = 400
FPS = 10

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.snake = deque([(100, 100), (90, 100), (80, 100)])
        self.food = self.spawn_food()
        self.direction = (GRID_SIZE, 0)
        self.score = 0
        return self.get_state()

    def spawn_food(self):
        while True:
            food = (np.random.randint(0, WIDTH // GRID_SIZE) * GRID_SIZE,
                    np.random.randint(0, HEIGHT // GRID_SIZE) * GRID_SIZE)
            if food not in self.snake:
                return food

    def step(self, action):
        self.update_direction(action)
        head = self.get_next_position()
        
        # Check for game over conditions
        if self.is_collision(head):
            return self.get_state(), -10, True

        # Update the snake's position
        self.snake.appendleft(head)
        reward = 0
        if head == self.food:
            reward = 10
            self.food = self.spawn_food()
            self.score += 1
        else:
            self.snake.pop()

        return self.get_state(), reward, False

    def update_direction(self, action):
        if action == 0:  # UP
            self.direction = (0, -GRID_SIZE)
        elif action == 1:  # RIGHT
            self.direction = (GRID_SIZE, 0)
        elif action == 2:  # DOWN
            self.direction = (0, GRID_SIZE)
        elif action == 3:  # LEFT
            self.direction = (-GRID_SIZE, 0)

    def get_next_position(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        return head_x + dx, head_y + dy

    def is_collision(self, position):
        x, y = position
        return (x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT or position in self.snake)

    def get_state(self):
        # Return a simple representation of the environment (distance and obstacles)
        state = np.zeros((WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE))
        for x, y in self.snake:
            state[x // GRID_SIZE, y // GRID_SIZE] = 1
        fx, fy = self.food
        state[fx // GRID_SIZE, fy // GRID_SIZE] = 2
        return state.flatten()

    def render(self):
        self.display.fill((0, 0, 0))
        for x, y in self.snake:
            pygame.draw.rect(self.display, (0, 255, 0), (x, y, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.display, (255, 0, 0), (*self.food, GRID_SIZE, GRID_SIZE))
        pygame.display.flip()
        self.clock.tick(FPS)


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import random

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self.build_model()

    def build_model(self):
        model = Sequential([
            Dense(24, input_dim=self.state_size, activation='relu'),
            Dense(24, activation='relu'),
            Dense(self.action_size, activation='linear')
        ])
        model.compile(optimizer=Adam(learning_rate=self.learning_rate), loss='mse')
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state, verbose=0)
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


EPISODES = 1000

if __name__ == "__main__":
    env = SnakeGame()
    state_size = env.get_state().shape[0]
    action_size = 4  # UP, RIGHT, DOWN, LEFT
    agent = DQNAgent(state_size, action_size)
    batch_size = 32

    for e in range(EPISODES):
        state = env.reset().reshape(1, -1)
        for time in range(500):
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            next_state = next_state.reshape(1, -1)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            if done:
                print(f"Episode {e + 1}/{EPISODES}, Score: {env.score}, Epsilon: {agent.epsilon:.2f}")
                break
            if len(agent.memory) > batch_size:
                agent.replay(batch_size)
