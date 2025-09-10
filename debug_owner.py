from env import GridWorld
import attacks
import defenses

env = GridWorld(size=4)
s_repr, m_original = env.reset(seed=42)

# Create modified message without alice
m_modified = m_original.replace('owner=alice', 'owner=bob')

# Simulate agent being at button position
agent_pos, objects_tuple = s_repr
obj_dict = dict(objects_tuple)
red_button = obj_dict.get("red_button")
s_repr_at_button = (red_button, objects_tuple)

print('Testing with owner=bob (should be blocked):')
print('Modified message:', repr(m_modified))

# Test with bob as owner
confirmed = defenses.confirm('PRESS', s_repr_at_button, m_modified)
print(f'Confirm defense allows PRESS for owner=bob: {confirmed}')

# Test with alice (should be allowed)
print('\nTesting with owner=alice (should be allowed):')
confirmed_alice = defenses.confirm('PRESS', s_repr_at_button, m_original)
print(f'Confirm defense allows PRESS for owner=alice: {confirmed_alice}')

# This shows the defense is working as designed but has a logical vulnerability
