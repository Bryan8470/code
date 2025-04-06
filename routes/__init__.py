from flask import Blueprint
from .calculator import calculator_bp
from .about import about_bp


def register_blueprints(app):
    app.register_blueprint(calculator_bp, url_prefix='/calculator')
    app.register_blueprint(about_bp, url_prefix='/about')
 