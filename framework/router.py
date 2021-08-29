from aiogram.types.callback_query import CallbackQuery
from models import Users


class Router:

    def __init__(self, start_view):
        self.routes = {'start': start_view}

    async def __call__(self, message):
        user = await Users.filter_one(t_id=message.from_user.id)
        if user:
            view_class = self.routes[user.stage]
        else:
            view_class = self.routes['start']
        is_inline_keyboard = False
        if isinstance(message, CallbackQuery):
            is_inline_keyboard = True
        view = view_class(user, message, is_inline_keyboard=is_inline_keyboard)
        await view.dispatch()

    def add_route(self, view_class):
        self.routes[view_class.get_stage_name()] = view_class
