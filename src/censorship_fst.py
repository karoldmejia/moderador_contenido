from pathlib import Path
import json

class CensorshipFST:
    def __init__(self):
        # Upload keywords from keywords.json
        keywords_file = Path(__file__).parent / "data" / "keywords.json"
        with open(keywords_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.badwords = set(word.lower() for word in data.get("badwords", []))
        self.sexwords = set(word.lower() for word in data.get("sexwords", []))
        self.violence = set(word.lower() for word in data.get("violence", []))
        
        # States
        self.q0 = "q0"
        self.qC = "qC"
        self.qF = "qF"
        self.state = self.q0

    def reset(self):
        self.state = self.q0

    def process_text(self, text):
        self.reset()
        output = []
        word_buffer = []  # To create words character by character
        i = 0
        text += " "  # Ensure a word boundary at the end

        while i < len(text):
            char = text[i]

            if self.state == self.q0:
                # We're in normal state
                if char.isalpha():
                    # Start reading a word
                    word_buffer = [char]
                    i += 1
                    # Read the whole word
                    while i < len(text) and text[i].isalpha():
                        word_buffer.append(text[i])
                        i += 1
                    word = "".join(word_buffer)
                    word_lower = word.lower()

                    if word_lower in self.badwords or word_lower in self.sexwords or word_lower in self.violence:
                        # Transition to state qC for censorship
                        self.state = self.qC
                        # Each letter is converted to *
                        output.extend(["*"] * len(word))
                        self.state = self.q0  # Return to q0 at the end of the word
                    else:
                        # Safe word, output is the same
                        output.append(word)
                    # We don't forget the current character if it's non-letter (space, punctuation)
                    if i < len(text) and not text[i].isalpha():
                        output.append(text[i])
                        i += 1
                else:
                    # Non-letter character (spaces, punctuation), output is the same
                    output.append(char)
                    i += 1

            else:
                # If for some reason we're in qC, the word should be processed and return to q0
                self.state = self.q0

        # End of text → final state qF
        self.state = self.qF
        return "".join(output).strip()
