import jwt
from flask import Flask, render_template, request, session
import base64
import os
import random

IMAGES_DIR_NAME = 'images'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'


@app.route('/', methods=['GET'])
def home():
    image_name = random.choice(os.listdir('images'))
    image = os.path.join(IMAGES_DIR_NAME, image_name)

    token = request.args.get('token')
    if token:
        try:
            session['user_role'] = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256']).get('role')
        except jwt.DecodeError as e:
            print(f'ERROR: Invalid signature or expiration date: {e}')
            return '403', 403
        except Exception as e:
            print(f'ERROR: {e}. Dont care')
            return '500', 500

    # TODO: can session['user_role'] be non-None and request.args['token'] be None?
    if session.get('user_role') is None:
        return '403', 403

    if session.get('user_role') == 'admin':
        image_name = request.args.get('img', '1.jpg')
        image = os.path.join(IMAGES_DIR_NAME, image_name)

    with open(image, 'rb') as file:
        img_data = base64.b64encode(file.read()).decode('utf-8')

    return render_template(
        'index.html',
        context={
           'img_data': img_data,
           'role': session.get('user_role')
        }
    )


if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debuger shell
    # if you hit an error while running the server
    app.run(debug=True, host='0.0.0.0', port=8080)