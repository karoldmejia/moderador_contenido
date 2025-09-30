from pathlib import Path
from .preprocessing import RegexTokenizer
from .directionality_dfa import DirectionalityDFA

class ContentDFA:
    def __init__(self):
        keywords_file = Path(__file__).parent / "data" / "keywords.json"
        self.tokenizer = RegexTokenizer(str(keywords_file))
        # -------------------
        # Intermediate states
        # -------------------
        self.q0 = "q0"      # Start
        self.qB = "qB"      # Badword
        self.qP = "qP"      # Politics
        self.qPB = "qPB"    # Politics + Badword
        self.qV = "qV"      # Violence
        self.qPV = "qPV"    # Politics + Violence
        self.qS = "qS"      # Sexword

        # -------------------
        # Final states
        # -------------------
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

        # Directionality DFA
        self.direction_dfa = DirectionalityDFA()

    # -------------------
    # Reset
    # -------------------
    def reset(self):
        self.state = self.q0
        self.direction_dfa.reset()

    # -------------------
    # Transitions
    # -------------------
    def transition(self, token):
        """Advances the content DFA based on the token"""
        token = token.upper()

        # Initial state
        if self.state == self.q0:
            if token == "BADWORD":
                self.state = self.qB
            elif token == "POLITIC":
                self.state = self.qP
            elif token == "SEXWORD":
                self.state = self.qS
            elif token == "VIOLENCE":
                self.state = self.qV
            # Σ → stays at q0
            return

        # State qB (Badword)
        if self.state == self.qB:
            if token == "POLITIC":
                self.state = self.qPB
            # Σ or BADWORD → stays at qB
            return

        # State qP (Politics)
        if self.state == self.qP:
            if token == "BADWORD":
                self.state = self.qPB
            elif token == "VIOLENCE":
                self.state = self.qPV
            # Σ or POLITIC → stays at qP
            return

        # State qV (Violence)
        if self.state == self.qV:
            if token == "POLITIC":
                self.state = self.qPV
            # Σ or VIOLENCE → stays at qV
            return

        # State qS (Sexword)
        if self.state == self.qS:
            # Σ or SEXWORD → stays at qS
            return

        # State qPB (Politics + Badword)
        if self.state == self.qPB:
            # Σ, BADWORD or POLITIC → stays at qPB
            return

        # State qPV (Politics + Violence)
        if self.state == self.qPV:
            # Σ, POLITIC or VIOLENCE → stays at qPV
            return

    # -------------------
    # Process text
    # -------------------
    def process_text(self, text):
        """Processes a complete text token by token"""
        self.reset()
        tokens = self.tokenizer.tokenize(text) if self.tokenizer else text.split()
        for tok in tokens:
            self.direction_dfa.transition(tok)  # updates directionality
            self.transition(tok)                # updates content
        return self.end_of_input()

    # -------------------
    # End of input
    # -------------------
    def end_of_input(self):
        """
        Finalizes the input ($) and returns the final state
        combining content + directionality.
        """
        direction_final = self.direction_dfa.end_of_input()

        # Just badword
        if self.state == self.qB:
            if direction_final == "qF_Self":
                return self.qF_Offensive
            elif direction_final in ["qF_Others", "qF_Generic"]:
                return self.qF_Hate

        # Just politics
        if self.state == self.qP:
            return self.qF_Safe

        # Politics + Badword
        if self.state == self.qPB:
            if direction_final == "qF_Self":
                return self.qF_Offensive
            elif direction_final in ["qF_Others", "qF_Generic"]:
                return self.qF_Hate

        # Sexword
        if self.state == self.qS:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Sex
            elif direction_final == "qF_Others":
                return self.qF_Harass

        # Violence
        if self.state == self.qV:
            if direction_final == "qF_Self":
                return self.qF_SelfHarm
            elif direction_final == "qF_Others":
                return self.qF_Threats
            elif direction_final == "qF_Generic":
                return self.qF_Violence

        # Politics + Violence
        if self.state == self.qPV:
            if direction_final in ["qF_Generic", "qF_Others"]:
                return self.qF_Hate
            elif direction_final == "qF_Self":
                return self.qF_Violence

        # No trigger is safe
        if self.state == self.q0:
            return self.qF_Safe

        return None
