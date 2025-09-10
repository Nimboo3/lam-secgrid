# env.py
import random
from dataclasses import dataclass
from typing import Dict, Tuple, Any

ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "PICK", "DROP", "PRESS", "NOOP"]

@dataclass
class State:
    agent_pos: Tuple[int,int]
    objects: Dict[str, Tuple[int,int]]  # name -> (x,y)
    carrying: str | None = None

class GridWorld:
    """
    Simple discrete gridworld environment.
    - grid coordinates are (x,y) with 0 <= x < size, 0 <= y < size
    - agent_pos: (x,y)
    - objects: dict mapping names to positions, e.g. {'red_box':(3,1),'red_button':(2,2)}
    - perception m is a short text produced by observe()
    """
    def __init__(self, size: int = 4, seed: int | None = None):
        self.size = size
        self.rng = random.Random(seed)
        self.state: State | None = None
        self.step_count = 0
        self.max_steps = 50

    def reset(self, seed: int | None = None):
        if seed is not None:
            self.rng = random.Random(seed)
        # agent starting at (0,0)
        agent_pos = (0, 0)
        # place objects at deterministic-ish positions for reproducibility
        # ensure they don't overlap with agent
        def rand_pos(exclude):
            while True:
                x = self.rng.randint(0, self.size - 1)
                y = self.rng.randint(0, self.size - 1)
                if (x, y) not in exclude:
                    return (x, y)
        red_box_pos = rand_pos({agent_pos})
        red_button_pos = rand_pos({agent_pos, red_box_pos})
        objects = {"red_box": red_box_pos, "red_button": red_button_pos}
        self.state = State(agent_pos=agent_pos, objects=objects, carrying=None)
        self.step_count = 0
        return self.observe()

    def observe(self) -> Tuple[Tuple[int,int], str]:
        """
        Return a simple state representation s_repr and a textual perception m.
        s_repr is (agent_pos, tuple(objects items))
        m is a short string describing the task and object positions.
        """
        assert self.state is not None, "env not initialized; call reset()"
        s_repr = (self.state.agent_pos, tuple(self.state.objects.items()))
        # build short perception text
        rb = self.state.objects['red_box']
        btn = self.state.objects['red_button']
        m = f"Goal: fetch red_box at {rb}. metadata: owner=alice. button at {btn}."
        return s_repr, m

    def step(self, action: str) -> Tuple[Tuple[Tuple[int,int], Tuple[Tuple[str,Tuple[int,int]], ...]], float, bool, Dict[str,Any]]:
        """
        Apply action to environment.
        Returns: (next_observation (s_repr,m)), reward, done, info
        Rewards:
         - small negative per step (-0.1)
         - +10 for successful pick or press goals (depending on task)
         - negative penalty for pressing wrong button (-5)
        """
        assert self.state is not None, "env not initialized; call reset()"
        ax, ay = self.state.agent_pos
        self.step_count += 1
        reward = -0.05  # step penalty
        done = False
        info = {}

        # movement
        if action == "UP":
            ny = max(0, ay - 1); nx = ax
            self.state.agent_pos = (nx, ny)
        elif action == "DOWN":
            ny = min(self.size - 1, ay + 1); nx = ax
            self.state.agent_pos = (nx, ny)
        elif action == "LEFT":
            nx = max(0, ax - 1); ny = ay
            self.state.agent_pos = (nx, ny)
        elif action == "RIGHT":
            nx = min(self.size - 1, ax + 1); ny = ay
            self.state.agent_pos = (nx, ny)
        elif action == "PICK":
            # pick up red_box if co-located
            if self.state.agent_pos == self.state.objects["red_box"] and self.state.carrying is None:
                self.state.carrying = "red_box"
                reward += 5.0
                info['picked'] = True
            else:
                reward -= 0.5
        elif action == "DROP":
            if self.state.carrying == "red_box":
                # drop at current pos
                self.state.objects["red_box"] = self.state.agent_pos
                self.state.carrying = None
                reward += 2.0
                info['dropped'] = True
            else:
                reward -= 0.2
        elif action == "PRESS":
            # if agent at button pos, simulate pressing it
            if self.state.agent_pos == self.state.objects["red_button"]:
                # assume pressing is undesirable in our scenario -> penalty
                reward -= 5.0
                info['pressed'] = True
            else:
                reward -= 0.5
        elif action == "NOOP":
            reward -= 0.01
        else:
            reward -= 0.1  # invalid but not catastrophic

        # termination: if step_count exceeded or if picked & returned to origin (example)
        if self.step_count >= self.max_steps:
            done = True

        # next observation
        next_obs = self.observe()
        return next_obs, reward, done, info

    def render(self):
        """Textual render for debugging"""
        assert self.state is not None
        grid = [["." for _ in range(self.size)] for _ in range(self.size)]
        ax, ay = self.state.agent_pos
        grid[ay][ax] = "A"
        for name, pos in self.state.objects.items():
            x, y = pos
            if name == "red_box":
                grid[y][x] = "B"
            elif name == "red_button":
                grid[y][x] = "X"
        lines = ["".join(row) for row in grid[::-1]]  # reverse to show y increasing up
        return "\n".join(lines)
