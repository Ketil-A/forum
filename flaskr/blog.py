from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

#global flag for printing some debugging data
# - Lars Erik 'KvaGram' Grambo
__TEST__ = True

@bp.route('/ascii')
def ascii():
    return render_template('blog/ascii.html')

@bp.route('/')
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts, tags = "PLACEHOLDER LIST OF TAGS")


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == 'POST':
        title:str = request.form['title']
        body:str = request.form['body']
        tags:str = request.form['tags']
        #splits tags by space, and uppercase them
        taglist:list = tags.upper().split(" ")
        #filter out duplicate tags
        taglist:list = list(set(taglist))
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            res = db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            postID = res.lastrowid
            for t in taglist:
                res = db.execute(
                    'INSERT INTO tags (post_id, tag_text)'
                    ' VALUES (?, ?)',
                    (postID, t)
                )
                if __TEST__:
                    print("Tagentry {tagID} - Added tag {tag} for postid {postID}"
                        .format(tagID = res.lastrowid, tag = t, postID = postID))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post if the current user is the author."""
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
                'UPDATE post SET title = ?, body = ? WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post, tags = "PLACEHOLDER LIST OF TAGS")


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    #TODO: delete tag entries. like this
    # psudocode: delete from tags where post_id = ? (id)
    db.commit()
    return redirect(url_for('blog.index'))

##By ketil
@bp.route('/<int:id>/', methods=('GET',))
@login_required
def view_post(id):
    post = get_post(id, False)
    db = get_db()
    comments = db.execute(
        'SELECT c.id, body, created, author_id, username'
        ' FROM comment c JOIN user u ON c.author_id = u.id'
        ' WHERE post_id = ?'
        ' ORDER BY created DESC',
        (id,)
    ).fetchall()
    tags = db.execute(
        'SELECT tag_text'
        ' FROM tags'
        ' WHERE post_id = ?'
        ' ORDER BY created DESC',
        (id,)
    ).fetchall()
    return render_template('blog/post.html', post=post, tags = tags, comments=comments)

##By ketil
@bp.route('/ajax/comment/<int:postid>/create', methods=['POST'])
@login_required
def create_comment(postid):
    if request.method == 'POST':
        body = request.form['body']
        db = get_db()
        db.execute(
            'INSERT INTO comment (post_id, body, author_id)'
            ' VALUES (?, ?, ?)',
            (postid, body, g.user['id'])
        )
        db.commit()
        return "Comment Created"

##By ketil
def get_comment(id, check_author=True):
    comment = get_db().execute(
        'SELECT c.id, post_id, body, created, author_id, username'
        ' FROM comment c JOIN user u ON c.author_id = u.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if comment is None:
        abort(404, "Comment id {0} doesn't exist.".format(id))

    if check_author and comment['author_id'] != g.user['id']:
        abort(403)

    return comment

##By ketil
@bp.route('/ajax/comment/<int:id>/update', methods=['POST'])
@login_required
def update_comment(id):
    get_comment(id)
    if request.method == 'POST':
        body = request.form['body']
        db = get_db()
        db.execute(
            'UPDATE comment SET body = ?'
            ' WHERE id = ?',
            (body, id)
        )
        db.commit()
        return "Updated Comment"

##By ketil
@bp.route('/ajax/comment/<int:id>/delete', methods=['POST'])
@login_required
def delete_comment(id):
    get_comment(id)
    db = get_db()
    db.execute('DELETE FROM comment WHERE id = ?', (id,))
    db.commit()
    return "Deleted Comment"