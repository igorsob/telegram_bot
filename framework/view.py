from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton


def action(message=None, is_inline_button=False, text=None, **kwargs):
    def _action(f):
        def wrapper(self, *f_args, **f_kwargs):
            return f(self, *f_args, **f_kwargs)
        wrapper.is_action = True
        wrapper.is_inline_button = is_inline_button
        wrapper.message = message
        wrapper.text = text
        wrapper.kwargs = kwargs
        return wrapper
    return _action


class View:
    STAGE = None

    def __init__(self, user, message, is_inline_keyboard=False):
        self.is_inline_keyboard = is_inline_keyboard
        self.user = user
        self.message = message
        self.bot = message.bot
        if self.is_inline_keyboard:
            self.chat = message.message.chat
        else:
            self.chat = message.chat

    @classmethod
    def get_stage_name(cls):
        if cls.STAGE:
            return cls.STAGE
        return cls.__name__.lower()

    @classmethod
    async def get_routes(cls):
        return {value.message: {'name': key, 'func': value}
                for key, value in cls.__dict__.items() if getattr(value, 'is_action', None)}

    @classmethod
    async def get_button_routes(cls):
        return {value.message: {'name': key, 'func': value}
                for key, value in cls.__dict__.items() if getattr(value, 'is_inline_button', None)}

    @classmethod
    async def get_inline_button(cls, func):
        return InlineKeyboardButton(text=func.text, callback_data=func.message)

    @classmethod
    async def get_inline_keyboard(cls):
        routes = await cls.get_button_routes()
        inline_keyboard = []
        for value in routes.values():
            inline_keyboard.append([await cls.get_inline_button(value['func'])])
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    async def get_route(self):
        if self.is_inline_keyboard:
            routes = await self.get_button_routes()
            route = routes.get(self.message.data)
        else:
            routes = await self.get_routes()
            route = routes.get(self.message.text)
        if route:
            return route['name']
        return 'empty'

    async def dispatch(self):
        route = await self.get_route()
        await self.call_route(route)

    async def call_route(self, route):
        await (getattr(self, route))()
        if not self.is_inline_keyboard:
            await self.message.delete()

    async def _send_message(self, text, reply_markup):
        if not reply_markup:
            reply_markup = await self.get_inline_keyboard()
        return await self.bot.send_message(self.chat.id, text, reply_markup=reply_markup)

    async def send_message(self, text, reply_markup=None):
        message = await self._send_message(text, reply_markup)
        if self.user.main_message_id:
            await self.bot.delete_message(self.chat.id, self.user.main_message_id)
        self.user.main_message_id = message.message_id
        await self.user.save()
        return message

    async def edit_message(self, text=None, reply_markup=None):
        if not reply_markup:
            reply_markup = await self.get_inline_keyboard()
        if text:
            await self.bot.edit_message_text(text, self.chat.id, self.user.main_message_id, reply_markup=reply_markup)

    async def reroute(self):
        self.user.stage = self.get_stage_name()
        await self.user.save()
        await self.main_message()

    async def empty(self):
        pass

    async def main_message(self):
        pass
