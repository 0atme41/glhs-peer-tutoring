from __future__ import print_function
from flask import Flask
from student_sign_up.student_sign_up import student_sign_up_bp
from register.register import register_bp

app = Flask(__name__)
app.register_blueprint(student_sign_up_bp)
app.register_blueprint(register_bp)

currentdirectory = "csgator"

UPLOAD_FOLDER = "static/files"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if __name__ == "__main__":
  app.run(debug=True)