class WarningFST:
    def __init__(self):
        # Diccionario de estados finales a advertencias
        self.transitions = {
            "qSpam": "this post may contain spam",
            "qF_Offensive": "this post may contain offensive language",
            "qF_Hate": "this post may contain hate speech",
            "qF_Sex": "this post may contain sexual content",
            "qF_Harass": "this post may contain harassment",
            "qF_SelfHarm": "this post may contain self-harm",
            "qF_Threats": "this post may contain threats",
            "qF_Violence": "this post may contain violence",
        }

    def generate_warning(self, final_state: str) -> str:
        """
        Dado un estado final de los DFAs,
        devuelve el mensaje de advertencia correspondiente
        o None si no hay advertencia.
        """
        return self.transitions.get(final_state, None)
