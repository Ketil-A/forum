from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
def adminmainpage():
    tags = {}       #all unique tags
    tagcounts = {} # number of posts by tag
    tagcolors = {} # designated color of each tag (default to 'Not set')
    categories = {} # all categories (not yet implemented)
    return render_template('blog/admin.html', tags = {}, tag_colors = {}, categories = {})