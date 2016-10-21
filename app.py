# -*- coding: utf-8 -*-

import os
import sqlite3
import time
from flask import *

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db/main.db'),
    HOST='0.0.0.0',
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/polls/<id>', methods=['GET'])
def poll(id):
    p = query_db('select * from polls where id = ?', [id])
    print p
    if p is []:
        return redirect(url_for('page_not_found'))
    return render_template('result.html', title="123")


@app.route('/polls', methods=['POST'])
def create():
    question = request.form.get('question', '')
    i = 0
    options = {}
    while request.form.get('option-' + str(i)) is not None:
        option = request.form.get('option-' + str(i))
        if (option != ""):
            options['option-' + str(i)] = option
        i += 1
    g.db.execute('insert into polls (question, is_multi, create_at) VALUES (?, ?, ?)', [question, False, int(time.time())])
    row_id = g.db.cursor().lastrowid
    i = 0
    for j in options:
        i += 1
        g.db.execute('insert into options (poll_id, option, content)', [row_id, i, options[j]])
    g.db.commit()
    print row_id
    return redirect(url_for('poll', id=1))


@app.route('/polls/<id>', methods=['POST'])
def vote():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
