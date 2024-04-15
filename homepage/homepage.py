from flask import Blueprint, render_template

homepage_bp = Blueprint('homepage', __name__, template_folder="templates", static_folder="static", static_url_path="/homepage/static")

@homepage_bp.route('/')
def homepage():
    return render_template('homepage/homepage.html')