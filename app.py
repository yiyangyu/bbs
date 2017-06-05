from flask import Flask
from routes import current_user
import config


# web framework
# web application
# __main__
app = Flask(__name__)
# 设置 secret_key 来使用 flask 自带的 session
# 这个字符串随便你设置什么内容都可以
app.secret_key = config.secret_key
# 设置全局变量渲染多个HTML模板
app.add_template_global(current_user, 'user')


"""
在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
用法如下
"""
# 注册蓝图
# 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀
from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.board import main as board_routes
from routes.mail import main as mail_routes
from routes.user import main as user_routes
from markdown import markdown
app.register_blueprint(index_routes)
app.register_blueprint(topic_routes, url_prefix='/topic')
app.register_blueprint(reply_routes, url_prefix='/reply')
app.register_blueprint(board_routes, url_prefix='/board')
app.register_blueprint(mail_routes, url_prefix='/mail')
app.register_blueprint(user_routes, url_prefix='/user')


def config_log(app):
    if not app.debug:
        import logging
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)


@app.context_processor
# 设置全局变量渲染模板
def include_current_user():
    return {'current_user': current_user()}


@app.context_processor
def include_markdown():
    return {'markdown': markdown}


@app.template_filter('delta')
def delta_time(unix_time):
    if unix_time is None:
        return ''
    import datetime
    past = datetime.datetime.fromtimestamp(unix_time)
    now = datetime.datetime.now()
    delta = now - past
    days = delta.days
    if days >= 365:
        return str(days // 365) + ' 年前'
    elif 30 <= days < 365:
        return str(days // 30) + ' 月前'
    else:
        if delta.days != 0:
            return str(delta.days) + ' 天前'
        else:
            sec = delta.seconds
            if sec < 60:
                return str(sec) + ' 秒前'
            elif sec < 3600:
                return str(sec // 60) + ' 分钟前'
            else:
                return str(sec // 3600) + ' 小时前'

# 运行代码
if __name__ == '__main__':
    # debug 模式可以自动加载你对代码的变动, 所以不用重启程序
    # host 参数指定为 '0.0.0.0' 可以让别的机器访问你的代码
    config = dict(
        debug=True,
        host='0.0.0.0',
        port=2000,
    )
    config_log(app)
    app.run(**config)
