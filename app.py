from __future__ import print_function
from flask import Flask
from student_sign_up.student_sign_up import student_sign_up_bp
from tutorials.tutorials import tutorials_bp
from glex.glex import glex_bp
from homepage.homepage import homepage_bp
from projects.projects import projects_bp
from seating_chart.seating_chart import seating_chart_bp

app = Flask(__name__)
app.register_blueprint(homepage_bp)
app.register_blueprint(student_sign_up_bp)
app.register_blueprint(tutorials_bp)
app.register_blueprint(glex_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(seating_chart_bp)

currentdirectory = "csgator"

UPLOAD_FOLDER = "static/files"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if __name__ == "__main__":
  app.run(debug=True)