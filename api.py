from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


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


@app.route('/user', methods=['GET'])
def get_users():
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
def get_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

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
def create_user():
    data = request.get_json()

    hashed_pass = generate_password_hash(data["password"], method='sha256')

    new_User = User(public_id=str(uuid.uuid4()),
                    name=data["name"], password=hashed_pass, admin=False)
    db.session.add(new_User)
    db.session.commit()

    return jsonify({'message': 'User Created Successfully....'})


@app.route('/user/<user_id>', methods=["PUT"])
def update_user(user_id):
    return "<h1> Update %s User </h1>" % user_id


@app.route('/user/<user_id>', methods=["DELETE"])
def delete_user(user_id):
    return "<h1> Delete %s User  </h1>" % user_id


if __name__ == '__main__':
    app.run(debug=True)
