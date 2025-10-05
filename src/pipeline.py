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

        # 1️⃣ Preprocesamiento (tokenización)
        tokens = self.tokenizer.tokenize(text)
        detailed_steps["tokens"] = tokens

        # 2️⃣ Detección de spam
        spam_state = self.spam_dfa.process_text(text)
        detailed_steps["spam_state"] = spam_state

        # 3️⃣ Detección de contenido inapropiado
        content_state = self.content_dfa.process_text(text)
        detailed_steps["content_state"] = content_state

        # 4️⃣ Recolección de advertencias
        all_warnings = []
        if spam_state != "qSafe":
            all_warnings.append(spam_state)
        if content_state not in ["qF_Safe"]:
            all_warnings.append(content_state)
        detailed_steps["dfa_warnings"] = all_warnings

        # 5️⃣ Aplicación de censura y transformación
        if all_warnings:
            censored_text = self.censorship_fst.process_text(text)
            readable_warnings = [
                self.warning_fst.generate_warning(w)
                for w in all_warnings
                if w
            ]
            final_post = transform_post(censored_text)
        else:
            censored_text = text
            readable_warnings = []
            final_post = transform_post(text)

        detailed_steps["censored_text"] = censored_text
        detailed_steps["readable_warnings"] = readable_warnings
        detailed_steps["final_post"] = final_post

        # 6️⃣ Resultado final simplificado
        final_result = {
            "text": final_post["text"],  # <-- HTML con fórmulas intactas ($...$)
            "warnings": readable_warnings
        }

        # Devolvemos dos niveles: uno para debug, otro para render
        return {
            "detailed": detailed_steps,
            "final": final_result
        }
