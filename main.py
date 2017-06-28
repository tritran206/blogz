from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog')
def show_blogs():
    blogs = Blog.query.all()
    return render_template('blogs.html', title="Your Blogs", blogs = blogs)


def single_blog():
    blog_id = int(request.args.get('id'))
    blogs = Blog.query.get(blog_id)
    return render_template('blogs.html', title="Current Blog", blogs = blogs)

@app.route('/newpost')
def index():
    return render_template('newpost.html', title="Add Posts")

@app.route('/addpost', methods=['POST'])
def add():

    title_error = ''
    body_error = ''

    blog_title = request.form['blog']
    blog_body = request.form['blog_body']

    if blog_title == "":
        title_error = "Please enter a title for you blog"

    if blog_body == "":
        body_error = "Please enter content for your blog"

    if body_error or title_error != '':
        return render_template('newpost.html', title="Add Posts", title_error=title_error, body_error=body_error)

    new_blog = Blog(blog_title, blog_body)
    db.session.add(new_blog)
    db.session.commit()

    return redirect('/blog')


if __name__ == '__main__':
    app.run()
