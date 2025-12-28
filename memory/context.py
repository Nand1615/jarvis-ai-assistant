# Short-term context memory

current_action = None
current_target = None

last_action = None
last_target = None


def set_context(action: str, target: str):
    global current_action, current_target
    global last_action, last_target

    # Save previous before overwriting
    last_action = current_action
    last_target = current_target

    current_action = action
    current_target = target


def get_current_context():
    return current_action, current_target


def get_last_context():
    return last_action, last_target


def clear_current_context():
    global current_action, current_target
    current_action = None
    current_target = None
