from flask import Blueprint, render_template

tutorials_bp = Blueprint('tutorials', __name__, template_folder="templates")

@tutorials_bp.route("/python")
def python():
    return render_template('tutorials/python_tutorial_main.html')

@tutorials_bp.route('/java')
def java():
    return render_template('tutorials/java_tutorial.html')

@tutorials_bp.route('/html-css')
def html_css():
    return render_template('tutorials/html-css_tutorial.html')

@tutorials_bp.route('/c++')
def cpp():
    return render_template('tutorials/c++_tutorial.html')