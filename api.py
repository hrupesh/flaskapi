from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


app = Flask(__name__)

file_path = os.path.abspath(os.getcwd())+"\data.db"

app.config['secret_key'] = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(80))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


def token_requiered(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({"message": "Token Missing!!"}), 401

        try:
            app.logger.info(token)
            data = jwt.decode(token, str(app.config['SECRET_KEY']))
            app.logger.info(data)
            current_user = User.query.filter_by(
                public_id=data['sub']).first()

        except:
            return jsonify({"message": "Token is Invalid!!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/user', methods=['GET'])
@token_requiered
def get_users(current_user):

    if not current_user.admin:
        return jsonify({"message": "Access Denied, user does not have requsted privelages."})

    users = User.query.all()
    ob = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        ob.append(user_data)

    return jsonify({"users": ob})


@app.route('/user/<public_id>', methods=['GET'])
@token_requiered
def get_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not current_user.admin:
        return jsonify({"message": "Access Denied, user does not have requsted privelages."})

    if not user:
        return jsonify({"message": "No user Found!"})

    user_data = {}
    user_data['id'] = user.id
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({"user": user_data})


@app.route('/user', methods=["POST"])
@token_requiered
def create_user(current_user):

    if not current_user.admin:
        return jsonify({"message": "Access Denied, user does not have requsted privelages."})

    data = request.get_json()
    app.logger.info(data)
    hashed_pass = generate_password_hash(data["password"], method='sha256')

    new_User = User(public_id=str(uuid.uuid4()),
                    name=data["name"], password=hashed_pass, admin=False)
    db.session.add(new_User)
    db.session.commit()

    return jsonify({'message': 'User Created Successfully....'})


@app.route('/user/<public_id>', methods=["PUT"])
@token_requiered
def update_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({"message": "Access Denied, user does not have requsted privelages."})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user Found!"})

    if user.admin:
        return jsonify({"message": "User is already admin."})

    user.admin = True
    db.session.commit()

    return jsonify({"message": "User Promoted to Admin"})


@app.route('/user/<public_id>', methods=["DELETE"])
@token_requiered
def delete_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({"message": "Access Denied, user does not have requsted privelages."})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user Found!"})

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User Deleted!!!!"})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("No Authentication Data Provided", 401, {'WWW-Authenticate': 'basic realm:"Login Required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user or not user.name or not user.password:
        return make_response("No User Found!", 401, {'WWW-Authenticate': 'basic realm:"User Not Found!!"'})

    if check_password_hash(user.password, auth.password):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow(),
            'sub': user.public_id
        }

        token = jwt.encode(
            payload,
            str(app.config['SECRET_KEY'])
        )
        app.logger.info(token)
        return jsonify({"token": token.decode('UTF-8')})

    return make_response("Passwords do not match", 401, {'WWW-Authenticate': 'basic realm:"Access Denied"'})


@app.route('/todo', methods=['GET'])
@token_requiered
def get_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id)

    if not todos:
        return jsonify({"message": "No TODO's Found."})

    obj = []
    for todo in todos:
        todoobj = {}
        todoobj['id'] = todo.id
        todoobj['text'] = todo.text
        todoobj['complete'] = todo.complete
        todoobj['user_id'] = todo.user_id
        obj.append(todoobj)

    return jsonify({"todos": obj})


@app.route('/todo/<todo_id>', methods=['GET'])
@token_requiered
def get_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({"message": "No TODO Found for this id."})

    obj = {}
    obj['id'] = todo.id
    obj['text'] = todo.text
    obj['complete'] = todo.complete
    obj['user_id'] = todo.user_id

    return jsonify({"todo": obj})


@app.route('/todo', methods=['POST'])
@token_requiered
def create_todo(current_user):
    data = request.get_json()

    new_todo = Todo(text=data['text'], complete=False,
                    user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({"message": "TODO Created."})


@app.route('/todo/<todo_id>', methods=['PUT'])
@token_requiered
def completed_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({"message": "No TODO found with this ID."})

    if todo.complete:
        return jsonify({"message": "This TODO is already Completed."})

    todo.complete = True

    db.session.commit()

    return jsonify({"message": "Completed Task (TODO). "})


@app.route('/todo/<todo_id>', methods=['DELETE'])
@token_requiered
def delete_todo(current_user, todo_id):

    todo = Todo.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({"message": "No TODO Found...!!!"})

    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "TODO Deleted!!"})


if __name__ == '__main__':
    app.run(debug=True)
