from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/killcat/<cat>')
def killcat(cat):
    return(f"Wery well sir, killing the cat {cat}")
@bp.route('/killtag/<tag>')
def killtag(tag):
    return(f"Wery well sir, eliminating the tag {tag}")
@bp.route('/colortag/<tag>')
def colortag(tag):
    return(f"Crayons drawn and ready! How shall we color {tag}?")


@bp.route('/')
def adminmainpage():
    tags = {}       #all unique tags
    tagcounts = {} # number of posts by tag
    tagcolors = {} # designated color of each tag (default to 'Not set')
    categories = {} # all categories (not yet implemented)
    
    db = get_db()

    #TODO: implement categories
    categories = [{"category_name" : "PLACEHOLDER 1"}, {"category_name" : "PLACEHOLDER 2"},{"category_name" : "PLACEHOLDER 3"},]

    tags = db.execute(
        ' SELECT DISTINCT tag_text'
        ' FROM tags'
    ).fetchall()
    for tag in tags:
        tag_text = tag['tag_text']
        tagcounts[tag_text] = len(get_db().execute(
                'SELECT * FROM tags'
                ' WHERE tag_text = ?',
                (tag_text,)
            ).fetchall())
        tagcolors[tag_text] = "NOT SET" #TODO: implement tag colors

    return render_template('blog/admin.html', categories = categories, tags = tags, tagcounts = tagcounts, tagcolors = tagcolors)