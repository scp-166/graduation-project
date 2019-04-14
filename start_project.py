from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer  # 替代django的uwsgi
from geventwebsocket.handler import WebSocketHandler  # websocket处理器
from project.wsgi import application
import argparse  # 替代sys.arg
import os


version = "1.0.0"

root_patch = os.path.dirname(__file__)

parser = argparse.ArgumentParser(
    description="基于树莓派和django的物联网项目"
)
parser.add_argument("--port", "-p",
                    type=int,
                    default=8000,
                    help="服务器端口，默认为8000")

parser.add_argument("--host", "-H",  # 避免和--help的简写冲突
                    default="0.0.0.0",
                    help="服务器ip，默认为0.0.0.0")

args = parser.parse_args()  # 监听ing

print("project {} is running on {}:{}".format(version, args.host, args.port))

wsgi_server = WSGIServer(  # 设置wsgi服务器
    (args.host, args.port),
    application,
    log=None,
    handler_class=WebSocketHandler
)

try:
    wsgi_server.serve_forever()
except KeyboardInterrupt:
    print("服务器退出")
    pass
