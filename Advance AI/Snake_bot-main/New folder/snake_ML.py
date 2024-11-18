import pygame as pg
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import torch.nn.functional as F

# Hyperparameters
WINDOW = 400
TITLE = 20
RANGE = (TITLE // 2, WINDOW - TITLE // 2, TITLE)
ACTION_SPACE = 4  # UP, DOWN, LEFT, RIGHT
GAMMA = 0.95
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01
MEMORY_SIZE = 10000
BATCH_SIZE = 64
LEARNING_RATE = 0.001
TARGET_UPDATE = 10  # Episodes to update the target network
TIME_STEP = 110  # Milliseconds between movements

# Helper function to get random food position
def get_rand():
    return [random.randrange(*RANGE), random.randrange(*RANGE)]

# Set up the Pygame environment
import pygame as pg
import random
import numpy as np

class SnakeEnv:
    def __init__(self):
        # Initialize Pygame and create a display surface
        if not pg.get_init():
            pg.init()  # Initialize Pygame if not already done
        self.screen = pg.display.set_mode([400, 400])
        self.clock = pg.time.Clock()
        self.episode = 1
        self.reset()

    def reset(self):
        self.snake = pg.Rect([0, 0, 20 - 2, 20 - 2])
        self.snake.center = [random.randint(20, 380), random.randint(20, 380)]
        self.snake_dir = (20, 0)
        self.segments = [self.snake.copy()]
        self.length = 1
        self.food = pg.Rect([0, 0, 20 - 2, 20 - 2])
        self.food.center = [random.randint(20, 380), random.randint(20, 380)]
        self.score = 0

    def render(self):
        # Check if Pygame is initialized before rendering
        if not pg.display.get_init():
            raise RuntimeError("Pygame display not initialized. Ensure pg.init() and set_mode() are called.")
        
        # Clear the screen
        self.screen.fill((0, 0, 0))  # Black background
        pg.draw.rect(self.screen, (0, 0, 255), self.food)  # Blue food
        for segment in self.segments:
            pg.draw.rect(self.screen, (0, 255, 0), segment)  # Green snake
        
        # Render score and episode
        font = pg.font.Font(None, 32)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))  # White
        episode_text = font.render(f"Episode: {self.episode}", True, (255, 255, 255))  # White
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(episode_text, (10, 40))

        # Update the display
        pg.display.flip()

    def close(self):
        pg.quit()  # Cleanly close Pygame


# Define the Q-Network (DQN model)
class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(4, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, ACTION_SPACE)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


class DQNAgent:
    def __init__(self):
        self.model = DQN()
        self.target_model = DQN()
        self.target_model.load_state_dict(self.model.state_dict())
        self.optimizer = optim.Adam(self.model.parameters(), lr=LEARNING_RATE)
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.epsilon = 1.0

    def act(self, state):
        if random.random() < self.epsilon:
            return random.randrange(ACTION_SPACE)
        else:
            with torch.no_grad():
                return torch.argmax(self.model(state)).item()

    def memorize(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < BATCH_SIZE:
            return

        # Sample a batch of experiences
        batch = random.sample(self.memory, BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*batch)
        states = torch.stack(states)
        actions = torch.tensor(actions)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        next_states = torch.stack(next_states)
        dones = torch.tensor(dones, dtype=torch.float32)

        # Compute Q values and target values
        q_values = self.model(states).gather(1, actions.unsqueeze(1)).squeeze()
        with torch.no_grad():
            max_next_q_values = self.target_model(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * GAMMA * max_next_q_values

        # Compute loss and optimize
        loss = F.mse_loss(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon
        self.epsilon = max(MIN_EPSILON, self.epsilon * EPSILON_DECAY)

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())


# Initialize Pygame and Agent
pg.init()
env = SnakeEnv()
agent = DQNAgent()

# Game loop with training
episodes = 1000
for episode in range(episodes):
    state = env.reset()
    env.episode = episode + 1
    done = False
    total_reward = 0
    while not done:
        action = agent.act(state)
        next_state, reward, done = env.step(action)
        agent.memorize(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward
        agent.replay()
        env.render()  # Render the game

    print(f"Episode: {episode}, Total Reward: {total_reward}")

    # Update the target network every few episodes
    if episode % TARGET_UPDATE == 0:
        agent.update_target_model()

# Quit Pygame safely
pg.quit()

if __name__ == "__main__":
    try:
        env = SnakeEnv()
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            
            env.render()
            env.clock.tick(10)
    finally:
        env.close()