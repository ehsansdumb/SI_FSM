# fsm_states.py

class FSM:
    def __init__(self, initial_state):
        self.state = initial_state

    def change_state(self, new_state):
        print(f"Transitioning from {self.state} to {new_state}")
        self.state = new_state