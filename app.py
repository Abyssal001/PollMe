# -*- coding: utf-8 -*-

import os
import sqlite3
import time
from flask import *

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db/main.db'),
    DEBUG=True,
    SECRET_KEY=os.urandom(24)
))


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/<id>', methods=['GET'])
def poll(id):
    p = query_db('select * from polls where id = ?', [id])
    print p
    return render_template('poll.html', poll=p)


@app.route('/', methods=['POST'])
def create():
    g.db.execute('insert into polls (question, is_multi, create_at) VALUES (?, ?, ?)', [question, is_multi, int(time.time())])
    g.db.commit()
    return redirect(url_for('poll', ))


@app.route('/<id>', methods=['POST'])
def vote():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
