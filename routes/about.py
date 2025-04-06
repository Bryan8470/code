from flask import Blueprint, request, jsonify, render_template
from db.models import Enkhuils



about_bp = Blueprint('about', __name__)

@about_bp.route('/')
def about():
    users = Enkhuils.query.first()
    f = "I love playing games, and I play piano on the moon"
    return render_template('about.html', 
                           message=f, 
                           name=users.name, 
                           dob=users.dob, 
                           hobby=users.hobby, 
                           grade=users.grade, 
                           age=users.age)