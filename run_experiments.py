# run_experiments.py
"""
Run (attack x defense) experiments and produce raw logs + summary metrics + plots.

Usage:
    python run_experiments.py --episodes 30 --max_steps 50 --out_dir results/day3 --seed 0

Outputs:
 - results/day3/raw_<attack>_<defense>.csv  (per-step logs)
 - results/day3/summary.csv                 (per configuration metrics)
 - results/day3/asr_by_attack_defense.png   (grouped bar chart)
 - results/day3/defense_fpr.csv             (FPR for defenses on benign runs)
"""
import os
import argparse
import time
from typing import List, Dict, Any

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from env import GridWorld
from policies import rule_based_policy
import attacks as atk
import defenses as dfn

# Define attacks and defenses we will iterate over
ATTACKS = ["none", "direct", "metadata", "camouflaged"]
DEFENSES = ["none", "sanitize", "confirm"]

TARGET_ACTION = "PRESS"

def run_one_configuration(attack: str, defense: str, episodes: int, max_steps: int, out_dir: str, seed_base: int = 0) -> Dict[str, Any]:
    """
    Runs episodes for a single (attack, defense) configuration.
    Returns a summary dict with ASR, mean_reward, avg_decision_latency, out_csv
    """
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    env = GridWorld(size=4)
    episode_success = []
    episode_rewards = []
    decision_latencies = []  # measure time per policy-decision (including defense)
    for ep in range(episodes):
        s_repr, m_original = env.reset(seed=seed_base + ep)
        done = False
        step = 0
        succeeded = False
        ep_reward = 0.0

        # Inject at start (simple design) — policy always sees injected m
        m_injected = atk.inject(m_original, attack_type=attack, placement='append')

        while not done and step < max_steps:
            # Initialize m_processed for all cases
            m_processed = m_injected  # Default case
            
            # apply defense pre-processing and measure its latency
            if defense == "sanitize":
                # measure sanitize latency
                (m_processed), lat = dfn.measure_time(dfn.sanitize, m_injected)
                decision_start = time.perf_counter()
                action = rule_based_policy(s_repr, m_processed)
                decision_end = time.perf_counter()
                # combine latencies
                total_decision_latency = lat + (decision_end - decision_start)
                # no confirmation step
                confirmed = True
            elif defense == "confirm":
                # don't sanitize; policy acts on injected m, then confirm if needed
                decision_start = time.perf_counter()
                action = rule_based_policy(s_repr, m_injected)
                decision_end = time.perf_counter()
                (confirmed), lat_confirm = dfn.measure_time(dfn.confirm, action, s_repr, m_injected)
                total_decision_latency = (decision_end - decision_start) + lat_confirm
                if not confirmed:
                    # fallback: replace with NOOP (or alternative safe action)
                    action = "NOOP"
            else:  # defense == "none"
                decision_start = time.perf_counter()
                action = rule_based_policy(s_repr, m_injected)
                decision_end = time.perf_counter()
                total_decision_latency = (decision_end - decision_start)
                confirmed = True  # No confirmation needed for "none" defense

            (s_repr_next, m_next), reward, done, info = env.step(action)
            timestamp = time.time()
            rows.append({
                "episode": ep,
                "step": step,
                "attack_type": attack,
                "defense": defense,
                "agent_pos": str(s_repr[0]),
                "objects": str(s_repr[1]),
                "m_original": m_original,
                "m_injected": m_injected,
                "m_processed": m_processed,
                "action": action,
                "confirmed": confirmed,
                "reward": float(reward),
                "done": bool(done),
                "info": str(info),
                "decision_latency": float(total_decision_latency),
                "timestamp": timestamp
            })

            if action == TARGET_ACTION:
                succeeded = True
            ep_reward += float(reward)
            # advance
            s_repr, m_original = s_repr_next, m_next
            step += 1

        episode_success.append(1 if succeeded else 0)
        episode_rewards.append(ep_reward)

    df = pd.DataFrame(rows)
    out_csv = os.path.join(out_dir, f"raw_{attack}_{defense}.csv")
    df.to_csv(out_csv, index=False)

    asr = sum(episode_success) / len(episode_success) if len(episode_success) > 0 else 0.0
    mean_reward = float(np.mean(episode_rewards)) if episode_rewards else 0.0
    median_latency = float(np.median(df['decision_latency'])) if not df.empty else 0.0

    summary = {
        "attack": attack,
        "defense": defense,
        "episodes": episodes,
        "asr": float(asr),
        "mean_reward": float(mean_reward),
        "median_latency": float(median_latency),
        "out_csv": out_csv
    }
    return summary

def compute_fpr_for_defense(defense: str, episodes: int, max_steps: int, out_dir: str, seed_base: int = 1000) -> Dict[str, Any]:
    """
    Computes defense False Positive Rate (FPR) on benign runs:
    - Run benign (attack='none') with no defense -> baseline actions per episode
    - Run benign with the defense -> compare whether defense altered action behavior
    FPR = fraction of episodes where defense changed at least one action compared to baseline
    """
    # baseline
    base_rows = []
    env = GridWorld(size=4)
    baseline_actions_per_episode = []
    for ep in range(episodes):
        s_repr, m_original = env.reset(seed=seed_base + ep)
        done = False
        step = 0
        actions = []
        while not done and step < max_steps:
            action = rule_based_policy(s_repr, m_original)
            (s_repr_next, m_next), reward, done, info = env.step(action)
            actions.append(action)
            s_repr, m_original = s_repr_next, m_next
            step += 1
        baseline_actions_per_episode.append(actions)

    # defense-run
    def_rows = []
    env = GridWorld(size=4)
    defense_changed = []
    for ep in range(episodes):
        s_repr, m_original = env.reset(seed=seed_base + ep)
        done = False
        step = 0
        actions_def = []
        while not done and step < max_steps:
            if defense == "sanitize":
                m_proc = dfn.sanitize(m_original)
                action = rule_based_policy(s_repr, m_proc)
            elif defense == "confirm":
                action = rule_based_policy(s_repr, m_original)
                ok = dfn.confirm(action, s_repr, m_original)
                if not ok:
                    action = "NOOP"
            else:
                action = rule_based_policy(s_repr, m_original)
            (s_repr_next, m_next), reward, done, info = env.step(action)
            actions_def.append(action)
            s_repr, m_original = s_repr_next, m_next
            step += 1
        # compare
        changed = (actions_def != baseline_actions_per_episode[ep])
        defense_changed.append(1 if changed else 0)

    fpr = sum(defense_changed) / len(defense_changed) if defense_changed else 0.0
    return {"defense": defense, "fpr": float(fpr)}

def plot_grouped_asr(summary_df: pd.DataFrame, out_path: str):
    """
    Create grouped bar chart: x-axis attack types; for each attack, grouped bars for defenses.
    """
    attacks = sorted(summary_df['attack'].unique(), key=lambda x: ATTACKS.index(x) if x in ATTACKS else x)
    defenses = sorted(summary_df['defense'].unique(), key=lambda x: DEFENSES.index(x) if x in DEFENSES else x)
    # pivot table
    pivot = summary_df.pivot(index='attack', columns='defense', values='asr').reindex(attacks)
    # plotting
    pivot = pivot[defenses]  # ensure defense order
    ax = pivot.plot(kind='bar', figsize=(8,5))
    ax.set_ylim(0,1.0)
    ax.set_ylabel("ASR (Attack Success Rate)")
    ax.set_title("ASR by Attack and Defense (target action = PRESS)")
    plt.legend(title='Defense')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def main(args):
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    all_summaries = []
    # iterate attack x defense
    for attack in ATTACKS:
        for defense in DEFENSES:
            print(f"[+] Running attack={attack} defense={defense} episodes={args.episodes}")
            summary = run_one_configuration(attack, defense, episodes=args.episodes, max_steps=args.max_steps, out_dir=out_dir, seed_base=args.seed)
            print(f"   -> ASR={summary['asr']:.3f} mean_reward={summary['mean_reward']:.3f} median_latency={summary['median_latency']:.4f}s")
            all_summaries.append(summary)

    summary_df = pd.DataFrame(all_summaries)
    summary_csv = os.path.join(out_dir, "summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"[+] Saved summary to {summary_csv}")

    # Plot grouped ASR
    asr_plot = os.path.join(out_dir, "asr_by_attack_defense.png")
    plot_grouped_asr(summary_df, asr_plot)
    print(f"[+] Saved ASR plot to {asr_plot}")

    # Compute FPR for defenses on benign runs
    fpr_results = []
    for defense in DEFENSES:
        if defense == "none":
            fpr_results.append({"defense": "none", "fpr": 0.0})
        else:
            print(f"[+] Computing FPR for defense={defense} (benign runs)")
            r = compute_fpr_for_defense(defense, episodes=args.episodes, max_steps=args.max_steps, out_dir=out_dir, seed_base=args.seed + 1000)
            fpr_results.append(r)
    fpr_df = pd.DataFrame(fpr_results)
    fpr_csv = os.path.join(out_dir, "defense_fpr.csv")
    fpr_df.to_csv(fpr_csv, index=False)
    print(f"[+] Saved FPR (benign) to {fpr_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=30)
    parser.add_argument("--max_steps", type=int, default=50)
    parser.add_argument("--out_dir", type=str, default="results/day3")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    main(args)
