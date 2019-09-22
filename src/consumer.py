import aio_pika


class Server:
    def __init__(self, wssrv, loop, queues: list, params):
        self.wssrv = wssrv
        self.loop = loop
        self.queues = ['speed_violation']
        self.host = params.rmqhost
        self.port = params.rmqport
        self.user = params.rmquser
        self.password = params.rmqpass

    async def handler(self):
        dsn = f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"

        connection = await aio_pika.connect_robust(dsn, loop=self.loop)

        async with connection:
            # Creating channel
            channel = await connection.channel()

            # Declaring queue
            for queue_name in self.queues:
                queue = await channel.declare_queue(
                    queue_name, auto_delete=True
                )

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            await self.wssrv.send(message.body.decode())
