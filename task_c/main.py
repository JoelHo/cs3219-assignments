# Reference: https://realpython.com/token-based-authentication-with-flask/
# Reference: https://www.bacancytechnology.com/blog/flask-jwt-authentication

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'sOmEsEcReTkEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fakedb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    permissions = db.Column(db.Integer)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(100))


class Permission(db.Model):
    bit = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')
        else:
            return make_response('Login Required!', 401, {'Authentication': '"login required"'})

        try:
            data = jwt.decode(token[1], app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(uuid=data['public_id']).first()
        except Exception as e:
            return make_response('Invalid token!', 401, {'Authentication': 'token is invalid'})

        if datetime.datetime.utcfromtimestamp(data['exp']) < datetime.datetime.utcnow():
            return make_response('Token expired, please login again', 401, {'Authentication': 'token is expired'})

        permissions = db.session.query(Permission.name).filter(Permission.bit.op('&')(current_user.permissions)).all()
        permissions = [x[0] for x in permissions]

        return f(current_user, permissions, *args, **kwargs)

    return decorator


@app.route('/register', methods=['POST'])
def signup_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(
        uuid=str(uuid.uuid4()),
        username=data['username'],
        password=hashed_password,
        permissions=data['permissions']
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})


@app.route('/login', methods=['POST'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Invalid login request!', 401, {'Authentication': 'login required"'})

    user = User.query.filter_by(username=auth.username).first()

    if user and check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                'public_id': user.uuid,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            },
            app.config['SECRET_KEY'],
            "HS256"
        )
        return make_response(jsonify({
            'message': 'Logged in',
            'token': token
        }), 200)

    return make_response('User not found!', 401, {'Authentication': 'login required'})


@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user, permissions):
    if 'CAN_ADMIN' not in permissions:
        return make_response('Not authorised!', 403, {'Authentication': 'Not authorised!'})

    users = User.query.all()
    result = []
    for user in users:
        user_data = {
            'public_id': user.uuid,
            'name': user.username,
            'password': user.password,
            'permissions': user.permissions
        }

        result.append(user_data)

    return jsonify({'users': result})


@app.route('/entry', methods=['POST', 'GET'])
@token_required
def entry(current_user, permissions):
    if request.method == 'POST':
        if 'CAN_WRITE' not in permissions:
            return make_response('Not authorised!', 403, {'Authentication': 'Not authorised!'})
        data = request.get_json()

        new_books = Entry(
            user_id=current_user.id,
            author=current_user.username,
            title=data['title'],
            content=data['content']

        )
        db.session.add(new_books)
        db.session.commit()

        return jsonify({'message': 'new entry created'})
    else:
        if 'CAN_READ' not in permissions:
            return make_response('Not authorised!', 403, {'Authentication': 'Not authorised!'})

        if 'CAN_ADMIN' in permissions:
            entries = Entry.query.all()
        else:
            entries = Entry.query.filter_by(user_id=current_user.id).all()

        output = []
        for e in entries:
            entry_data = {
                'id': e.id,
                'author': e.author,
                'title': e.title,
                'content': e.content
            }
            output.append(entry_data)

        return jsonify({'entries': output})


@app.route('/entry/<entry_id>', methods=['DELETE'])
@token_required
def delete_entry(current_user, permissions, entry_id):
    if 'CAN_DELETE' not in permissions:
        return make_response('Not authorised!', 403, {'Authentication': 'Not authorised!'})

    e = Entry.query.filter_by(id=entry_id).first()

    if not e:
        return jsonify({'message': 'entry does not exist'})

    if 'CAN_ADMIN' not in permissions and e.author != current_user.uuid:
        return jsonify({'message': 'cannot delete entry not owned by you'})

    db.session.delete(e)
    db.session.commit()

    return jsonify({'message': 'entry deleted'})


if __name__ == '__main__':
    app.run(debug=True)
