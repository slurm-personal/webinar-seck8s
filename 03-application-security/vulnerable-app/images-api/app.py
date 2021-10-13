import base64
import os
import random

import jwt
from flask import Flask, render_template, request, session

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["IMAGES_DIR_NAME"] = "images"

@app.route("/", methods=["GET", "POST"])
def home():
    image_name = random.choice(os.listdir("images"))
    image = os.path.join(app.config["IMAGES_DIR_NAME"], image_name)

    # TODO: should pass token via POST parameters
    token = request.args.get("token")
    if not token:
        return "401 Unauthorized (missing token)", 401

    try:
        key = app.config["SECRET_KEY"]
        session["user_role"] = jwt.decode(token, key, algorithms=["HS256"]).get("role")
    except jwt.DecodeError as e:
        print(f"ERROR: Invalid signature or expiration date: {e}")
        return "403 Forbidden (invalid token)", 403
    except Exception as e:
        print(f"ERROR: {e}. Dont care")
        return "500 Internal Server Error", 500

    # File upload functionality
    if 'file' in request.files:
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file and file.filename:
            new_file = os.path.join(app.config['IMAGES_DIR_NAME'], file.filename)
            file.save(new_file)
            # return f"Saved file: {os.path.abspath(new_file)}", 200
            return render_template(
                "saved_success.html",
                context={
                    "new_file": new_file,
                    "token": token,
                },
            )

    # File read functionality
    if session.get("user_role") == "admin":
        image_name = request.args.get("img") or "1.jpg"
        image = os.path.join(app.config["IMAGES_DIR_NAME"], image_name)
    with open(image, "rb") as f:
        img_data = base64.b64encode(f.read()).decode("utf-8")

    return render_template(
        "index.html",
        context={
            "img_data": img_data,
            "role": session.get("user_role"),
            "token": token,
        },
    )


if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debuger shell
    # if you hit an error while running the server
    app.run(debug=True, host="0.0.0.0", port=8080)
