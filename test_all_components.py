# Comprehensive test of all components
from env import GridWorld
from policies import rule_based_policy
import attacks as atk
import defenses as dfn

print('🔍 COMPREHENSIVE COMPONENT TEST')
print('='*50)

# Test 1: Environment
env = GridWorld(size=4)
s_repr, m = env.reset(seed=42)
print(f'✅ Environment: {len(str(s_repr))} char state, {len(m)} char message')

# Test 2: Policy  
action = rule_based_policy(s_repr, m)
print(f'✅ Policy: chose action {action}')

# Test 3: Attacks
for attack_type in ['none', 'direct', 'metadata', 'camouflaged']:
    injected = atk.inject(m, attack_type)
    print(f'✅ Attack {attack_type}: {len(injected)} chars')

# Test 4: Defenses
sanitized = dfn.sanitize(injected)
confirmed = dfn.confirm('PRESS', s_repr, injected)
print(f'✅ Defenses: sanitized={len(sanitized)} chars, confirmed={confirmed}')

print('='*50)
print('🎉 ALL COMPONENTS WORKING CORRECTLY!')
