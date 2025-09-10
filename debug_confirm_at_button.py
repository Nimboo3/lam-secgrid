from env import GridWorld
import attacks
import defenses

env = GridWorld(size=4)
s_repr, m_original = env.reset(seed=42)

# Simulate agent being at button position
agent_pos, objects_tuple = s_repr
obj_dict = dict(objects_tuple)
red_button = obj_dict.get("red_button")

# Create a new state where agent is at button position
s_repr_at_button = (red_button, objects_tuple)

print(f'Agent moved to button position: {red_button}')
print('Original environment message:', repr(m_original))

# Test each attack with injected message when agent is at button
attacks_to_test = ['direct', 'metadata', 'camouflaged']
for attack in attacks_to_test:
    m_injected = attacks.inject(m_original, attack_type=attack)
    print(f'\n{attack.upper()} attack injected message:', repr(m_injected))
    
    # Test confirm defense when agent is at button
    confirmed = defenses.confirm('PRESS', s_repr_at_button, m_injected)
    print(f'Confirm defense allows PRESS when at button: {confirmed}')
    
    # Check if the original message contains owner=alice
    has_alice = 'owner=alice' in m_injected
    print(f'Message contains owner=alice: {has_alice}')
