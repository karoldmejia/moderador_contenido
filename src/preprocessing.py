import re
import json

class RegexTokenizer:
    def __init__(self, keywords_file="keywords.json"):
        with open(keywords_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Simple word sets
        self.badwords = set(data["badwords"])
        self.sexwords = set(data["sexwords"])
        self.violence = set(data["violence"])
        self.spamwords = sorted(data["spamwords"], key=lambda x: -len(x))
        self.fakeclaims = sorted(data["fakeclaims"], key=lambda x: -len(x))
        self.politics = set(data["politics"])
        self.pronouns = set(data["pronouns"])
        self.pronouns_self = set(data["pronouns_self"])
        self.pronouns_other = set(data["pronouns_other"])
        self.pronouns_group = set(data["pronouns_group"])
        self.aux_verbs = set(data["aux_verbs"])
        self.bad_emojis = set(data["bademojis"])

        # Regex patterns
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
        # Insert spaces before and after each emoji
        return self.patterns["EMOJI"].sub(r' \g<0> ', text)

    def tokenize(self, text):
        # 1. Separate emojis attached to words
        text = self.separate_emojis(text)

        # 2. Replace multi-word phrases first
        text = self.replace_phrases(text, self.spamwords, "SPAMWORD")
        text = self.replace_phrases(text, self.fakeclaims, "FAKECLAIM")

        tokens = []
        for word in text.split():
            word_lower = word.lower()

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

            # Simple word categories (one word)
            if any(bw in word_lower for bw in self.badwords):
                tokens.append("BADWORD")
                continue
            if any(sw in word_lower for sw in self.sexwords):
                tokens.append("SEXWORD")
                continue
            if any(vw in word_lower for vw in self.violence):
                tokens.append("VIOLENCE")
                continue
            if any(p in word_lower for p in self.politics):
                tokens.append("POLITIC")
                continue
            if word_lower in self.pronouns_self:
                tokens.append("PRONOUN_SELF")
                continue
            if word_lower in self.pronouns_other:
                tokens.append("PRONOUN_OTHER")
                continue
            if word_lower in self.pronouns_group:
                tokens.append("PRONOUN_GROUP")
                continue
            if word_lower in self.pronouns:
                tokens.append("PRONOUN")
                continue
            if word_lower in self.aux_verbs:
                tokens.append("AUX_VERB")
                continue

            # Multi-word phrases already replaced
            if word in ["SPAMWORD", "FAKECLAIM"]:
                tokens.append(word)
                continue

            # Emojis
            if self.patterns["EMOJI"].match(word):
                tokens.append("NEG_EMOJI" if word in self.bad_emojis else "EMOJI")
                continue

            # Normal words
            if self.patterns["WORD"].match(word):
                tokens.append("WORD")
                continue

            # Anything else
            tokens.append("WORD")

        return tokens
