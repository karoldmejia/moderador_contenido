class DirectionalityDFA:
    def __init__(self):
        # States
        self.q0 = "q0"
        self.q1 = "q1"  # Self detected
        self.q2 = "q2"  # Others detected
        self.q3 = "q3"  # Generic
        self.qF_Self = "qF_Self"
        self.qF_Others = "qF_Others"
        self.qF_Generic = "qF_Generic"

        # Initial state
        self.state = self.q0

    def reset(self):
        self.state = self.q0

    def transition(self, token):
        """
        Applies the transition of the automaton given a token.
        """
        # If a pronoun appears at any time, update the state
        if token == "PRONOUN_SELF":
            self.state = self.q1
        elif token == "PRONOUN_OTHER":
            self.state = self.q2
        else:
            # If not yet classified, mark as generic
            if self.state == self.q0:
                self.state = self.q3
        # If already in q1 or q2, do not change to generic


    def end_of_input(self):
        """
        Transition to the final state ($).
        """
        if self.state == self.q1:
            self.state = self.qF_Self
        elif self.state == self.q2:
            self.state = self.qF_Others
        elif self.state == self.q3:
            self.state = self.qF_Generic
        return self.state
