from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

file_path = os.path.abspath(os.getcwd())+"\data.db"

app.config['secret_key'] = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


@app.route('/user', methods=['GET'])
def get_users():
    return "<h1> Get All Users </h1> "


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    return "<h1>Get  %s User</h1>" % user_id


@app.route('/user', methods=["POST"])
def create_user():
    return "<h1>Create User</h1>"


@app.route('/user/<user_id>', methods=["PUT"])
def update_user(user_id):
    return "<h1> Update %s User </h1>" % user_id


@app.route('/user/<user_id>', methods=["DELETE"])
def delete_user(user_id):
    return "<h1> Delete %s User  </h1>" % user_id


if __name__ == '__main__':
    app.run(debug=True)
