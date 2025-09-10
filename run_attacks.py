# run_attacks.py
"""
Run experiments that inject attacks into perception m and compute ASR for action 'PRESS'.

Usage (example):
    python run_attacks.py --episodes 30 --max_steps 50 --out_dir results/day2 --seed 0 --attacks direct metadata camouflaged

If you pass 'all' for --attacks, it will run all templates including 'none'.
"""
import argparse
import os
import time
from typing import List, Dict, Any

import pandas as pd
import matplotlib.pyplot as plt

from env import GridWorld
from policies import rule_based_policy
import attacks as atk

TARGET_ACTION = "PRESS"

def run_for_attack(attack_type: str, episodes: int, max_steps: int, out_dir: str, seed_base: int = 0) -> Dict[str, Any]:
    """
    Run episodes where the perception m is injected with attack_type payload.
    Returns summary dict (ASR, episodes, attack_type, output_csv).
    """
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    env = GridWorld(size=4)
    episode_success = []  # whether episode reached target action at least once
    for ep in range(episodes):
        # reset env with deterministic seed for reproducibility
        s_repr, m_original = env.reset(seed=seed_base + ep)
        done = False
        step = 0
        succeeded = False
        # inject once at episode start (simple scenario)
        m_injected = atk.inject(m_original, attack_type=attack_type, placement='append')
        while not done and step < max_steps:
            action = rule_based_policy(s_repr, m_injected)  # policy sees injected m
            (s_repr_next, m_next), reward, done, info = env.step(action)
            timestamp = time.time()
            rows.append({
                "episode": ep,
                "attack_type": attack_type,
                "step": step,
                "agent_pos": str(s_repr[0]),
                "objects": str(s_repr[1]),
                "m_original": m_original,
                "m_injected": m_injected,
                "action": action,
                "reward": float(reward),
                "done": bool(done),
                "info": str(info),
                "timestamp": timestamp
            })
            if action == TARGET_ACTION:
                succeeded = True
            # advance
            s_repr, m_original = s_repr_next, m_next
            step += 1

        episode_success.append(1 if succeeded else 0)

    df = pd.DataFrame(rows)
    out_csv = os.path.join(out_dir, f"raw_{attack_type}.csv")
    df.to_csv(out_csv, index=False)
    # compute ASR = fraction of episodes where target action occurred at least once
    asr = sum(episode_success) / len(episode_success) if len(episode_success) > 0 else 0.0
    summary = {
        "attack_type": attack_type,
        "episodes": episodes,
        "asr": float(asr),
        "out_csv": out_csv
    }
    return summary

def plot_asr(summaries: List[Dict[str, Any]], out_path: str):
    attack_names = [s["attack_type"] for s in summaries]
    asr_vals = [s["asr"] for s in summaries]
    plt.figure(figsize=(6,4))
    bars = plt.bar(attack_names, asr_vals, color=["#d9534f","#f0ad4e","#5bc0de","#5cb85c"])
    plt.ylim(0,1.0)
    plt.ylabel("Attack Success Rate (ASR)")
    plt.title("ASR by Attack Template (target action = PRESS)")
    # annotate values
    for bar, val in zip(bars, asr_vals):
        plt.text(bar.get_x() + bar.get_width()/2, val + 0.02, f"{val:.2f}", ha='center')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def main(args):
    # determine attacks to run
    if "all" in args.attacks:
        attack_list = atk.attack_names()
    else:
        # validate given names
        attack_list = []
        for a in args.attacks:
            if a not in atk.attack_names():
                print(f"Warning: unknown attack '{a}' - skipping")
            else:
                attack_list.append(a)
    if not attack_list:
        print("No valid attacks to run. Exiting.")
        return

    os.makedirs(args.out_dir, exist_ok=True)
    summaries = []
    for a in attack_list:
        print(f"[+] Running attack '{a}' for {args.episodes} episodes...")
        summary = run_for_attack(a, episodes=args.episodes, max_steps=args.max_steps, out_dir=args.out_dir, seed_base=args.seed)
        print(f"   -> ASR for {a}: {summary['asr']:.3f}")
        summaries.append(summary)

    # save summary CSV
    summary_df = pd.DataFrame(summaries)
    summary_csv = os.path.join(args.out_dir, "asr_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"[+] Saved summary to {summary_csv}")

    # plot ASR bar chart
    plot_path = os.path.join(args.out_dir, "asr_by_attack.png")
    plot_asr(summaries, plot_path)
    print(f"[+] Saved ASR plot to {plot_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=30, help="number of episodes per attack")
    parser.add_argument("--max_steps", type=int, default=50, help="max steps per episode")
    parser.add_argument("--out_dir", type=str, default="results/day2", help="output directory")
    parser.add_argument("--seed", type=int, default=0, help="seed base for reproducibility")
    parser.add_argument("--attacks", nargs="+", default=["direct","metadata","camouflaged"], help="attacks to run or 'all'")
    args = parser.parse_args()
    main(args)
