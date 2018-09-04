import os

from quart import Quart, websocket
from quart import render_template, redirect, abort, flash, g, request, session, url_for
from sqlite3 import dbapi2 as sqlite3


app = Quart(__name__)
app.config.update({
    'DATABASE': os.path.join(app.root_path, 'blog.db'),
    'DEBUG': True,
    'SECRET_KEY': 'development key',
    'USERNAME': 'admin',
    'PASSWORD': 'admin',
})

@app.cli.command()
def init_db():
    """Create an empty database."""
    db = connect_db()
    with open(os.path.join(os.path.dirname(__file__), 'schemal.sql'), mode='r') as file_:
        db.cursor().executescript(file_.read())
    db.commit()


# class User(UserMixin):
#     def __init__(self, user_id):
#         self.id = user_id
#
#     def get_name(self):
#         return "Greg Hayes"




data={
     "navlinks": {
        "Home": "index",
        "Random Thoughts": "posts",
        # "Side Projects": "side-projects",
        # "About": "about",
        },
    "images": [
        "images/IMG1.png"
                  ],
}


@app.route('/')
async def index():
    return await render_template('index.html', data=data)

@app.websocket('/ws')
async def ws():
    while True:
        await websocket.send('index')


@app.route('/random-thoughts', methods=['GET'])
async def posts():
    db = get_db()
    cur = db.execute("SELECT title, text FROM post ORDER BY id DESC")
    posts = cur.fetchall()
    return await render_template('posts.html', posts=posts, data=data)


@app.route('/random-thoughts', methods=['POST'])
async def create():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    form = await request.form
    db.execute("INSERT INTO post (title, text) VALUES (?, ?)",
               [form['title'], form['text']],
               )
    db.commit()
    await flash('New entry was sucessfully posted')
    return redirect(url_for('posts'))


@app.route("/random-thoughts/login/", methods=['GET', 'POST'])
async def login():
    error = None
    if request.method == 'POST':
        form = await request.form
        if form['username'] != app.config['USERNAME']:
            error = 'Invalid username!'
        elif form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            await flash('You were logged in')
            return redirect(url_for('blog_editor'))
    return await render_template('login.html', error=error, data=data)


@app.route("/random-thoughts/editor", methods=["GET", "POST"])
async def blog_editor():
    return await render_template('blog_editor.html', data=data)

@app.route("/logout")
async def logout():
    session.pop('logged_in', None)
    await flash('You were logged out...')
    return redirect(url_for('posts'))


def connect_db():
    engine = sqlite3.connect(app.config['DATABASE'])
    engine.row_factory = sqlite3.Row
    return engine

@app.cli.command()
def init_db():
    """Create an empty dtabase"""
    _init_db()

def _init_db():
    # This exists solely for use in test code
    db = connect_db()
    # with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), mode='r') as file_:
    #     db.cursor().executescript(file_.read())
    db.cursor().execute('''
                           CREATE TABLE post (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           title TEXT NOT NULL,
                           'text' TEXT NOT NULL)'''
                        )
    # db.commit()


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

app.run()
