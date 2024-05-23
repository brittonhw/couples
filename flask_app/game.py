from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flask_app.auth import login_required
from flask_app.db import get_db

bp = Blueprint('game', __name__)



current_game =[ 'MAN', 'CAT', 'PLAY', 'SILLY', 'EDUCATE', 'MINUTE', 'GLOVE', 'CONTROL', 'SHORE', 'RABBIT']

current_solves = []

answer_key = [{'SILLY', 'RABBIT'}, {'CAT', 'GLOVE'}, {'EDUCATE', 'SHORE'}, {'MAN', 'CONTROL'}, {'PLAY', 'MINUTE'}]




@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('game/index.html', posts=posts)


@bp.route('/submit', methods=['POST'])
def submit_form():
    global current_game
    global current_solves

    selected_options = request.form.getlist('options')  # Get the list of selected options

    if set(selected_options) in answer_key:
        current_solves.append(selected_options)
        current_game = [word for word in current_game if word not in selected_options]

    print(current_game)
    
    return render_template('game/create.html', current_game = current_game, current_solves = current_solves)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('game.index'))

    return render_template('game/create.html', current_game = current_game, current_solves = current_solves)

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('game.index'))

    return render_template('game/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('game.index'))