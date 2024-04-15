from flask import Blueprint, render_template, request
import sqlite3
import smtplib, ssl
from email.message import EmailMessage

def email_student(email):
    connection = sqlite3.connect("student_sign_up/tutoring.db")
    cursor = connection.cursor()
    fn, subject, t_id = cursor.execute("SELECT fn, subject, t_id FROM students WHERE email = ?", (email,)).fetchall()[-1]
    cursor.close()

    if t_id > 0:
        cursor = connection.cursor()
        t_ln, t_fn, t_email = cursor.execute("SELECT t_ln, t_fn, email FROM tutors WHERE t_id = ?", (t_id,)).fetchall()[0]
        cursor.close()

    message = EmailMessage()

    if t_id > 0:
        message["Subject"] = "Tutor Found!"
        content = f"""Hi {fn}!

We've successfully matched you with a tutor. Email {t_fn} {t_ln} at {t_email} to set up a time for {subject} tutoring.

Sincerely, the CSGator Team"""
    elif t_id == 0:
        message["Subject"] = "Tutor in the Works"
        content = f"""Hi {fn}!

As of right now, we haven't been able to pair you with one of our tutors. You will receive an email when a tutor has been found. Thank you for your patience!

Sincerely, the CSGator Team"""

    message['From'] = "pythonsmtpssltest@gmail.com"
    message['To'] = email

    message.set_content(content)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login("pythonsmtpssltest@gmail.com", "kdak sdyf mpvq nduj")
        s.sendmail("pythonsmtpssltest@gmail.com", email, message.as_string())
    
def email_tutor(student_email):
    connection = sqlite3.connect("student_sign_up/tutoring.db")
    cursor = connection.cursor()
    ln, fn, subject, t_id = cursor.execute("SELECT ln, fn, subject, t_id FROM students WHERE email = ?", (student_email,)).fetchall()[-1]
    cursor.close()

    cursor = connection.cursor()
    t_fn, t_email = cursor.execute("SELECT t_fn, email FROM tutors WHERE t_id = ?", (t_id,)).fetchall()[0]
    cursor.close()
        
    message = EmailMessage()

    message["Subject"] = "Student Found!"
    content = f"""Hi {t_fn}!

We've successfully matched you with a student. Email {fn} {ln} at {student_email} to set up a time for {subject} tutoring.

Sincerely, the CSGator Team"""
        
    message['From'] = "pythonsmtpssltest@gmail.com"
    message['To'] = t_email

    message.set_content(content)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login("pythonsmtpssltest@gmail.com", "kdak sdyf mpvq nduj")
        s.sendmail("pythonsmtpssltest@gmail.com", t_email, message.as_string())

student_sign_up_bp = Blueprint('student_sign_up', __name__, template_folder="templates")

subjects = []
with open('student_sign_up/static/classList.txt', 'r') as classFile:
    subjects = classFile.readlines()

@student_sign_up_bp.route('/student-sign-up', methods=['GET', 'POST'])
def student_sign_up():
    connection = sqlite3.connect("student_sign_up/tutoring.db")

    fn = request.form.get('fn')
    ln = request.form.get('ln')
    email = request.form.get('email')
    subject = request.form.get('subject')

    t_id = []
    if subject:
        subject = subject.strip()
        cursor = connection.cursor()
        t_id = cursor.execute("SELECT t_id FROM tutors WHERE subject = ?", (subject,)).fetchall()
        cursor.close()

        if len(t_id) == 0:
            t_id = 0
            
        else:
            t_id = t_id[0][0]
        
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (fn, ln, email, subject, t_id) VALUES (?, ?, ?, ?, ?)", (fn, ln, email, subject, t_id))
        connection.commit()
        cursor.close()
        
        email_student(email)
        if t_id > 0:
            email_tutor(email)

    return render_template('student_sign_up/student_sign_up.html', subjects = subjects)
