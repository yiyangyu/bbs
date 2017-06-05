from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort,
)

from routes import *

from models.topic import Topic
from models.board import Board


main = Blueprint('topic', __name__)


import uuid
csrf_tokens = dict()


@main.route("/")
def index(num=100):
    # board_id = 2
    # 实现了分页的功能，前端页面暂时没有处理
    # print(123)
    start = int(request.args.get('start', 0))
    ms1 = []
    ms2 = []
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        # ms = Topic.all()
        ms1 = Topic.top()
        ms2 = Topic.cache_all()

    else:
        ms = Topic.find_all(board_id=board_id)
        for m in ms:
            if m.istop==True:
                ms1.append(m)
            else:
                ms2.append(m)
    token = str(uuid.uuid4())
    u = current_user()
    # print(u.role)
    # print(u.username)
    if u is not None:
        csrf_tokens[token] = u.id
    bs = Board.all()
    num -= len(ms1)
    start -= num
    if start < 0:
        start = 0
    if u is None:
        return render_template("topic/index1.html", ms1=ms1, ms2=ms2, token=token, bs=bs, start=start, num=num)
    return render_template("topic/index.html", ms1=ms1, ms2=ms2, token=token, bs=bs, start=start, num=num, user=u)


@main.route('/<int:id>')
def detail(id):
    from models.user import User
    m = Topic.get(id)
    # 传递 topic 的所有 reply 到 页面中
    user_id = m.user_id
    username = User.get(user_id).username
    u = User.get(user_id)
    return render_template("topic/detail.html", topic=m, username=username, user=u)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    m = Topic.new(form, user_id=u.id)
    return redirect(url_for('.detail', id=m.id))


@main.route("/delete")
def delete():
    id = int(request.args.get('id'))
    topic = Topic.get(id)
    token = request.args.get('token')
    u = current_user()
    # 判断 token 是否是我们给的
    if u.role == 1:
        if token in csrf_tokens and csrf_tokens[token] == u.id:
            csrf_tokens.pop(token)
            if u is not None:
                # print('删除 topic 用户是', u, id)
                Topic.delete(id)
                # topic.delete()
                return redirect(url_for('.admin'))
            else:
                abort(404)
        else:
            abort(403)
    else:
        return redirect(url_for('.index'))


@main.route("/new")
def new():
    u = current_user()
    if u is None:
        return redirect("/")
    bs = Board.all()
    return render_template("topic/new.html", bs=bs)


@main.route("/admin")
def admin():
    if current_user().role != 1:
        return redirect(url_for('index.index'))
    ms1 = []
    ms2 = []
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        # ms = Topic.all()
        ms1 = Topic.top()
        ms2 = Topic.cache_all()

    else:
        ms = Topic.find_all(board_id=board_id)
        for m in ms:
            if m.istop == True:
                ms1.append(m)
            else:
                ms2.append(m)
    token = str(uuid.uuid4())
    u = current_user()
    if u is not None:
        csrf_tokens[token] = u.id
    bs = Board.all()
    return render_template("topic/admin.html", ms1=ms1, ms2=ms2, token=token, bs=bs)


@main.route("/settop/<int:id>")
def settop(id):
    m = Topic.get(id)
    m.istop = True
    m.save()
    return redirect(url_for('.admin'))


@main.route("/setnotop/<int:id>")
def setnotop(id):
    m = Topic.get(id)
    m.istop = False
    m.save()
    return redirect(url_for('.admin'))
