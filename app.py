from flask import Flask, render_template, request, abort, make_response
from eco_engine import analyze_website
import db
from pdf_report import build_pdf

app = Flask(__name__)
db.init_db()


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    saved_id = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()

        # Auto-add https:// if missing
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url

        result = analyze_website(url)
        if result:
            saved_id = db.insert_analysis(result)

    latest = db.get_latest(10)
    top_green = db.get_top_green(10)

    return render_template(
        "index.html",
        result=result,
        saved_id=saved_id,
        latest=latest,
        top_green=top_green
    )


@app.route("/report/<int:row_id>")
def report(row_id):
    row = db.get_one(row_id)
    if not row:
        abort(404)

    pdf_bytes = build_pdf(row)

    # Mac/Chrome safe PDF download response
    resp = make_response(pdf_bytes)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = f'attachment; filename="EcoWeb_Report_{row_id}.pdf"'
    return resp


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
