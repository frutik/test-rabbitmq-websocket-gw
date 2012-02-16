import tornado.ioloop
import tornado.web
import tornado.websocket as websocket

from tornado.options import define, options

import os.path
import uuid
import time

http_settings = dict(
    cookie_secret=str(uuid.uuid1()),
    #template_path=os.path.join(os.path.dirname(__file__), "templates"),
    #static_path=os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=False,
    autoescape="xhtml_escape",
)

define("port", default=8888, help="run on the given port", type=int)

import logging
logging.basicConfig(level=logging.INFO)

import pika
from pika_client import PikaClient
from agent_channel_ws import AgentChannelWebSocket

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/agent/([0-9]+)', AgentChannelWebSocket),
        ]
        tornado.web.Application.__init__(self, handlers, http_settings)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)

    pc = PikaClient(
        username = 'guest',
        password = 'guest',
        host = '127.0.0.1',
        port = 5672,
        virtual_host = '/',
        exchange_name = 'ucall222'
    )
    pika.log.setup(color=True)

    app.pika = pc

    ioloop = tornado.ioloop.IOLoop.instance()

    # Add our Pika connect to the IOLoop with a deadline in 0.1 seconds
    ioloop.add_timeout(time.time() + .1, app.pika.connect)

    # Start the IOLoop
    ioloop.start()

if __name__ == "__main__":
    main()

