from src.censorship_fst import CensorshipFST
from src.content_dfa import ContentDFA
from src.post_processor import transform_post
from src.preprocessing import RegexTokenizer
from src.spam_dfa import SpamDFA
from src.warning_fst import WarningFST


class TextPipeline:
    def __init__(self):
        self.tokenizer = RegexTokenizer("data/keywords.json")
        self.spam_dfa = SpamDFA()
        self.content_dfa = ContentDFA()
        self.censorship_fst = CensorshipFST()
        self.warning_fst = WarningFST()

    def run(self, text):
        detailed_steps = {}

        # 1. Preprocessing (tokenization)
        tokens = self.tokenizer.tokenize(text)
        detailed_steps["tokens"] = tokens

        # 2. Spam DFA
        spam_state = self.spam_dfa.process_text(text)
        detailed_steps["spam_state"] = spam_state

        # 3. Directionality and Content DFA
        content_state = self.content_dfa.process_text(text)
        detailed_steps["content_state"] = content_state

        # 4. Warnings detected
        all_warnings = []
        if spam_state != "qSafe":
            all_warnings.append(spam_state)
        if content_state not in ["qF_Safe"]:
            all_warnings.append(content_state)
        detailed_steps["dfa_warnings"] = all_warnings

        # 5. FSTs and final transformation (only if there are warnings)
        if all_warnings:
            censored_text = self.censorship_fst.process_text(text)
            readable_warnings = [
                self.warning_fst.generate_warning(w) for w in all_warnings
            ]
            final_post = transform_post(censored_text)
        else:
            censored_text = text
            readable_warnings = []
            final_post = transform_post(text)

        detailed_steps["censored_text"] = censored_text
        detailed_steps["readable_warnings"] = [w for w in readable_warnings if w]
        detailed_steps["final_post"] = final_post

        # Final results summarized for the “final hearing”
        final_result = {
            "text": final_post["text"],
            "enhancements": final_post["enhancements"],
            "warnings": detailed_steps["readable_warnings"]
        }

        return {"detailed": detailed_steps, "final": final_result}
