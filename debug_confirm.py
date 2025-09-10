from env import GridWorld
import attacks
import defenses

env = GridWorld(size=4)
s_repr, m_original = env.reset(seed=42)
print('Original environment message:', repr(m_original))

# Test each attack with injected message
attacks_to_test = ['direct', 'metadata', 'camouflaged']
for attack in attacks_to_test:
    m_injected = attacks.inject(m_original, attack_type=attack)
    print(f'\n{attack.upper()} attack injected message:', repr(m_injected))
    
    # Test confirm defense
    confirmed = defenses.confirm('PRESS', s_repr, m_injected)
    print(f'Confirm defense allows PRESS: {confirmed}')
    
    # Test if agent is at button position
    agent_pos, objects_tuple = s_repr
    obj_dict = dict(objects_tuple)
    red_button = obj_dict.get("red_button")
    print(f'Agent at button position: {agent_pos == red_button}')
    print(f'Agent position: {agent_pos}, Button position: {red_button}')
