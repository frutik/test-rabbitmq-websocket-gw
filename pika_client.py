import os
import pika

from pika.adapters.tornado_connection import TornadoConnection

class PikaClient(object):

    def __init__(self, username='guest', exchange_name='ws', password='guest', host='localhost', port=5672, virtual_host='/'):
	self.exchange_name = exchange_name

        # Options
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.virtual_host = virtual_host

        # Default values
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None

    def connect(self):
        if self.connecting:
            pika.log.info('PikaClient: Already connecting to RabbitMQ')
            return
        pika.log.info('PikaClient: Connecting to RabbitMQ on localhost:5672')
        self.connecting = True

        credentials = pika.PlainCredentials(self.username, self.password)
        param = pika.ConnectionParameters(host=self.host,
                                          port=self.port,
                                          virtual_host=self.virtual_host,
                                          credentials=credentials)
        self.connection = TornadoConnection(param,
                                            on_open_callback=self.on_connected)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        pika.log.info('PikaClient: Connected to RabbitMQ on localhost:5672')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        pika.log.info('PikaClient: Channel Open, Declaring Exchange')
        self.channel = channel

        self.channel.exchange_declare(exchange=self.exchange_name,
                                      type="direct",
                                      callback=self.on_exchange_declared)

    def on_exchange_declared(self, frame):
        pika.log.info('PikaClient: Exchange Declared, Ready for declaring Queues')

    def on_basic_cancel(self, frame):
        pika.log.info('PikaClient: Basic Cancel Ok')
        # If we don't have any more consumer processes running close
        self.connection.close()

    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        tornado.ioloop.IOLoop.instance().stop()

