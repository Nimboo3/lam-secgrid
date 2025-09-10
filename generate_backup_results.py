#!/usr/bin/env python3
"""
Backup demo results generator - run this before your presentation
to ensure you have good results ready in case live demo fails.
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"GENERATING: {description}")
    print(f"COMMAND: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ SUCCESS: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {description}")
        print(f"Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    print("🎯 GENERATING BACKUP DEMO RESULTS")
    print("This ensures you have good results even if live demo fails...")
    
    # Use full Python path
    python_exe = "C:/Projects/lam-secgrid/venv/Scripts/python.exe"
    
    commands = [
        (f"{python_exe} run.py --episodes 10 --max_steps 20 --out results/backup_clean.csv", 
         "Clean baseline behavior"),
        
        (f"{python_exe} run_attacks.py --episodes 20 --max_steps 25 --out_dir results/backup_attacks --attacks all", 
         "Attack effectiveness demonstration"),
        
        (f"{python_exe} run_experiments.py --episodes 15 --max_steps 25 --out_dir results/backup_defenses", 
         "Defense evaluation with all metrics"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"BACKUP GENERATION COMPLETE")
    print(f"Successfully generated {success_count}/{len(commands)} result sets")
    
    if success_count == len(commands):
        print("🎉 ALL BACKUP RESULTS READY!")
        print("\nYou can now confidently present, knowing you have:")
        print("  📊 results/backup_attacks/ - Attack demonstrations")
        print("  📊 results/backup_defenses/ - Defense evaluations") 
        print("  📊 results/backup_clean.csv - Baseline behavior")
        print("\nIf live demo fails, simply reference these backup files.")
    else:
        print("⚠️  Some backup generation failed - check errors above")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
