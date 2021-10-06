import jwt
from flask import Flask, render_template, request, session
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'


@app.route('/', methods=['GET'])
def home():
    image = 'serval.jpeg'
    token = request.args.get('token')
    if token:
        try:
            session['user_role'] = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256']).get('role')
        except:
            print('Invalid signature or expiration date. Dont care')
            return '403', 403
    if session.get('user_role') is None:
        return '403', 403
    if session.get('user_role') == 'admin':
        image = request.args.get('img', 'serval.jpeg')
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
    app.run(debug=True, host='0.0.0.0', port=8000)