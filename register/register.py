from flask import Blueprint, render_template, request
import sqlite3

register_bp = Blueprint('register', __name__, template_folder="templates")

@register_bp.route('/register')
def register_main():
    return render_template("register/register_main.html")

@register_bp.route('/register-student')
def register_student():
    return render_template("register/register_student.html")

@register_bp.route('/register-tutor', methods=["GET", "POST"])
def register_tutor():
    email = request.form.get('email')
    if email:
        connection = sqlite3.connect("student_sign_up/tutoring.db")
        cursor = connection.cursor()
        t_list = cursor.execute("SELECT t_fn, t_ln FROM tutors WHERE email = ?", (email,)).fetchall()
        if t_list:
            t_fn, t_ln = t_list[0]
            t_name = t_fn + " " + t_ln
        else:
            t_name = "No Email"
    else:
        t_name = None
    return render_template("register/register_tutor.html", t_name=t_name)