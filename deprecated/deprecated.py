def unique_check(username, email):
    connection = sqlite3.connect(currentdirectory + "/classes.db")
    cursor = connection.cursor()
    username_check = cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,)).fetchall()
    email_check = cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,)).fetchall()

    if username_check or email_check:
        return False
    return True

def register_student(fn, ln, email, subject):
    connection = sqlite3.connect(currentdirectory + "/tutoring.db")
    cursor = connection.cursor()
    
    if not unique_check(username, email):
        return False
    
    salt = bcrypt.gensalt(rounds=16)
    str_password = password
    password = bytes(password, 'utf-8')
    password_hash = bcrypt.hashpw(password, salt)
    

    cursor.execute("INSERT INTO students (fn, ln, email, subject) VALUES (?, ?, ?, ?)", (fn, ln, email, subject))
    connection.commit()
    
    login_func(email)
    return True

def login_func(username, password):
    connection = sqlite3.connect(currentdirectory + "/classes.db")
    cursor = connection.cursor()
    username_check = cursor.execute("SELECT hash FROM users WHERE username = ?", (username,)).fetchall()
    if not username_check:
        return False
     
    password_hash = username_check[0][0]
    password = bytes(password, 'utf-8')
    password_check = bcrypt.checkpw(password, password_hash)
    if not password_check:
        return False

    user_id, email, account_type = cursor.execute("SELECT user_id, email, account_type FROM users WHERE username = ?", (username,)).fetchall()[0]

    new_user = User(str(user_id), username, email, account_type)
    login_user(new_user)
    return True

@login_manager.user_loader
def load_user(user_id):
    if user_id == "None":
        return None
    else:
        print(type(user_id))
        return User.get_user(user_id)

class User(UserMixin):
    users = {}

    @classmethod
    def get_user(user, user_id):
        print(user.users[user_id])
        return user.users[user_id]
    
    @classmethod
    def add_user(user, new_user, user_id):
        user.users[user_id] = new_user

    def __init__(self, user_id, ln, fn, email, account_type, t_id, cur_capacity, full_capacity):
        if account_type == "Student":
            self.user_id = email
            self.t_id = t_id
            self.ln = ln
            self.fn = fn
            self.account_type = account_type
        elif account_type == "Tutor":
            self.user_id = email
            self.ln = ln
            self.fn = fn
            self.cur_capacity = cur_capacity
            self.full_capacity = full_capacity
            self.account_type = account_type

        self.subjects = []
        User.add_user(self, user_id)

    def get_id(self):
        return self.user_id
    
    def add_subject(self, subject):
        self.subjects.append(subject)


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
'''

'''
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