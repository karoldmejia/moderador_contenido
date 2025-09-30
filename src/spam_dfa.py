from pathlib import Path
from .preprocessing import RegexTokenizer

class SpamDFA:
    def __init__(self):
        keywords_file = Path(__file__).parent / "data" / "keywords.json"
        self.tokenizer = RegexTokenizer(str(keywords_file))

        # -------------------
        # States
        # -------------------
        self.q0    = "q0"     # Start
        self.qU1   = "qU1"    # 1 URL
        self.qU2   = "qU2"    # 2 URLs
        self.qU3   = "qU3"    # 3 URLs
        self.qH1   = "qH1"    # 1 Hashtag
        self.qH2   = "qH2"    # 2 Hashtags
        self.qH3   = "qH3"    # 3 Hashtags
        self.qSpam = "qSpam"  # Spam detected (final)
        self.qSafe = "qSafe"  # Safe (final)

        # Initial state
        self.state = self.q0

    # -------------------
    # Reset
    # -------------------
    def reset(self):
        self.state = self.q0

    # -------------------
    # Transitions
    # -------------------
    def transition(self, token):
        token = token.lower()

        # ----------------
        # State q0
        # ----------------
        if self.state == self.q0:
            if token in ["spamword", "fakeclaim"]:
                self.state = self.qSpam
            elif token == "url":
                self.state = self.qU1
            elif token == "hashtag":
                self.state = self.qH1
            else:
                self.state = self.q0
            return

        # ----------------
        # URL states
        # ----------------
        if self.state == self.qU1:
            if token == "url":
                self.state = self.qU2
            elif token in ["spamword", "fakeclaim"]:
                self.state = self.qSpam
            else:
                self.state = self.qU1
            return

        if self.state == self.qU2:
            if token == "url":
                self.state = self.qU3
            elif token in ["spamword", "fakeclaim"]:
                self.state = self.qSpam
            else:
                self.state = self.qU2
            return

        if self.state == self.qU3:
            if token == "url":  # 4th URL
                self.state = self.qSpam
            elif token in ["spamword", "fakeclaim"]:
                self.state = self.qSpam
            else:
                self.state = self.qU3
            return

        # ----------------
        # Hashtag states
        # ----------------
        if self.state == self.qH1:
            if token == "hashtag":
                self.state = self.qH2
            elif token in ["spamword", "fakeclaim"]:
                self.state = self.qSpam
            else:
                self.state = self.qH1
            return

        if self.state == self.qH2:
            if token == "hashtag":
                self.state = self.qH3
            elif token in ["spamword", "fakeclaim"]:
                self.state = self.qSpam
            else:
                self.state = self.qH2
            return

        if self.state == self.qH3:
            if token == "hashtag":  # 4th hashtag
                self.state = self.qSpam
            elif token in ["spamword", "fakeclaim"]:
                self.state = self.qSpam
            else:
                self.state = self.qH3
            return

        # ----------------
        # State Spam
        # ----------------
        if self.state == self.qSpam:
            self.state = self.qSpam
            return

    # -------------------
    # Process text
    # -------------------
    def process_text(self, text):
        self.reset()
        tokens = self.tokenizer.tokenize(text) if self.tokenizer else text.split()
        for tok in tokens:
            self.transition(tok)
        return self.end_of_input()

    # -------------------
    # End of input ($)
    # -------------------
    def end_of_input(self):
        if self.state == self.qSpam:
            return self.qSpam
        return self.qSafe
