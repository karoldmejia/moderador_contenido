class ContentDFA:
    def __init__(self):
        # Intermediate states
        self.q0 = "q0"
        self.qB = "qB"      # Badword
        self.qP = "qP"      # Politic
        self.qPB = "qPB"    # Politic + Badword
        self.qV = "qV"      # Violence
        self.qPV = "qPV"    # Politic + Violence
        self.qS = "qS"      # Sexword

        # Final states
        self.qF_Offensive  = "qF_Offensive"
        self.qF_Hate       = "qF_Hate"
        self.qF_Sex        = "qF_Sex"
        self.qF_Harass     = "qF_Harass"
        self.qF_SelfHarm   = "qF_SelfHarm"
        self.qF_Threats    = "qF_Threats"
        self.qF_Violence   = "qF_Violence"
        self.qF_Safe       = "qF_Safe"

        # Initial state
        self.state = self.q0

    def reset(self):
        self.state = self.q0

    def transition(self, token):
        token = token.lower()

        # -------------------------
        # Transitions from q0
        # -------------------------
        if self.state == self.q0:
            if token == "badword":
                self.state = self.qB
            elif token == "politic":
                self.state = self.qP
            elif token == "sexword":
                self.state = self.qS
            elif token == "violence":
                self.state = self.qV
            else:  # Σ, any other token
                self.state = self.q0
            return

        # -------------------------
        # Combinations
        # -------------------------
        if self.state == self.qB:
            if token == "politic":
                self.state = self.qPB
            elif token != "badword":  # Σ
                self.state = self.qB
            return

        if self.state == self.qP:
            if token == "badword":
                self.state = self.qPB
            elif token == "violence":
                self.state = self.qPV
            elif token != "politic":  # Σ
                self.state = self.qP
            return

        if self.state == self.qV:
            if token == "politic":
                self.state = self.qPV
            elif token != "violence":  # Σ
                self.state = self.qV
            return

        if self.state == self.qS:
            if token != "sexword":  # Σ
                self.state = self.qS
            return

        if self.state == self.qPB:
            if token != "badword" and token != "politic":  # Σ
                self.state = self.qPB
            return

        if self.state == self.qPV:
            if token != "politic" and token != "violence":  # Σ
                self.state = self.qPV
            return

    def end_of_input(self, direction_final):
        """
        Finalizes the string ($) and returns the final state according to the directionality.
        """
        if self.state == self.qB:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Offensive
            elif direction_final == "qF_Others":
                return self.qF_Hate

        if self.state == self.qP:
            return self.qF_Safe  # Politic alone without combination

        if self.state == self.qPB:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Offensive
            elif direction_final == "qF_Others":
                return self.qF_Hate

        if self.state == self.qS:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Sex
            elif direction_final == "qF_Others":
                return self.qF_Harass

        if self.state == self.qV:
            if direction_final == "qF_Self":
                return self.qF_SelfHarm
            elif direction_final == "qF_Others":
                return self.qF_Threats
            elif direction_final == "qF_Generic":
                return self.qF_Violence

        if self.state == self.qPV:
            if direction_final in ["qF_Generic", "qF_Others"]:
                return self.qF_Hate
            elif direction_final == "qF_Self":
                return self.qF_Violence

        if self.state == self.q0:  # no alert word
            return self.qF_Safe

        return None