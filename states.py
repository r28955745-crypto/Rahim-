user_states = {}

def init_user_state(user_id):
    user_states[user_id] = {}

def set_state_data(user_id, key, value):
    if user_id not in user_states:
        init_user_state(user_id)
    user_states[user_id][key] = value

def get_user_data(user_id):
    return user_states.get(user_id)

def clear_user_state(user_id):
    if user_id in user_states:
        del user_states[user_id]

def add_to_history(user_id, record):
    if user_id not in user_states:
        user_states[user_id] = {'history': []}
    if 'history' not in user_states[user_id]:
        user_states[user_id]['history'] = []
    user_states[user_id]['history'].append(record)

def get_history(user_id):
    if user_id in user_states and 'history' in user_states[user_id]:
        return user_states[user_id]['history']
    return []

def clear_history(user_id):
    if user_id in user_states:
        user_states[user_id] = {}