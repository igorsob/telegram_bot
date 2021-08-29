from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from framework.view import action, View
from models import Users


class CalcView(View):
    STAGE = 'calc'

    @classmethod
    async def get_inline_keyboard(cls):
        inline_keyboard = [
            [await cls.get_inline_button(cls.button_7), await cls.get_inline_button(cls.button_8), await cls.get_inline_button(cls.button_9)],
            [await cls.get_inline_button(cls.button_4), await cls.get_inline_button(cls.button_5), await cls.get_inline_button(cls.button_6)],
            [await cls.get_inline_button(cls.button_1), await cls.get_inline_button(cls.button_2), await cls.get_inline_button(cls.button_3)],
            [await cls.get_inline_button(cls.button_0)],
            [
                await cls.get_inline_button(cls.button_plus),
                await cls.get_inline_button(cls.button_minus),
                await cls.get_inline_button(cls.button_multiply),
                await cls.get_inline_button(cls.button_divide)
            ],
            [await cls.get_inline_button(cls.button_equals)],
            [await cls.get_inline_button(cls.button_clear), await cls.get_inline_button(cls.button_back)]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    async def main_message(self):
        await self.send_message('Выражение: ')

    @action(message='button_1', is_inline_button=True, text='1')
    async def button_1(self):
        await self.edit_message(self.message.message.text + '1')

    @action(message='button_2', is_inline_button=True, text='2')
    async def button_2(self):
        await self.edit_message(self.message.message.text + '2')

    @action(message='button_3', is_inline_button=True, text='3')
    async def button_3(self):
        await self.edit_message(self.message.message.text + '3')

    @action(message='button_4', is_inline_button=True, text='4')
    async def button_4(self):
        await self.edit_message(self.message.message.text + '4')

    @action(message='button_5', is_inline_button=True, text='5')
    async def button_5(self):
        await self.edit_message(self.message.message.text + '5')

    @action(message='button_6', is_inline_button=True, text='6')
    async def button_6(self):
        await self.edit_message(self.message.message.text + '6')

    @action(message='button_7', is_inline_button=True, text='7')
    async def button_7(self):
        await self.edit_message(self.message.message.text + '7')

    @action(message='button_8', is_inline_button=True, text='8')
    async def button_8(self):
        await self.edit_message(self.message.message.text + '8')

    @action(message='button_9', is_inline_button=True, text='9')
    async def button_9(self):
        await self.edit_message(self.message.message.text + '9')

    @action(message='button_0', is_inline_button=True, text='0')
    async def button_0(self):
        await self.edit_message(self.message.message.text + '0')

    @action(message='button_+', is_inline_button=True, text='+')
    async def button_plus(self):
        await self.edit_message(self.message.message.text + '+')

    @action(message='button_-', is_inline_button=True, text='-')
    async def button_minus(self):
        await self.edit_message(self.message.message.text + '-')

    @action(message='button_*', is_inline_button=True, text='*')
    async def button_multiply(self):
        await self.edit_message(self.message.message.text + '*')

    @action(message='button_/', is_inline_button=True, text='/')
    async def button_divide(self):
        await self.edit_message(self.message.message.text + '/')

    @action(message='button_=', is_inline_button=True, text='=')
    async def button_equals(self):
        text = eval(self.message.message.text.removeprefix('Выражение:'))
        await self.edit_message('Выражение:' + str(text))

    @action(message='button_clear', is_inline_button=True, text='Очистить')
    async def button_clear(self):
        await self.edit_message('Выражение:')

    @action(message='button_back', is_inline_button=True, text='Назад')
    async def button_back(self):
        main_view = MainView(self.user, self.message, True)
        await main_view.reroute()


class MainView(View):
    STAGE = 'main'

    async def main_message(self):
        await self.send_message('Меню')

    @action(message='calc', is_inline_button=True, text='Калькулятор')
    async def sd(self):
        calc_view = CalcView(self.user, self.message, True)
        await calc_view.reroute()


class StartView(View):
    STAGE = 'start'

    @action(message='/start')
    async def start(self):
        if not self.user:
            self.user = await Users.create_from_t_user(self.message.from_user)
        main_view = MainView(self.user, self.message)
        await main_view.reroute()

