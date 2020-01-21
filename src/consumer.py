from aio_pika import connect, IncomingMessage, ExchangeType


class Server:
    def __init__(self, queues: dict, loop,  params):
        self.loop = loop
        self.queues = queues

        self.host = params.rmqhost
        self.port = params.rmqport
        self.user = params.rmquser
        self.password = params.rmqpass

    async def on_message(self, message: IncomingMessage):
        with message.process():
            await self.queues[message.routing_key](message.body.decode())

    async def handler(self):
        dsn = f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"

        connection = await connect(dsn, loop=self.loop)

        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            'beholder', ExchangeType.DIRECT
        )

        queue = await channel.declare_queue(durable=True)

        for routing_key in self.queues.keys():
            await queue.bind(exchange, routing_key=routing_key)

        await queue.consume(self.on_message)
