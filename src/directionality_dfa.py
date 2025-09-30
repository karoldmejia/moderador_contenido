class DirectionalityDFA:
    def __init__(self):
        # Estados
        self.q0 = "q0"
        self.q1 = "q1"  # Self detected
        self.q2 = "q2"  # Others detected
        self.q3 = "q3"  # Generic
        self.qF_Self = "qF_Self"
        self.qF_Others = "qF_Others"
        self.qF_Generic = "qF_Generic"

        # Estado inicial
        self.state = self.q0

    def reset(self):
        self.state = self.q0

    def transition(self, token):
        """
        Aplica la transición del autómata dado un token.
        """
        # Si aparece un pronombre en cualquier momento, actualiza
        if token == "PRONOUN_SELF":
            self.state = self.q1
        elif token == "PRONOUN_OTHER":
            self.state = self.q2
        else:
            # Si aún no se ha clasificado, marca como genérico
            if self.state == self.q0:
                self.state = self.q3
        # Si ya está en q1 o q2, no se cambia por genérico


    def end_of_input(self):
        """
        Transición al estado final ($).
        """
        if self.state == self.q1:
            self.state = self.qF_Self
        elif self.state == self.q2:
            self.state = self.qF_Others
        elif self.state == self.q3:
            self.state = self.qF_Generic
        return self.state
