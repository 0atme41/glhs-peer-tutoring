from flask import Blueprint, render_template, request
import sqlite3

accounts_bp = Blueprint('accounts', __name__, template_folder="templates")

@accounts_bp.route('/create-account')
def create_account_main():
    return render_template("accounts/create_account_main.html")

@accounts_bp.route('/create-account-tutors', methods=['GET', 'POST'])
def create_account_tutors():
    email = request.form.get('email')
    if email:
        connection = sqlite3.connect("student_sign_up/tutoring.db")
        cursor = connection.cursor()
        # = cursor.execute("SELECT t_id, fn, ln FROM tutors WHERE email = ?", (email,)).fetchall()
        cursor.close()
    
    return render_template("accounts/create_account_tutors.html", found_email=None)

@accounts_bp.route('/create-account-students')
def create_account_students():
    return render_template("accounts/create_account_students.html")