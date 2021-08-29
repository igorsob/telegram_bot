from aiopg.sa import create_engine


class Database:

    def __init__(self):
        self.engine = None
        self.conn = None

    async def open(self):
        self.engine = await create_engine(user='saia_user',
                                          database='bot_test',
                                          host='127.0.0.1',
                                          password='saia_pass')
        self.conn = await self.engine.acquire()


db = Database()


async def setup_db(dispatcher):
    await db.open()
    dispatcher.db = db
