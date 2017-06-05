from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    make_response,
    send_from_directory,
    abort,
)

from werkzeug.utils import secure_filename
from models.user import User
from config import user_file_director
import os
from routes import *

main = Blueprint('index', __name__)


def current_user():
    # 从 session 中找到 user_id 字段, 找不到就 -1
    # 然后 User.find_by 来用 id 找用户
    # 找不到就返回 None
    uid = session.get('user_id', -1)
    u = User.find_by(id=uid)
    return u


"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/logout")
def log_out():
    u = current_user()
    if u is None:
        return redirect(url_for(".index"))
    session.pop("user_id")
    return redirect(url_for(".index"))


@main.route("/")
def index():
    u = current_user()
    # print(123)
    # log(123333)
    # logger.debug('just do it')
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    form = request.form
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('topic.index'))
    else:
        # session 中写入 user_id
        # print('session before', session)
        session['user_id'] = u.id
        # print('session after', session)
        # 设置 cookie 有效期为 永久
        session.permanent = True
        return redirect(url_for('topic.index'))


# @main.route('/profile')
# def profile():
#     u = current_user()
#     if u is None:
#         return redirect(url_for('.index'))
#     else:
#         return render_template('profile.html', user=u)


def allow_file(filename):
    suffix = filename.split('.')[-1]
    from config import accept_user_file_type
    return suffix in accept_user_file_type


@main.route('/addimg', methods=["POST"])
def add_img():
    u = current_user()

    if u is None:
        return redirect(url_for(".profile"))

    if 'file' not in request.files:
        # return redirect(request.url)
        abort(500)

    file = request.files['file']
    if file.filename == '':
        abort(500)
        # return redirect(url_for(".profile"))

    if allow_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(user_file_director, filename))  # 路径拼接
        u.user_image = filename
        u.save()

    return redirect(url_for(".setting"))


# send_from_directory
# nginx 静态文件
@main.route("/uploads/<filename>")
def uploads(filename):
    if filename is None:
        return ''
    return send_from_directory(user_file_director, filename)


@main.route('/setting')
def setting():
    # print(2333)
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template('setting.html', user=u)


@main.route('/setpass', methods=["POST"])
def setpass():
    u = current_user()
    oldpass = request.form.get('old_pass', '')
    if u is not None and u.password == u.salted_password(oldpass):
        pwd = request.form.get('new_pass')
        u.password = u.salted_password(pwd)
        u.save()
        return redirect(url_for('.setting'))
    else:
        abort(403)
