from flask import Blueprint, render_template

homepage_bp = Blueprint('homepage', __name__, template_folder="templates")

@homepage_bp.route('/')
def homepage():
    return render_template('homepage/homepage.html')