from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.reply import Reply
from models.topic import Topic
from models.topic import User


main = Blueprint('user', __name__)


@main.route("/<username>")
def detail(username):
    # u = current_user()
    u = User.find_by(username=username)
    ts = Topic.find_all(user_id=u.id)
    tss = []
    rs = Reply.find_all(user_id=u.id)
    for r in rs:
        t = Topic.find_by(id=r.topic_id)
        if t is not None and t.user_id != u.id:
            tss.append(t)
    return render_template("user/detail.html", user=u, ts=ts, tss=tss)


@main.route('/update', methods=['POST'])
def update():
    u = current_user()
    form = request.form
    u.update(form)
    return redirect(url_for('index.setting'))
