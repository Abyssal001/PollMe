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
    p = query_db('select * from polls where id = ?', [id], one=True)
    if p is None:
        abort(404)
    v = query_db('select * from votes where poll_id = ? and ip = ?', [id, request.remote_addr])
    options = query_db('select * from options where poll_id = ?', [id])
    if v:
        total = 0
        for i in options:
            total += i['voters']
        x = time.localtime(p['create_at'])
        create_at = time.strftime('%Y-%m-%d %H:%M:%S', x)
        return render_template('result.html', poll=p, options=options, total=total, create_at=create_at)
    else:
        return render_template('poll.html', poll=p, options=options)


@app.route('/polls', methods=['POST'])
def create():
    question = request.form.get('question', '')
    i = 1
    options = {}
    while request.form.get('option-' + str(i)) is not None:
        option = request.form.get('option-' + str(i))
        if option != "":
            options['option-' + str(i)] = option
        i += 1
    cur = g.db.cursor()
    cur.execute('insert into polls (question, is_multi, create_at) VALUES (?, ?, ?)',
                [question, False, int(time.time())])
    g.db.commit()
    row_id = cur.lastrowid
    i = 0
    for j in options:
        i += 1
        g.db.execute('insert into options (poll_id, option, content) VALUES (?, ?, ?)', [row_id, i, options[j]])
    g.db.commit()
    return redirect(url_for('poll', id=row_id))


@app.route('/polls/<id>', methods=['POST'])
def vote(id):
    ip = request.remote_addr
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    option = request.form.get('option', '1')
    v = query_db('select * from votes where poll_id = ? and ip = ?', [id, request.remote_addr])
    if v:
        return redirect(url_for("poll", id=id))
    g.db.execute('insert into votes (poll_id, option_id, ip) VALUES (?, ?, ?)', [id, option, ip])
    v = query_db('select voters from options where poll_id = ? and option = ?', [id, option], one=True)
    g.db.execute('update options set voters = ? where poll_id = ? and option = ?', [v['voters'] + 1, id, option])
    g.db.commit()
    return redirect(url_for("poll", id=id))


@app.route('/ip', methods=['GET'])
def ip():
    ip = ""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return str(ip)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
