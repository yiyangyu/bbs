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


main = Blueprint('reply', __name__)


@main.route("/add", methods=["POST"])
def add():
    u = current_user()
    if u is None:
        return redirect(url_for('index.index'))
    form = request.form
    m = Reply.new(form, user_id=u.id)
    topic_id = m.topic_id
    topic = Topic.find_by(id=topic_id)
    topic.last_reply_id = u.id
    topic.set_time()
    return redirect(url_for('topic.detail', id=m.topic_id))

