import logging

from aiogram import Bot, Dispatcher, executor
from framework.database import setup_db
from framework.router import Router
from views import StartView, MainView, CalcView



API_TOKEN = '1961919405:AAF5HddmljDqsGTe-Upip0YCeFO7XsZ7LIQ'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)


router = Router(StartView)

router.add_route(MainView)
router.add_route(CalcView)

dp.message_handler()(router)
dp.callback_query_handler()(router)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=setup_db)
