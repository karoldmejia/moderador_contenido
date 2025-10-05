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
        ":-)": "\U0001F60A",  # 😊
        ":)": "\U0001F60A",
        ":-(": "\U0001F622",  # 😢
        ":(": "\U0001F622",
        ":D": "\U0001F603",  # 😃
        ":-D": "\U0001F603",
        ":*": "\U0001F618",  # 😘
        ":-*": "\U0001F618",
        ";)": "\U0001F609",  # 😉
        ";-)": "\U0001F609",
        ":P": "\U0001F61B",  # 😛
        ":-P": "\U0001F61B",
        "XD": "\U0001F606",  # 😆
        ":'(": "\U0001F62D",  # 😭
        ":O": "\U0001F62E",  # 😮
        ":-O": "\U0001F62E",
    }
    for k, v in emoji_map.items():
        if k in text:
            text = text.replace(k, v)
            enhancements_applied.append(f"Emoji '{k}' → '{v}'")
    
    # --- Links ---
    link_count = len(re.findall(r"(https?://[^\s]+)", text))
    if link_count > 0:
        text = re.sub(r"(https?://[^\s]+)", r"<a href='\1' target='_blank'>\1</a>", text)
        enhancements_applied.append("Link detected")

    # --- Mentions ---
    mention_count = len(re.findall(r"(@\w+)", text))
    if mention_count > 0:
        text = re.sub(r"(@\w+)", r"<span class='mention'>\1</span>", text)
        enhancements_applied.append("Mention detected")

    # --- Hashtags ---
    hashtag_count = len(re.findall(r"(#\w+)", text))
    if hashtag_count > 0:
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

    # Fractions
    if cls == "Frac":
        num = render_formula(node.num)
        den = render_formula(node.den)
        result = f"\frac{{{num}}}{{{den}}}"
        return result

    # Square roots
    elif cls == "Sqrt":
        value = render_formula(node.value)
        if getattr(node, "index", None):
            index = render_formula(node.index)
            result = f"\sqrt[{index}]{{{value}}}"
        else:
            result = f"\sqrt{{{value}}}"
        return result

    # Subscripts / Superscripts
    elif cls == "SubSup":
        base = render_formula(node.base)
        sup = f"^{{{render_formula(node.sup)}}}" if getattr(node, "sup", None) else ""
        sub = f"_{{{render_formula(node.sub)}}}" if getattr(node, "sub", None) else ""
        result = f"{base}{sup}{sub}"
        return result

    # Agrupation
    elif cls == "Group":
        inner = render_formula(node.expr)
        result = inner 
        return result

    # Expressions with operators
    elif cls == "Expr":
        s = render_formula(getattr(node, "first", node.terms[0] if hasattr(node, "terms") else node))
        for pair in getattr(node, "rest", []):
            s += f" {pair.op} " + render_formula(pair.term)
        return s

    # Full formula
    elif cls == "Formula":
        result = render_formula(node.expr)
        return result

    # Simple nodes with attributes
    elif hasattr(node, "ID"):
        result = str(node.ID)
        return result
    elif hasattr(node, "INT"):
        result = str(node.INT)
        return result

    # Atom
    elif cls == "Atom":
        if hasattr(node, "ID"):
            result = str(node.ID)
        elif hasattr(node, "INT"):
            result = str(node.INT)
        else:
            result = "[Atom]"
        return result

    # Direct value
    elif hasattr(node, "value"):
        result = render_formula(node.value)
        return result

    # Detect numbers and direct strings
    elif isinstance(node, int) or isinstance(node, float):
        return str(node)
    elif isinstance(node, str):
        return node

    # Fallback: frozen string
    elif hasattr(node, "_tx_frozen_str"):
        result = node._tx_frozen_str
        return result

    # Last resource
    result = f"[{cls}]"
    return result

def render_part(part, enhancements):
    cls = part.__class__.__name__

    if cls == "Bold":
        enhancements.append("Bold formatting")
        text = part._tx_frozen_str.strip("*")
        result = f"<b>{text}</b>"
        return result

    elif cls == "Italic":
        enhancements.append("Italic formatting")
        text = part._tx_frozen_str.strip("-")
        result = f"<i>{text}</i>"
        return result

    elif cls == "Underline":
        enhancements.append("Underline formatting")
        text = part._tx_frozen_str.strip("_")
        result = f"<u>{text}</u>"
        return result

    elif cls == "Font":
        enhancements.append("Font style")
        text = part._tx_frozen_str.strip("/").strip()
        result = f"<span style='font-family:cursive'>{text}</span>"
        return result

    elif cls == "Formula":
        enhancements.append("Formula rendering")
        try:
            # Render the formula expression in LaTeX
            rendered_formula = render_formula(part.expr)
            # Return the original LaTeX with $ for MathJax
            result = f"${rendered_formula}$"
            return result
        except Exception as e:
            # If there's an error, use the original text as a fallback
            original_text = getattr(part, '_tx_frozen_str', f"${part.expr}$")
            result = original_text
            return result

    elif cls in ["Mention", "Hashtag", "Link", "Text"]:
        result = part._tx_frozen_str
        return result

    else:
        result = str(part)
        return result


# =======================================================
# 4. Final transformation (integration)
# =======================================================

def transform_post(text: str) -> dict:
    """
    Transforms a post by applying visual enhancements and rendering mathematical formulas.
    Returns the final HTML and a list of applied enhancements.
    """
    regex_result = enhance_post(text)
    preprocessed_text = regex_result["text"]
    enhancements = regex_result["enhancements"]

    html_parts = []

    try:
        # Try to parse the entire text with TextX
        model = post_mm.model_from_str(preprocessed_text)
        for p in model.parts:
            rendered_part = render_part(p, enhancements)
            html_parts.append(rendered_part)

    except Exception:
        # If the global parsing fails, try splitting by formulas ($...$)
        html_parts = []
        segments = re.split(r'(\$[^$]+\$)', preprocessed_text)

        for segment in segments:
            if not segment.strip():
                continue

            # If the segment looks like a formula
            if segment.startswith('$') and segment.endswith('$'):
                formula_content = segment[1:-1]
                try:
                    formula_model = post_mm.model_from_str(f"${formula_content}$")
                    formula_part = formula_model.parts[0]
                    rendered_formula = render_part(formula_part, enhancements)
                    html_parts.append(rendered_formula)
                except Exception:
                    # If the formula can't be parsed, show it as error text
                    error_html = f'<span class="formula-error">{segment}</span>'
                    html_parts.append(error_html)
                    enhancements.append("Invalid formula detected")
            else:
                # Normal text (not a formula)
                html_parts.append(segment)

    # Build the final HTML
    html = " ".join(html_parts)

    return {"text": html, "enhancements": enhancements}