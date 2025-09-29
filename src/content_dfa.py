class ContentDFA:
    def __init__(self):
        # States
        self.q0 = "q0"
        self.qBad = "qBad"
        self.qPol = "qPol"
        self.qSex = "qSex"
        self.qViol = "qViol"

        # Final states
        self.qF_Hate = "qF_Hate"
        self.qF_Offensive = "qF_Offensive"
        self.qF_Sex = "qF_Sex"
        self.qF_Harass = "qF_Harass"
        self.qF_Threats = "qF_Threats"
        self.qF_SelfHarm = "qF_SelfHarm"
        self.qF_Violence = "qF_Violence"
        self.qF_Safe = "qF_Safe"

        # Initial state
        self.state = self.q0

    def reset(self):
        self.state = self.q0

    def transition(self, token):
        token = token.lower()
        """
        Advances the automaton according to the token.
        """
        # From q0
        if self.state == self.q0:
            if token == "badword":
                self.state = self.qBad
            elif token == "politics":
                self.state = self.qPol
            elif token == "sexword":
                self.state = self.qSex
            elif token == "violence":
                self.state = self.qViol
            return

        # "other_token" loops
        if token == "otro_token":
            # remains in the same state if it is already in qBad, qPol, qSex or qViol
            return

        # if another different token arrives, the state does not change
        return

    def end_of_input(self, direction_final):
        """
        Cierra la ejecución ($) y determina el estado final 
        considerando la direccionalidad.
        """
        if self.state == self.qBad:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Offensive
            elif direction_final == "qF_Others":
                return self.qF_Hate

        if self.state == self.qPol:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Offensive
            elif direction_final == "qF_Others":
                return self.qF_Hate

        if self.state == self.qSex:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Sex
            elif direction_final == "qF_Others":
                return self.qF_Harass

        if self.state == self.qViol:
            if direction_final == "qF_Self":
                return self.qF_SelfHarm
            elif direction_final == "qF_Others":
                return self.qF_Threats
            elif direction_final == "qF_Generic":
                return self.qF_Violence

        # If no thematic state was ever activated
        if self.state == self.q0:
            return self.qF_Safe

        return None
