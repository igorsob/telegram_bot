from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton


def action(message=None, **kwargs):
    def _action(f):
        def wrapper(self, *f_args, **f_kwargs):
            return f(self, *f_args, **f_kwargs)
        wrapper.is_action = True
        wrapper.message = message
        wrapper.kwargs = kwargs
        return wrapper
    return _action


class InlineButton:

    def __init__(self, data, text, func):
        self.data = data
        self.text = text
        self.func = func


class View:
    STAGE = None

    BUTTONS = [[]]

    def __init__(self, user, message, is_inline_keyboard=False):
        self.is_inline_keyboard = is_inline_keyboard
        self.user = user
        self.message = message
        self.bot = message.bot
        if self.is_inline_keyboard:
            self.chat = self.message.message.chat
            self.action = self.message.data
        else:
            self.chat = self.message.chat
            self.action = self.message.text

    @classmethod
    def get_stage_name(cls):
        if cls.STAGE:
            return cls.STAGE
        return cls.__name__.lower()

    @classmethod
    async def get_routes(cls):
        return {value.message: key for key, value in cls.__dict__.items() if getattr(value, 'is_action', None)}

    async def get_buttons(self):
        return self.BUTTONS

    async def get_button_routes(self):
        routes = {}
        for row in await self.get_buttons():
            for button in row:
                routes[button.data] = button.func
        return routes

    async def get_inline_button(self, button):
        return InlineKeyboardButton(text=button.text, callback_data=button.data)

    async def get_inline_keyboard(self):
        buttons = await self.get_buttons()
        inline_keyboard = []
        for buttons_row in buttons:
            row = []
            for button in buttons_row:
                row.append(await self.get_inline_button(button))
            inline_keyboard.append(row)
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    async def get_route(self):
        routes = await self.get_button_routes() if self.is_inline_keyboard else await self.get_routes()
        route = routes.get(self.action)
        if route:
            return route
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
        return await self.bot.send_message(self.chat.id, text, reply_markup=reply_markup, parse_mode='MarkdownV2')

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
            await self.bot.edit_message_text(text, self.chat.id, self.user.main_message_id, reply_markup=reply_markup, parse_mode='MarkdownV2')

    async def reroute(self):
        self.user.stage = self.get_stage_name()
        await self.user.save()
        await self.main_message()

    async def empty(self):
        pass

    async def main_message(self):
        pass
