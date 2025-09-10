import pandas as pd

df = pd.read_csv('results/day3/summary.csv')
print('Summary Results:')
print(df.to_string(index=False))
print('\nKey Observations:')
print('1. Without defense (none): ASR = 1.0 for all attacks (except none)')
print('2. With sanitize defense: ASR = 0.0 for all attacks')
print('3. With confirm defense: Still ASR = 1.0 - potential issue!')
print('4. Mean reward is much lower with successful attacks (-86 vs -4)')

print('\nChecking confirm defense logic...')
# The issue might be that confirm defense allows legitimate owner=alice + PRESS combination
print('Confirm defense should block unauthorized PRESS actions but allow authorized ones')
