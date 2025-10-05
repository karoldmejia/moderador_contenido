from flask import Flask, render_template, request, redirect, url_for
from src.pipeline import TextPipeline

app = Flask(__name__)
pipeline = TextPipeline()

last_detailed_steps = None

@app.route("/", methods=["GET", "POST"])
def index():
    global last_detailed_steps

    result = None
    warnings = []
    user_text = ""

    if request.method == "POST":
        user_text = request.form["user_text"]
        output = pipeline.run(user_text)
        final = output["final"]
        detailed = output["detailed"]
        result = final["text"]
        warnings = final["warnings"]
        last_detailed_steps = detailed  # guardamos el análisis completo

    # botón se activa solo si ya hay análisis
    detailed_available = last_detailed_steps is not None

    return render_template(
        "index.html",
        result=result,
        warnings=warnings,
        user_text=user_text,
        detailed_available=detailed_available
    )


@app.route("/details")
def details():
    global last_detailed_steps
    if not last_detailed_steps:
        return redirect(url_for("index"))
    return render_template("details.html", steps=last_detailed_steps)


if __name__ == "__main__":
    app.run(debug=True)
