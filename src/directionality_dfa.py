from .preprocessing import RegexTokenizer
from .directionality_dfa import DirectionalityDFA

class ContentDFA:
    def __init__(self, keywords_file=None):
        # Content DFA states
        self.q0 = "q0"
        self.qBad = "qBad"
        self.qPol = "qPol"
        self.qSex = "qSex"
        self.qViol = "qViol"

        self.qF_Hate = "qF_Hate"
        self.qF_Offensive = "qF_Offensive"
        self.qF_Sex = "qF_Sex"
        self.qF_Harass = "qF_Harass"
        self.qF_Threats = "qF_Threats"
        self.qF_SelfHarm = "qF_SelfHarm"
        self.qF_Violence = "qF_Violence"
        self.qF_Safe = "qF_Safe"

        self.state = self.q0

        # Tokenizer
        self.tokenizer = RegexTokenizer(keywords_file) if keywords_file else None

        # Directionality DFA
        self.direction_dfa = DirectionalityDFA()

    def reset(self):
        self.state = self.q0
        self.direction_dfa.reset()

    def transition(self, token):
        """Avanza el autómata de contenido"""
        if self.state == self.q0:
            if token == "BADWORD":
                self.state = self.qBad
            elif token == "POLITIC":
                self.state = self.qPol
            elif token == "SEXWORD":
                self.state = self.qSex
            elif token == "VIOLENCE":
                self.state = self.qViol
            # another_token keeps q0
        elif token == "otro_token":
            # Remains in the same state if a topic has already been activated
            pass

    def process_text(self, text):
        """Recibe un texto completo y lo procesa token por token"""
        self.reset()
        tokens = self.tokenizer.tokenize(text) if self.tokenizer else text.split()
        for tok in tokens:
            # First we update the directionality
            self.direction_dfa.transition(tok)
            # Then the content DFA
            self.transition(tok)
        # In the end we obtain the final state of directionality
        direction_final = self.direction_dfa.end_of_input()
        return self.end_of_input(direction_final)

    def end_of_input(self, direction_final):
        """Devuelve el estado final de contenido según la direccionalidad"""
        if self.state == self.qBad:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Offensive
            elif direction_final == "qF_Others":
                return self.qF_Hate
        elif self.state == self.qPol:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Offensive
            elif direction_final == "qF_Others":
                return self.qF_Hate
        elif self.state == self.qSex:
            if direction_final in ["qF_Self", "qF_Generic"]:
                return self.qF_Sex
            elif direction_final == "qF_Others":
                return self.qF_Harass
        elif self.state == self.qViol:
            if direction_final == "qF_Self":
                return self.qF_SelfHarm
            elif direction_final == "qF_Others":
                return self.qF_Threats
            elif direction_final == "qF_Generic":
                return self.qF_Violence
        elif self.state == self.q0:
            return self.qF_Safe
        return None
