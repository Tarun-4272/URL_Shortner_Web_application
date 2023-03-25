from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug import urls
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(1000), nullable=False)
    short_url = db.Column(db.String(20), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"URL('{self.long_url}', '{self.short_url}')"


import random
import string

def generate_short_url():
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(5))
    timestamp = int(datetime.timestamp(datetime.utcnow()))
    short_url = f"{random_string}-{timestamp}"
    return short_url



'''@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        custom_url = request.form['custom_url']
        if custom_url == "":
            short_url = generate_short_url()
        else:
            short_url = custom_url
        new_url = URL(long_url=long_url, short_url=short_url, user_id=current_user.id)
        db.session.add(new_url)
        db.session.commit()
        return redirect(url_for('display_short_url', short_url=short_url))
    return render_template('index.html')'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        custom_url = request.form.get('custom_url', '')
        short_url = generate_short_url(custom_url)
        urls[short_url] = original_url
        return render_template('index.html', short_url=short_url)
    return render_template('index.html')

def generate_short_url(custom_url=''):
    if custom_url:
        if custom_url in urls:
            return None
        else:
            return custom_url
    else:
        while True:
            short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if short_url not in urls:
                return short_url


@app.route('/<short_url>')
def redirect_to_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url.long_url)

@app.route('/short-url/<short_url>')
@login_required
def display_short_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    return render_template('short_url.html', url=url)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request

if __name__ == '__main__':
    app.run(debug=True)