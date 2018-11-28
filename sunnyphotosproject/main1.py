from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug import secure_filename
from datetime import datetime
import os

app = Flask(__name__)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SECRET_KEY'] = 'Ruu9iK5O8fg9hKfRgCjY45j78KEHjh6gKWR'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    albums = db.relationship('Album', backref='author', lazy='dynamic')

    def __repr__(self):
        return "Users(" + self.name + ", " + self.email + ")"

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    img = db.Column(db.String(100), unique=True, nullable=False)
    img_name = db.Column(db.String(50), unique=False, nullable=False)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(40), unique=False, nullable=False)
    message = db.Column(db.String(500), unique=False, nullable=False)

    def __repr__(self):
        return "Contact(" + self.name + ", " + self.email + ", " + self.message + ")"

# Forms
class LoginForm(FlaskForm):
    email  = StringField('email', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=100)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=5, max=50)])
    email = StringField('email', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=100)])

@app.route("/")
def home():
    if current_user.is_authenticated:
        action = "logout"
        value = "Logout"
    else:
        action = "login"
        value = "Login"
        
    return render_template("index.html", action=action, value=value)

@app.route("/upload")
@login_required
def upload():
    return render_template("upload.html")

# upload configuration
app.config['UPLOAD_FOLDER'] = "static/upload_img"
@app.route("/uploader", methods=["POST", "GET"])
def upload_file():
    if request.method == "POST":
        f = request.files['file']
        img_name = request.form.get("img_name")
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        album = Album(img=str(f.filename), img_name=str(img_name), time=datetime.now(), user_id=User.query.get(current_user.get_id()).id)
        db.create_all()
        db.session.add(album)
        db.session.commit()

        return 'Image uploaded successfully!'

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect("/upload")

    form = LoginForm()

    email = form.email.data
    password = form.password.data
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                #return redirect("/upload")
                login_user(user, remember=form.remember.data)
                return redirect("/upload")
        else:
            flash("Invalid Email or Password!")

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")
    
@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = RegisterForm()
    full_name = form.username.data
    email = form.email.data
    password = form.password.data

    if form.validate_on_submit():
        user = User(name=full_name, email=email, password=password)
        db.create_all()
        db.session.add(user)
        db.session.commit()

        return "User added"
    
    return render_template("signup.html", form=form)

@app.route("/do_signup")
def do_signup():
    form = RegisterForm()
    

    user = User(name=full_name, email=email, password=password)

    db.create_all()
    db.session.add(user)
    db.session.commit()

    return render_template("index.html")

@app.route("/signout")
def signout():
    session['logged_in'] = False

@app.route("/contact")
def contact_us():
    return render_template("contact.html")

@app.route("/do_contact", methods=["POST"])
def do_contact():
    user_data = request.form
    name = user_data['name']
    email = user_data['email']
    message = user_data['message']

    contact = Contact(name=name, email=email, message=message)

    db.create_all()
    db.session.add(contact)
    db.session.commit()

    return redirect("/all_contacts")

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/photos")
def photos():
    img_list = []
    time_list = []
    #img_name = []
    try:
        album = Album.query.filter_by(user_id=current_user.get_id()).all()
        for a in album:
            img_list.append(str(a.img))
            #img_name.append(a.img_name)
            time_list.append(a.time)
    except:
        return "Sorry there are no photos in the Album!"

    return render_template("photos.html", img_list__time_list=zip(img_list, time_list))

# for showing images


# Image Search
@app.route("/search", methods=["GET", "POST"])
def search_img():
    search_q = request.args.get('search_q', '')
    return render_template("search.html", query=search_q)

@app.route("/features")
def features():
    return render_template("features.html")

#for contact test only
@app.route("/all_contacts")
def all_contacts():
    contacts = Contact.query.all()
    return render_template("all_contacts.html", contacts=contacts)

#for signup test only
@app.route("/users")
def users():
    users = User.query.all()
    return render_template("users.html", users=users)

if __name__ == '__main__':
    app.run(debug = True)
