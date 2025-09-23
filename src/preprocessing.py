import re
import json

class RegexTokenizer:
    def __init__(self, keywords_file="keywords.json"):
        with open(keywords_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.badwords = set(data["badwords"])
        self.sexwords = set(data["sexwords"])
        self.violence = set(data["violence"])
        self.drugs = set(data["drugs"])
        self.selfharm = set(data["selfharm"])
        self.spamwords = sorted(data["spamwords"], key=lambda x: -len(x))
        self.fakeclaims = sorted(data["fakeclaims"], key=lambda x: -len(x))
        self.politics = set(data["politics"])
        self.pronouns = set(data["pronouns"])
        self.bad_emojis = set(data["bademojis"])

        self.patterns = {
            "URL": re.compile(r"(https?:\/\/[^\s]+)"),
            "HASHTAG": re.compile(r"(#[\w\d_]+)"),
            "MENTION": re.compile(r"(@[\w\d_]+)"),
            "WORD": re.compile(r"\b[a-zA-Z]+\b"),
            "EMOJI": re.compile(r"[\U0001F300-\U0001FAFF]")
        }

    def replace_phrases(self, text, phrases, token):
        for phrase in phrases:
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            text = pattern.sub(token, text)
        return text

    def separate_emojis(self, text):
        # Inserta espacios antes y después de cada emoji
        return self.patterns["EMOJI"].sub(r' \g<0> ', text)

    def tokenize(self, text):
        # 1. Separar emojis pegados a palabras
        text = self.separate_emojis(text)

        # 2. Reemplazar frases multi-palabra
        text = self.replace_phrases(text, self.spamwords, "SPAMWORD")
        text = self.replace_phrases(text, self.fakeclaims, "FAKECLAIM")

        tokens = []
        for word in text.split():
            word_lower = word.lower()

            # Categorías simples (una palabra)
            if word_lower in self.badwords:
                tokens.append("BADWORD")
                continue
            if word_lower in self.sexwords:
                tokens.append("SEXWORD")
                continue
            if word_lower in self.violence:
                tokens.append("VIOLENCE")
                continue
            if word_lower in self.drugs:
                tokens.append("DRUG")
                continue
            if word_lower in self.selfharm:
                tokens.append("SELFHARM")
                continue
            if word_lower in self.politics:
                tokens.append("POLITIC")
                continue
            if word_lower in self.pronouns:
                tokens.append("PRONOUN")
                continue

            # Frases ya reemplazadas
            if word in ["SPAMWORD", "FAKECLAIM"]:
                tokens.append(word)
                continue

            # URLs, hashtags, mentions
            if self.patterns["URL"].match(word):
                tokens.append("URL")
                continue
            if self.patterns["HASHTAG"].match(word):
                tokens.append("HASHTAG")
                continue
            if self.patterns["MENTION"].match(word):
                tokens.append("MENTION")
                continue

            # Emojis
            if self.patterns["EMOJI"].match(word):
                tokens.append("NEG_EMOJI" if word in self.bad_emojis else "EMOJI")
                continue

            # Palabras normales
            if self.patterns["WORD"].match(word):
                tokens.append("WORD")
                continue

            # Cualquier otra cosa
            tokens.append("WORD")

        return tokens
