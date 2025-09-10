# policies.py
import re
from typing import Tuple, Any
from env import ACTIONS

def parse_goal_coords(m_text: str):
    """
    Expect a substring like: 'red_box at (3,1)'.
    Return (x,y) as ints or None.
    """
    m = re.search(r'red_box at \((\s*\d+)\s*,\s*(\d+)\s*\)', m_text)
    if m:
        x = int(m.group(1)); y = int(m.group(2))
        return (x, y)
    return None

def greedy_move_towards(agent_pos: Tuple[int,int], target_pos: Tuple[int,int]):
    ax, ay = agent_pos; tx, ty = target_pos
    if ax < tx:
        return "RIGHT"
    if ax > tx:
        return "LEFT"
    if ay < ty:
        return "DOWN"
    if ay > ty:
        return "UP"
    return "NOOP"  # already there

def rule_based_policy(s_repr: Tuple[Tuple[int,int], tuple], m_text: str) -> str:
    """
    Very simple rule-based policy:
      - parse target coords from m_text
      - move towards it using greedy Manhattan
      - once at box location: PICK
      - if carrying, move back to origin (0,0) and DROP
      - if at button location and 'press' token appears, do PRESS (simulate vulnerability)
    """
    agent_pos, objects_tuple = s_repr
    # find red_box and red_button positions from s_repr
    obj_dict = dict(objects_tuple)
    red_box = obj_dict.get("red_box")
    red_button = obj_dict.get("red_button")

    # if message contains a "press" instruction, do PRESS if co-located or try to go there
    if re.search(r'press', m_text, flags=re.I):
        # if agent at button location -> press
        if agent_pos == red_button:
            return "PRESS"
        # otherwise move towards button
        return greedy_move_towards(agent_pos, red_button)

    # if carrying box -> go back to origin and drop
    carrying = False  # in this simple policy we can't see carrying; env sets carrying separately
    # As a rule-based proxy we decide: if agent at box pos and not carrying -> PICK
    if agent_pos == red_box:
        return "PICK"

    # else move toward red_box
    move = greedy_move_towards(agent_pos, red_box)
    return move
