# run.py
import argparse
import time
import pandas as pd
from env import GridWorld
from policies import rule_based_policy

def run_episodes(n_episodes: int = 20, max_steps: int = 50, out_csv: str = "results/day1_results.csv", seed_base: int = 0):
    rows = []
    env = GridWorld(size=4)
    for ep in range(n_episodes):
        s_repr, m = env.reset(seed=seed_base + ep)
        done = False
        step = 0
        while not done and step < max_steps:
            # policy chooses action
            action = rule_based_policy(s_repr, m)
            (s_repr_next, m_next), reward, done, info = env.step(action)
            timestamp = time.time()
            rows.append({
                "episode": ep,
                "step": step,
                "agent_pos": str(s_repr[0]),
                "objects": str(s_repr[1]),
                "m": m,
                "action": action,
                "reward": float(reward),
                "done": bool(done),
                "info": str(info),
                "timestamp": timestamp
            })
            # advance
            s_repr, m = s_repr_next, m_next
            step += 1
    df = pd.DataFrame(rows)
    # ensure results folder exists
    import os
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Saved results to {out_csv}")
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Day1 GridWorld experiments")
    parser.add_argument("--episodes", type=int, default=30)
    parser.add_argument("--max_steps", type=int, default=50)
    parser.add_argument("--out", type=str, default="results/day1_results.csv")
    args = parser.parse_args()
    df = run_episodes(n_episodes=args.episodes, max_steps=args.max_steps, out_csv=args.out)
    print(df.head())
