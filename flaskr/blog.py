from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import html

bp = Blueprint('blog', __name__)

#global flag for printing some debugging data
# - Lars Erik 'KvaGram' Grambo
__TEST__ = True
__MAX_TAGS__ = 10 #posts with too many tags will be rejected.
__MIN_TAGS__ = 0 #posts with too few tags will be rejected.
__MAX_TAGLENGTH__ = 20 #a tag with too many characters in length will be rejected
__MIN_TAGLENGTH__ = 2 #a tag with too few characters in length will be rejected

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
    tags = {}
    for p in posts:
        p_id = p['id']
        tags[p_id] = getTagtext(postID = p_id, number = True, links = True, tagCase = TagCase.CAPITAL)
    return render_template('blog/index.html', posts=posts, tags = tags)


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
def get_tags(postID:int):
    """Gets list of tags associated with a post, by postID.

    :param postID: id of the post tag-list to get
    :return: a list of tags for this post
    """
    post = get_db().execute(
        'SELECT tag_text'
        ' FROM tags'
        ' WHERE post_id = ?'
        ' ORDER BY tag_text DESC',
        (postID,)
    ).fetchall()
    return post


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == 'POST':
        title:str = request.form['title']
        body:str = request.form['body']
        tags:str = request.form['tags']
        #split uppercase and split tags into a set.
        #this ensures same case and no duplicates
        taglist:set = set(tags.upper().split(" "))
        taglist.remove("") #remove empty string tag
        error = None

        tagErr = checkTags(tags)
        if tagErr:
            error = tagErr
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

# Displays all posts with given tag
@bp.route('/<string:tag>/bytag', methods=('GET', 'POST'))
def bytag(tag):
    db = get_db()
    posts = []
    posttags = {}
    taghits = db.execute(
        'SELECT post_id'
        ' FROM tags'
        ' WHERE tag_text = ?'
        ' ORDER BY post_id DESC',
        (tag,)
    ).fetchall()
    for h in taghits:
        postID = h['post_id']
        posts.append(get_post(postID, False))
        posttags[postID] = getTagtext(postID = postID, number = True, links = True, tagCase = TagCase.CAPITAL)
    return render_template('blog/index.html', posts=posts, tags = posttags)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)
    tags = get_tags(id)
    tags_str = ""
    for t in tags:
        tags_str += t['tag_text'] + " "

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        newtags = request.form['tags']

        newtaglist:set = set(newtags.upper().split(" "))
        newtaglist.remove("") #remove empty string tag
        error = None

        tagErr = checkTags(newtaglist)
        if tagErr:
            error = tagErr

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
            update_tags(id, tags, newtags)
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post, tags = tags_str)
    
def update_tags(postID:int, oldtags:list, newtags:str):
    oldtaglist = set()
    for t in oldtags:
        oldtaglist.add(t['tag_text'])
    newtaglist = set(newtags.upper().split(" "))

    tags_to_add = newtaglist - oldtaglist
    tags_to_del = oldtaglist - newtaglist

    db = get_db()
    for t in tags_to_add:
        res = db.execute(
            'INSERT INTO tags (post_id, tag_text)'
            ' VALUES (?, ?)',
            (postID, t)
        )
        if __TEST__:
            print("Tagentry {tagID} - Added tag {tag} for postid {postID}"
                .format(tagID = res.lastrowid, tag = t, postID = postID))
    for t in tags_to_del:
        db.execute('DELETE FROM tags WHERE post_id = ? and tag_text = ?', (postID,t))
        if __TEST__:
            print("Removed tag {tag} from postid {postID}"
                .format(tag = t, postID = postID))
    db.commit()

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
    db.execute('DELETE FROM tags WHERE post_id = ?',(id,))
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
    tags = getTagtext(postID = id, number = True, links = True, tagCase = TagCase.CAPITAL)
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

def getTagtext(**kwargs):
    """
    postID or tagResults required.
    If postID is given, gets tagResults from get_tags()
    :param postID: id of post to get comment string
    :param tagResults : tags to convert to string.
    :param tagCase : The displayed typecase of the tags
    :param number: add number of post with tag
    :param colorize: add color-data to tags
    :param links : add links for bytag page
    :param sort: sorting-mode, see TagSort enum
    :return: a string containing the tags.
    """
    postID      = kwargs.get("postID", None)
    tagResults  = kwargs.get("tagResults", None)
    tagCase     = kwargs.get("tagCase", TagCase.UPPER)
    addNums     = kwargs.get("number", False)
    addColors   = kwargs.get("colorize", False)
    addLinks    = kwargs.get("links", False)
    sortmode    = kwargs.get("sort", TagSort.NONE)

    if not tagResults:
        tagResults = get_tags(postID)
    if not tagResults or len(tagResults) < 1:
        return ""

    tagtextlist = []
    for t in tagResults:
        tt = t['tag_text']
        text = tt
        if tagCase == TagCase.LOWER:
            text = text.lower()
        elif tagCase == TagCase.CAPITAL:
            text = text.capitalize()
        if addNums:
            length = len(get_db().execute(
                'SELECT post_id'
                ' FROM tags'
                ' WHERE tag_text = ?',
                (tt,)
            ).fetchall()) #NOTE: There must be a better way to do this.
            lentext = shortenLongInt(length)
            text = f"{text} ({lentext})"
        if addColors:
            pass #TODO add applicable colors to tags (may require some lookup table or database)
        if addLinks:
            url = url_for('blog.bytag', tag = tt)
            text = "<a href ='" + url + "'>" + html.escape(text) + "</a>"
        else: 
            text = html.escape(text)
        tagtextlist.append(text)
    if sortmode == TagSort.ALPHABETIC:
        pass #TODO: add sorting
    return " ".join(tagtextlist)

def shortenLongInt(num:int):
    suff = ["", "K","M","B","T"]
    mag = 0
    while abs(num) >= 1000:
        mag += 1
        num /= 1000.0
    if mag > 4:
        return "A-true-fuckton"
    num = int(num)
    return f"{num}{suff[mag]}"


def checkTags(tags):
    """
    Checktags checks if there are any issues with one of the tags.
    This could be a bad length or some html exploit.
    Returns: a string explaining the problem or False
    """
    #TODO: write some technical checks for tags
    if type(tags) in (list,tuple,set):
        taglist = list(tags)
    elif type(tags) in (str,):
        taglist = tags.upper().split(" ")
    if len(taglist) < __MIN_TAGS__:
        return f"Woah! We know almost nothing about this post. A post needs to have {__MIN_TAGS__} tags at least!"
    elif len(taglist) > __MAX_TAGS__:
        return f"Woah! Hold your horses there. Don't you think {len(taglist)} tags are a bit extreme? Try to cut it down to just {__MAX_TAGS__} tags."
    for t in taglist:
        if len(t) < __MIN_TAGLENGTH__:
            return f"Woah! Is '{t}' even a word? It seems a bit short. Try lengthen it to at least {__MIN_TAGLENGTH__} characters"
        elif len(t) > __MAX_TAGLENGTH__:
            return f"Excuse me! This field is not meant to write novels in. Try shortening that long tag there to just {__MAX_TAGLENGTH__} characters"
        elif not t.isalnum():
            return "Tags can only have alphanumeric characters"
        #let's forget about Little Boddy Tables for now...
        #Let's worry about him later ;-- drop table Code
        if False:
            return f"The tag '{t}' was rejected for some reason!"
    return False #No problems found

#enum for TagSort
class TagSort:
    NONE = 0 # keep tags as is from database
    ALPHABETIC = 1 # sort tags alphabetically - (current sql query in get_tags?)
class TagCase:
    UPPER = 0
    LOWER = 1
    CAPITAL = 2