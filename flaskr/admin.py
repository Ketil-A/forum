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
    flash(f"Wery well sir, killing the cat {cat}")
    return render_template('blog/admin.html', **GetAdminpageData())
@bp.route('/killtag/<tag>')
def killtag(tag):
    flash(f"Wery well sir, eliminating the tag {tag}")
    return render_template('blog/admin.html', **GetAdminpageData())
@bp.route('/colortag/<tag>')
def colortag(tag):
    flash(f"Crayons drawn and ready! How shall we color {tag}?")
    return render_template('blog/admin.html', **GetAdminpageData())
@bp.route('/makecat', methods=("POST",))
def makecat():
    catname:str = request.form['catname']
    flash(f"Wery well sir, making the cat {catname}")
    return render_template('blog/admin.html', **GetAdminpageData())

@bp.route('/')
def adminmainpage():
    return render_template('blog/admin.html', **GetAdminpageData())

def GetAdminpageData():
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
    return {"categories" : categories, "tags" : tags, "tagcounts" : tagcounts, "tagcolors" : tagcolors}