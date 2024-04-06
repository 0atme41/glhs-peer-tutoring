from __future__ import print_function
from flask import Flask, render_template, request, url_for, flash, redirect
import pgeocode
import googlemaps
import folium
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import cairo
import random
from fpdf import FPDF
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import time
import csv

os.environ["TZ"] = "America/New_York"
time.tzset()

login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kmykey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

login_manager.init_app(app)
login_manager.login_view = 'login'

subjects = []
with open('classList.txt', 'r') as classFile:
    subjects = classFile.readlines()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    comment_list = db.relationship('Comment',backref='user',lazy='dynamic')
    reply_list = db.relationship('Reply',backref='user',lazy='dynamic')
    account_type = db.Column(db.String)


    def __init__(self,email,username,password,account_type_code):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        if account_type_code == 'PCdWS0n432i5$IK6B*k$':
            account_type = 'Admin'
        elif account_type_code == 'glhs23_$3' and '@students.wcpss.net' in self.email:
            account_type = 'Student'
        else:
            account_type = 'Standard'
        self.account_type = account_type

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def set_email(self,new_email):
        if self.account_type == 'Student' and '@students.wcpss.net' not in new_email:
            self.account_type = 'Standard'
        self.email = new_email

    def set_type(self,account_type_code):
        if account_type_code == 'PCdWS0n432i5$IK6B*k$':
            account_type = 'Admin'
        elif account_type_code == 'glhs23_$3' and '@students.wcpss.net' in self.email:
            account_type = 'Student'
        else:
            account_type = 'Standard'
        self.account_type = account_type

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    comment = db.Column(db.String)
    title = db.Column(db.String(128))
    c_username = db.Column(db.String,db.ForeignKey('users.username'))
    c_email = db.Column(db.String)
    reply_list = db.relationship('Reply',backref='comment',lazy='dynamic')
    timestamp = db.Column(db.DateTime)
    c_admin = db.Column(db.Boolean)

    def __init__(self,comment,title,c_username,c_email,timestamp,c_admin):
        self.comment = comment
        self.title = title
        self.c_username = c_username
        self.c_email = c_email
        self.timestamp = timestamp
        self.c_admin = c_admin

class CommentArchive(db.Model):
    __tablename__ = 'comment_archive'
    id = db.Column(db.Integer, primary_key = True)
    comment = db.Column(db.String)
    title = db.Column(db.String(128))
    c_username = db.Column(db.String,db.ForeignKey('users.username'))
    c_email = db.Column(db.String)
    timestamp = db.Column(db.String)

    def __init__(self,comment,title,c_email,c_username,timestamp):
        self.comment = comment
        self.title = title
        self.c_email = c_email
        self.c_username = c_username
        self.timestamp = timestamp

class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key = True)
    reply = db.Column(db.String)
    r_username = db.Column(db.String,db.ForeignKey('users.username'))
    r_email = db.Column(db.String)
    r_comment = db.Column(db.Integer,db.ForeignKey('comments.id'))
    timestamp = db.Column(db.DateTime)
    r_admin = db.Column(db.Boolean)

    def __init__(self,reply,r_username,r_email,r_comment,timestamp,r_admin):
        self.reply = reply
        self.r_email = r_email
        self.r_username = r_username
        self.r_comment = r_comment
        self.timestamp = timestamp
        self.r_admin = r_admin

class ReplyArchive(db.Model):
    __tablename__ = 'reply_archive'
    id = db.Column(db.Integer, primary_key = True)
    reply = db.Column(db.String)
    r_username = db.Column(db.String,db.ForeignKey('users.username'))
    r_email = db.Column(db.String)
    timestamp = db.Column(db.String)

    def __init__(self,reply,r_username,r_email,timestamp):
        self.reply = reply
        self.r_username = r_username
        self.r_email = r_email
        self.timestamp = timestamp

@app.route('/loggedin')
@login_required
def logged_in():
    return render_template('logged_in.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You logged out")
    return redirect(url_for('welcome'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.")
            next = request.args.get('next')

            if next == None or not next[0] == '/':
                next = url_for('welcome')

            return redirect(next)
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        account_type_code = request.form.get('account_type_code')
        if email == '' or username == '':
            return render_template('register.html', helpers=[])

        pass_quals = {
            'num': 'Have at least one number ',
            'upper': 'Have at least one upper case letter ',
            'lower': 'Have at least one lower case letter ',
            'special': 'Have at least one special letter ',
            'length': 'Be at least twelve characters long '
        }
        if len(password) >= 12:
            pass_quals['length'] = ''
        for i in password:
            if i.isnumeric():
                pass_quals['num'] = ''
            if i.isupper():
                pass_quals['upper'] = ''
            if i.islower():
                pass_quals['lower'] = ''
            if not i.isalnum():
                pass_quals['special'] = ''
        pass_helpers = []
        for i in pass_quals.keys():
            if pass_quals[i]:
                pass_helpers.append(pass_quals[i])
        email_error = False
        try:
            validate_email(email)
        except EmailNotValidError:
            email_error = True
        username_test = User.query.filter_by(username=username).first()
        email_test = User.query.filter_by(email=email).first()
        username_taken = False
        email_taken = False
        if username_test is not None:
            username_taken = True
        if email_test is not None:
            email_taken = True
        if pass_helpers or email_taken or username_taken or email_error:
            return render_template('register.html', pass_helpers=pass_helpers, email_error=email_error,username_taken=username_taken,email_taken=email_taken)
        else:
            user = User(email=email,username=username,password=password,account_type_code=account_type_code)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('welcome'))
    return render_template('register.html', helpers=[],email_error=False,username_taken=False,email_taken=False)

@app.route('/')
def welcome():
    return render_template('welcome_page.html')

@app.route('/everyday-apps')
def everyday_apps():
    return render_template('everyday_apps.html')

@app.route('/community-service-apps')
def community_service_apps():
    return render_template('community_service_apps.html')

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/glex',methods=['GET','POST'])
def glex():
    if request.method == 'POST':
        result = request.form.get('zipcode')
        nomi = pgeocode.Nominatim('us')
        df = nomi.query_postal_code(result)
        lat_lon = [df['latitude'],df['longitude']]
        key = 'AIzaSyBQrw01btyVL_Y-ioNkQYY8VumySpeBWTo'
        search_radius = 8000
        circle_radius = 1600
        keyword = 'supermarket'
        min_price = 1
        max_price = 3
        gmaps = googlemaps.Client(key)
        m = folium.Map(location=lat_lon,zoom_start=10)
        group = folium.FeatureGroup("Stores")
        list_of_places = gmaps.places(keyword,lat_lon,search_radius, min_price = min_price, max_price = max_price)
        def add_to_group(store):
            folium.Circle(
                location=[store["geometry"]["location"]["lat"],store["geometry"]["location"]["lng"]],
                radius=circle_radius,
                popup=store["name"],
                color=store["icon_background_color"],
                fill=True,
                fill_color=store["icon_background_color"],
            ).add_to(group)

        def next_page(lst):
            for store in list_of_places['results']:
                add_to_group(store)
            while True:
                time.sleep(2)
                try:
                    npt = lst["next_page_token"]
                    lst = gmaps.places(keyword,lat_lon,search_radius,page_token=npt,max_price = max_price,min_price = min_price)
                    for store in list_of_places['results']:
                        add_to_group(store)
                except:
                    break
        inp_zip = True
        next_page(list_of_places)

        group.add_to(m)

        m.get_root().width = "800px"
        m.get_root().height = "600px"
        iframe = m.get_root()._repr_html_()
        return render_template('glex_project.html', iframe=iframe, inp_zip=inp_zip)
    return render_template('glex_project.html',iframe=None,inp_zip=False)

@app.route("/python")
def python():
    return render_template('python_tutorial_main.html')

@app.route('/java')
def java():
    return render_template('java_tutorial.html')

@app.route('/CSS')
def CSS():
    return render_template('css_tutorial.html')

@app.route('/c++')
def cpp():
    return render_template('c++_tutorial.html')


def seating_chart(new_student_name):
    rectangles = "static/images/rectangles.svg"
    num_section = int(request.form["num_groups"])
    desk_in_row = int(request.form["num_columns"])
    desk_in_column = int(request.form["num_rows"])
    width = desk_in_row * 460
    height = desk_in_column * 350 * num_section
    with cairo.SVGSurface(rectangles, width, height) as surface:
        context = cairo.Context(surface)
        context.set_source_rgba(0, 0, 0, 1)
        def find_space_name(name, x, y):
            if " " in name:
                space = name.find(" ")
                context.stroke()
                context.move_to(x, y+35)
                context.show_text(name[0:space])
                context.stroke()
                context.move_to(x, y+65)
                context.show_text(name[space+1:])
            elif len(name) >= 12:
                context.stroke()
                context.move_to(x, y+35)
                context.show_text(name[0:11] + "-")
                context.stroke()
                context.move_to(x, y+65)
                context.show_text(name[11:])
            else:
                context.stroke()
                context.move_to(x, y+35)
                context.show_text(name)

        #first and last name
        def desk_name(x, y, name, placement):
            context.move_to(x,y-15)
            context.set_font_size(25)
            context.select_font_face("Arial")
            find_space_name(name[0], x, y-65)
            find_space_name(name[1], x, y)
            context.move_to(x, y+115)
            context.show_text(placement)

        #rectangle
        def rectangle_desk(x, y, x_dash, y_dash):
            context.set_line_width(10)
            context.set_dash([])
            context.rectangle(x, y, 400, 200) #(x, y, width, height)
            context.set_line_join(cairo.LINE_JOIN_BEVEL)
            context.stroke()
            context.set_dash([10.0])
            context.move_to(x_dash, y_dash) #(where,length of line)
            context.line_to(x_dash, y_dash - 200)
            context.stroke()

        #VARIABLES
        sections = "abcdefghijklmnopqurstuvwxyz"
        #desk_number = len(new_student_name)/2   #TOTAL DESKS
        shuffle_or_no = request.form["shuffle"]
        if shuffle_or_no[0].upper() == "Y":
            random.shuffle(new_student_name)
        placement_num_ltr = [1, sections[0].upper()]
        if num_section == 1:
            placement_num_ltr[1] = " "
        place_name_list = []

        #name_place_file = open("static/name_place.txt", "r+")
        x_desk = 30
        y_desk = 90
        x_dash = 225
        y_dash = 285
        x_name = 50
        y_name = 160

        for section in range(num_section):
            if new_student_name == 0:
                break
            placement_num_ltr[0] = 1
            placement_num_ltr[1] = sections[section].upper()
            if num_section == 1:
                placement_num_ltr[1] = " "
            #random.shuffle(main_gym_list)
            if section == 0:
                context.move_to(30,60)
                context.set_font_size(50)
            else:
                y_name += 100
            context.show_text("Section "+ str(sections[section].upper()))
            for column in range(desk_in_column):
                for desk in range(desk_in_row):
                    desks = rectangle_desk(x_desk, y_desk, x_dash, y_dash)
                    x_desk += 450
                    x_dash += 450

                for name in range(desk_in_row*2):
                    if new_student_name != []:
                        name_pop = new_student_name.pop(0)
                        name_on_desk = desk_name(x_name, y_name, name_pop, str(placement_num_ltr[0]))
                        place_name_list.append([[name_pop[1], name_pop[0]], placement_num_ltr[0], placement_num_ltr[1]])
                        placement_num_ltr[0] += 1
                        x_name += 200
                        if name % 2:
                            x_name += 50
                x_dash = 225
                x_desk = 30
                x_name = 50
                y_desk += 250
                y_dash += 250
                y_name += 250
                #if column == desk_in_column:
                #    break
            y_desk += 100
            y_dash += 100
            y_name += 0
            context.move_to(30, y_name)
            context.set_font_size(50)

        context.stroke()
        #print(place_name_list)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 12)
        count = 1
        for name in place_name_list:
            pdf.cell(200, 10, txt = str(name[0][0]) + ", " + str(name[0][1]) + " " + str(name[1]) + str(name[2]),
                ln = 5, align = 'L')
            count += 1
        pdf.output("static/images/Roster2.pdf")
        place_name_list.sort()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 12)
        count = 1
        for name in place_name_list:
            pdf.cell(200, 10, txt = str(name[0][0]) + ", " + str(name[0][1]) + " " + str(name[1]) + str(name[2]),
                ln = 5, align = 'L')
            count += 1
        pdf.output("static/images/Roster.pdf")
        return render_template("together.html")

@app.route('/seating-chart-type', methods=['GET', 'POST'])
def seating_chart_type():
    if request.method == "GET":
        return render_template("seating_chart_type.html")

    student_names = request.form["studentsType"]
    new_student_name = student_names.split(",")
    for student in range(len(new_student_name)):
        if new_student_name[student].startswith(" "):
            new_student_name[student] = new_student_name[student][1:]
        new_student_name[student] = new_student_name[student].title()
    for student in range(len(new_student_name)):
        new_student_name[student] = new_student_name[student].split(" ")


    seating_chart_return = seating_chart(new_student_name)
    return seating_chart_return


UPLOAD_FOLDER = "static/files"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/seating-chart-upload', methods=['GET', 'POST'])
def seating_chart_upload():
    if request.method == "GET":
        return render_template("seating_chart_upload.html")
    student_names = request.files["studentsUpload"]
    #filename = secure_filename(student_names.filename)
    #basedir = os.path.abspath(os.path.dirname(__file__))
    if student_names.filename != "":
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], student_names.filename)
        student_names.save(file_path)
    file_path_str = str(file_path)
    period_index = file_path_str.find(".")
    if file_path_str[period_index:] == ".csv":
        with open(file_path, 'r') as file:
          csvreader = csv.reader(file)
          new_student_name = []
          for row in csvreader:
                first_name = row[0]
                last_name = row[1]
                new_student_name.append([first_name.title(), last_name.title()])
    elif file_path_str[period_index:] == ".xlsx":
        pass
    seating_chart_return = seating_chart(new_student_name)
    return seating_chart_return

@app.route("/seating_chart_main_page.html")
def seating_chart_main_page():
    return render_template("seating_chart_main_page.html")

@app.route("/seating_chart_webpage.html")
def seating_chart_webpage():
    return render_template("seating_chart_webpage.html")

@app.route("/roster.html")
def roster():
    return render_template("roster.html")

@app.route("/together/")
def together():
    return render_template("together.html")

@app.route('/peer-tutors')
def peer_tutors():
    return render_template('peer_tutors.html', subjects=subjects)

@app.route('/peer_tutors_code', methods=['GET', 'POST'])
def peer_tutors_code():
    userName = request.form.get('name')
    userEmail = request.form.get('email')
    userSubject = request.form.get('subjects')
    pairs = []
    unpaired = []
    tutors = []
    updated = []

    def tutorFinder(userEmail, userSubject):
        with open('TutorsWID.csv', 'r+') as tutorsFile:
            reader = csv.DictReader(tutorsFile)

            #Searches for matching tutors
            for tutor in reader:
                focusClass1 = tutor['Focus Class 1']
                focusClass2 = tutor['Focus Class 2']

                if userSubject.lower().strip() in focusClass1.lower() or userSubject.lower().strip() in focusClass2.lower():
                    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                    availableWeek = []
                    for day in weekdays:
                        if tutor[day] == 'YES':
                            availableWeek.append(day)

                    pairs.append({
                        'Tutor ID': tutor['ID'],
                        'Tutor': tutor['Student Name '],  # keep the space at the end
                        'Tutor Email': tutor['Student E-mail'],
                        'Student Name': userName,
                        'Student Email': userEmail,
                        'Subject': userSubject.strip(),
                        'Weekday Availability': availableWeek,
                        'Availability': tutor['Before School, Lunch, After School, Connectivity'],
                        'Date/Time': datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                    })

                    for row in reader:
                        if row != tutor:
                            updated.append(row)

                    return True
                    break
                else:

                    unpaired.append({
                        'Student Name' : userName,
                        'Student Email': userEmail,
                        'Subject': userSubject,
                        })
                    return False



        tutorReturn = tutorFinder(userEmail, userSubject)

        if tutorReturn:
            # Write pairs to Pairs.csv
            with open('pairs.csv', 'r+') as pairsFile:
                fieldnames_pairs = ['Tutor ID', 'Tutor', 'Tutor Email', 'Student Name', 'Student Email', 'Subject', 'Weekday Availability', 'Availability', 'Date/Time']
                writer = csv.DictWriter(pairsFile, fieldnames = fieldnames_pairs)  # Must use fieldnames
                writer.writeheader()
                for pair in pairs:
                    writer.writerow(pair)

            #Updates TutorsWID.csv without pairs
            with open('TutorsWID.csv', 'w') as tutorsFileW:
                fieldnames = updated[0].keys()
                writer = csv.DictWriter(tutorsFileW, fieldnames = fieldnames)

                writer.writeheader()
                for row in updated:
                    writer.writerow(row)

            return True

        else:
            # Write unpaired students to unpaired.csv
            with open('unpaired.csv', 'r+') as unpairedFile:
                fieldnames_unpaired = ['Student Name', 'Student Email', 'Subject']
                writer = csv.DictWriter(unpairedFile, fieldnames = fieldnames_unpaired)  # Must use fieldnames
                writer.writeheader()
                for student in unpaired:
                    writer.writerow(student)

            return False

    tutorID = pairs[0]
    tutorName = pairs[1]
    tutorEmail = pairs[2]
    studentName = pairs[3]
    studentEmail = pairs[4]
    subject = pairs[5]
    weekdayAvailability = pairs[6]
    availability = pairs[7]
    dateTime = pairs[8]


    return render_template('peer_tutors_found.html', tutorIDs=tutorID)

@app.route('/forum', methods=['GET','POST'])
@login_required
def forum():
    if request.method == 'POST':
        if 'add_comment' in request.form:
            timestamp = datetime.now()
            comment = request.form.get('comment')
            title = request.form.get('title')
            if current_user.account_type == 'Admin':
                c_admin = True
            else:
                c_admin = False
            new_comment = Comment(comment=comment,title=title,c_username=current_user.username,c_email=current_user.email,timestamp=timestamp,c_admin=c_admin)
            db.session.add(new_comment)
            db.session.commit()
            return redirect('/forum')
        elif 'add_reply' in request.form:
            rep_id = int(request.form.get('rep_id'))
            reply = request.form.get('reply')
            timestamp = datetime.now()
            if current_user.account_type == 'Admin':
                r_admin = True
            else:
                r_admin = False
            new_reply = Reply(reply=reply,r_username=current_user.username,r_email=current_user.email,r_comment=rep_id,timestamp=timestamp,r_admin=r_admin)
            db.session.add(new_reply)
            db.session.commit()
            return redirect('/forum')
        elif 'delete' in request.form:
            del_id = request.form.get('del_id')
            del_comment = Comment.query.get(del_id)
            replies = Reply.query.order_by(Reply.id).all()
            for reply in replies:
                if reply.r_comment == del_comment.id:
                    timestamp = reply.timestamp
                    new_timestamp = timestamp.strftime('%a, %b %-d %Y - %-I:%M %p EST')
                    new_r_archive = ReplyArchive(reply=reply.reply,r_username=reply.r_username,r_email=reply.r_email,timestamp=new_timestamp)
                    db.session.add(new_r_archive)
                    db.session.delete(reply)
            timestamp = del_comment.timestamp
            new_timestamp = timestamp.strftime('%a, %b %-d %Y - %-I:%M %p EST')
            new_archive = CommentArchive(comment=del_comment.comment,title=del_comment.title,c_username=del_comment.c_username,c_email=del_comment.c_email,timestamp=new_timestamp)
            db.session.delete(del_comment)
            db.session.add(new_archive)
            db.session.commit()
            return redirect('/forum')
        elif 'reply' in request.form:
            rep_id = int(request.form.get('rep_id'))
            comments = Comment.query.order_by(Comment.id).all()
            now = datetime.now()
            replies = Reply.query.order_by(Reply.id).all()
            return render_template('forum.html',comments=comments,replies=replies,now=now,rep_id=rep_id)
        elif 'del_rep' in request.form:
            del_id = request.form.get('del_id')
            del_reply = Reply.query.get(del_id)
            timestamp = del_reply.timestamp
            new_timestamp = timestamp.strftime('%a, %b %-d %Y - %-I:%M %p EST')
            new_archive = ReplyArchive(reply=del_reply.reply,r_username=del_reply.r_username,r_email=del_reply.r_email,timestamp=new_timestamp)
            db.session.delete(del_reply)
            db.session.add(new_archive)
            db.session.commit()
            return redirect('/forum')
    comments = Comment.query.order_by(Comment.id).all()
    now = datetime.now()
    replies = Reply.query.order_by(Reply.id).all()
    return render_template('forum.html',comments=comments,replies=replies,now=now,rep_id=0)

@app.route('/forum-archive')
@login_required
def forum_archive():
    comments = CommentArchive.query.order_by(CommentArchive.id).all()
    replies = ReplyArchive.query.order_by(ReplyArchive.id).all()
    return render_template('forum_archive.html',comments=comments,replies=replies)

@app.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        if 'del_user' in request.form:
            password = request.form.get('password')
            if current_user.check_password(password):
                logout_user()
                del_id = request.form.get('del_id')
                del_user = User.query.get(del_id)
                db.session.delete(del_user)
                db.session.commit()
                return redirect(url_for('welcome'))
        elif 'change_email' in request.form:
            email = request.form.get('email')
            password = request.form.get('password')
            clash = User.query.filter_by(email=email).first()
            if current_user.check_password(password) and clash == None:
                current_user.set_email(email)
                db.session.commit()
        elif 'change_account' in request.form:
            code = request.form.get('code')
            password = request.form.get('password')
            if current_user.check_password(password):
                current_user.set_type(code)
                db.session.commit()

    return render_template('settings.html')
if __name__ == "__main__":
  app.run()
