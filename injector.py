#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='ucall222',
                         type='direct')

agent = sys.argv[1] if len(sys.argv) > 1 else '14'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

channel.basic_publish(exchange='ucall222',
                      routing_key=agent,
                      body=message)
print " [x] Sent %r:%r" % (agent, message)
connection.close()