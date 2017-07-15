from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['signup', 'home', 'allpost', 'login', '/']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error = False

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '':
            flash('Please enter a username')
            error = True
            username = ''

        elif len(username) <=3:
            flash('Your username is not long enough')
            error = True
            username = ''

        elif ' ' in username:
            flash('Your username can not contain any spaces')
            error = True
            username = ''

        elif len(username) > 20:
            flash('Your username is too long')
            error = True
            username = ''

        if password == '':
            flash('Please enter a password')
            error = True
            password = ''
            verify = ''

        elif len(password) <=3:
            flash('Your password is not long enough')
            error = True
            password = ''
            verify = ''

        elif ' ' in password:
            flash('Your password can not contain any spaces')
            error = True
            password = ''
            verify = ''

        elif len(password) > 20:
            flash('Your password is too long')
            error = True
            password = ''
            verify = ''

        elif password != verify:
            flash('Your passwords did not match')
            error = True
            password = ''
            verify = ''

        # if email:
        #     if "@" not in email:
        #         flash('Your email is invalid')
        #         error = True
        #     elif "." not in email:
        #         flash('Your email is invalid')
        #         error = True
        #     elif " " in email:
        #         flash('Your email is invalid')
        #         error = True

        if not error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('This username has already been registered')
                return render_template('signup.html')
        else:
            return render_template('signup.html')

    else:
        return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Welcome back, ' + username)
            return redirect('/newpost')
        else:
            flash('Your username or password was incorrect')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
    return redirect('/blog')

@app.route('/')
def display_users():
    users = User.query.all()
    return render_template('index.html', title="Blog Users", users=users)

@app.route('/blog')
def home():
    if 'id' in request.args:
        return single_blog()
    elif 'user' in request.args:
        return users_blog()
    else:
        return show_blogs()


def show_blogs():
    blogs = Blog.query.all()
    users = User.query.all()
    if 'username' in session:
        return render_template('blogs.html', title="Your Blogs", blogs=blogs, users=users, username=session['username'])

    return render_template('blogs.html', title="Your Blogs", blogs = blogs)

def users_blog():
    users_id = int(request.args.get('user'))
    user = User.query.get(users_id)
    blogs = Blog.query.all()
    if 'username' in session:
        return render_template('individualuser.html', title=user.username, blogs=blogs, id=users_id)


def single_blog():
    blog_id = int(request.args.get('id'))
    blog = Blog.query.get(blog_id)
    if 'username' in session:
        return render_template('singleblog.html', title="Current Blog", blog=blog, username=session['username'])

    return render_template('singleblog.html', title="Current Blog", blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':

        error = False

        blog_title = request.form['blog']
        blog_body = request.form['blog_body']
        owner = User.query.filter_by(username=session['username']).first()

        if blog_title == "":
            flash("Please enter a title for you blog")
            error = True

        elif blog_body == "":
            flash("Please enter content for your blog")
            error = True

        if error == True:
            return render_template('newpost.html', title="Add Posts")

        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog')

    return render_template('newpost.html', title="New Posts", username=session['username'])


if __name__ == '__main__':
    app.run()
