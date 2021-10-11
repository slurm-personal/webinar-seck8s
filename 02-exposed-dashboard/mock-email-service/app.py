import logging
import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, make_response, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

# Debug mode by default: on production, might leak secrets
DEBUG = bool(os.environ.get("DEBUG", True))

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger("ganimed")

CURRENT_DIR = Path(__file__).parent
TEMPLATES_DIR = CURRENT_DIR / "templates"

app = Flask(__name__)


DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ.get("DB_PORT", 3306)
DB_DATABASE = os.environ["DB_DATABASE"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
connection = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
)

app.config["SQLALCHEMY_DATABASE_URI"] = connection
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True


db = SQLAlchemy(app)

class EmailData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    to = db.Column(db.String(70))
    public_id = db.Column(db.String(50), unique=True)
    subject = db.Column(db.String(100))
    confirm_url = db.Column(db.String(100))
    html_template = db.Column(db.String(100))
    txt_template = db.Column(db.String(100))

    def __repr__(self):
        # Overload repr so that to print the whole object to the log
        mid = ", ".join(
            [
                f"{k}={repr(v)}"
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            ]
        )
        return f"EmailData({mid})"


db.create_all()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    params = request.form

    to_email = params.get("to_email")
    if not to_email:
        return make_response("Missing parameter 'to_email'", 400)

    subject = params.get("subject", "Email confirmation")
    public_id = uuid.uuid4()
    confirm_url = (
        f"https://fakeemailconfirm.appspot.com/email-confirm/{public_id.hex[:20]}/"
    )
    html_template = "emails/email_confirm.html"
    txt_template = "emails/email_confirm.txt"

    data = EmailData(
        to=to_email,
        public_id=str(public_id),
        subject=subject,
        confirm_url=confirm_url,
        html_template=html_template,
        txt_template=txt_template,
    )
    logger.debug(f"Request received: {data}")  # <-- Data leakage point
    db.session.add(data)
    db.session.commit()

    return redirect("/success")


@app.route("/success", methods=["GET"])
def success():
    return render_template("success.html")


if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debuger shell
    # if you hit an error while running the server
    app.run(host="0.0.0.0", port=8080, debug=DEBUG)
