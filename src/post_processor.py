import re
from pyparsing import Path
from textx import metamodel_from_file

grammar_path = Path(__file__).parent / "post.tx"
post_mm = metamodel_from_file(str(grammar_path))

# =======================================================
# 1. Simple replacements (regex)
# =======================================================
def enhance_post(text: str) -> dict:
    enhancements_applied = []

    # --- Emojis ---
    emoji_map = {
        ":-)": "😊", ":)": "😊",
        ":-(": "😢", ":(": "😢",
        ":D": "😃", ":-D": "😃",
        ":*": "😘", ":-*": "😘",
        ";)": "😉", ";-)": "😉",
        ":P": "😛", ":-P": "😛",
        "XD": "😆", ":'(": "😭",
        ":O": "😮", ":-O": "😮",
    }
    for k, v in emoji_map.items():
        if k in text:
            text = text.replace(k, v)
            enhancements_applied.append(f"Emoji '{k}' → '{v}'")

    # --- Links ---
    text = re.sub(r"(https?://[^\s]+)", r"<a href='\1' target='_blank'>\1</a>", text)
    enhancements_applied.append("Link detected")

    # --- Mentions ---
    text = re.sub(r"(@\w+)", r"<span class='mention'>\1</span>", text)
    enhancements_applied.append("Mention detected")

    # --- Hashtags ---
    text = re.sub(r"(#\w+)", r"<span class='hashtag'>\1</span>", text)
    enhancements_applied.append("Hashtag detected")

    return {"text": text, "enhancements": enhancements_applied}


# =======================================================
# 2. Rendering functions (TextX)
# =======================================================
def render_formula(node):
    if node is None:
        return ""
    cls = node.__class__.__name__

    if cls == "Frac":
        num = render_formula(node.num)
        den = render_formula(node.den)
        return f"<span class='frac'><span class='num'>{num}</span>/<span class='den'>{den}</span></span>"

    elif cls == "Sqrt":
        index = render_formula(node.index) if getattr(node, "index", None) else ""
        value = render_formula(node.value)
        return f"√<sup>{index}</sup>({value})" if index else f"√({value})"

    elif cls == "SubSup":
        base = node.base
        sup = render_formula(node.sup) if node.sup else ""
        sub = render_formula(node.sub) if node.sub else ""
        html = base
        if sup: html += f"<sup>{sup}</sup>"
        if sub: html += f"<sub>{sub}</sub>"
        return html

    elif cls == "Group":
        return f"({render_formula(node.expr)})"

    elif cls == "Expr":
        parts = []
        terms = getattr(node, "terms", [])
        ops = getattr(node, "op", [])
        for i, term in enumerate(terms):
            part_html = render_formula(term)
            if i < len(ops):
                part_html += f" {ops[i]} "
            parts.append(part_html)
        return "".join(parts)

    elif hasattr(node, "ID") or hasattr(node, "INT"):
        return str(node)
    elif isinstance(node, str):
        return node
    elif cls == "Formula":
        return render_formula(node.expr)
    return str(node)


def render_part(part, enhancements):
    cls = part.__class__.__name__

    if cls == "Bold":
        enhancements.append("Bold formatting")
        text = part._tx_frozen_str.strip("*")
        return f"<b>{text}</b>"

    elif cls == "Italic":
        enhancements.append("Italic formatting")
        text = part._tx_frozen_str.strip("-")
        return f"<i>{text}</i>"

    elif cls == "Underline":
        enhancements.append("Underline formatting")
        text = part._tx_frozen_str.strip("_")
        return f"<u>{text}</u>"

    elif cls == "Font":
        enhancements.append("Font style")
        text = part._tx_frozen_str.strip("/").strip()
        return f"<span style='font-family:cursive'>{text}</span>"

    elif cls == "Formula":
        enhancements.append("Formula rendering")
        return f"<span class='formula'>{render_formula(part)}</span>"

    elif cls in ["Mention", "Hashtag", "Link", "Text"]:
        return part._tx_frozen_str

    else:
        return str(part)


# =======================================================
# 4. Final transformation (integration)
# =======================================================
def transform_post(text: str) -> dict:
    """
    Applies both levels of processing:
    1. Cleaning and emojis (regex)
    2. Structural formatting (TextX)
    """
    # Step 1: apply regex (emojis, mentions, links)
    regex_result = enhance_post(text)
    preprocessed_text = regex_result["text"]
    enhancements = regex_result["enhancements"]

    # Step 2: Parse with TextX (no fallback)
    model = post_mm.model_from_str(preprocessed_text)
    html_parts = [render_part(p, enhancements) for p in model.parts]
    html = " ".join(html_parts)

    return {"text": html, "enhancements": enhancements}
