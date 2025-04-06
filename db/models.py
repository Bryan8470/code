from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db



class Enkhuils(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    dob = db.Column(db.String(120), nullable=True)
    hobby = db.Column(db.String(120), nullable=True)
    grade = db.Column(db.String(120), nullable=True)
    age = db.Column(db.String(120), nullable=True)


    def __repr__(self):
        return f'<Role {self.name}>'
