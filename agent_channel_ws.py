import tornado.websocket as websocket
import pika
import uuid

class AgentChannelWebSocket(websocket.WebSocketHandler):
    def open(self, agent_id):
        pika.log.info('PikaClient: WebSocket opened, Declaring Queue')

        self.queue_name = str(uuid.uuid1()) 
        self.agent_id = agent_id

        self.application.pika.channel.queue_declare(exclusive=True, queue=self.queue_name, callback=self.on_queue_declared)

    def on_message(self, message):
        pika.log.info('PikaClient: WebSocket got message, TODO send it to somebody?')
        
        self.write_message(u"You said: " + message)

    def on_close(self):
        pika.log.info('PikaClient: WebSocket closed, TODO cancel consumming stuff')
        
	self.application.pika.channel.queue_unbind(
	    callback=self.on_queue_unbound, 
	    queue=self.queue_name, 
	    exchange=self.application.pika.exchange_name, 
	    routing_key=self.agent_id
	)
	
    def on_queue_unbound(self, method):
	self.application.pika.channel.queue_delete(callback=None, queue=self.queue_name)

    def on_queue_declared(self, frame):
        pika.log.info('PikaClient: Queue Declared, Binding Queue')
        
        self.application.pika.channel.queue_bind(exchange=self.application.pika.exchange_name,
                                queue=self.queue_name,
                                routing_key=self.agent_id,
                                callback=self.on_queue_bound)

    def on_queue_bound(self, frame):
        pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')

        self.application.pika.channel.basic_consume(consumer_callback=self.on_pika_message,
                                   queue=self.queue_name,
                                   no_ack=True)

    def on_pika_message(self, channel, method, header, body):
	pika.log.info('PikaCient: Message receive, delivery tag #%i' % method.delivery_tag)
        self.write_message(u"You got: " + body)
