import calendar
from datetime import datetime
from framework.view import action, View, InlineButton
from models import Users, Calendar


class CalendarView(View):
    STAGE = 'calendar'

    BUTTONS = [
        [InlineButton('button_back', 'Назад', 'button_back')]
    ]

    async def get_buttons(self):
        if self.user.stage_metadata['meta_stage'] == 'choice_year':
            buttons = await self.get_choice_year_buttons()
        elif self.user.stage_metadata['meta_stage'] == 'choice_month':
            buttons = await self.get_choice_month_buttons()
        else:
            buttons = await self.get_calendar_buttons()
        return buttons

    async def get_choice_year_buttons(self):
        today = datetime.today()

        def get_year_button(year_number):
            def get_text():
                year = str(year_number)
                if year_number == today.year:
                    year = f'|{year}|'
                if year_number == self.user.stage_metadata['year']:
                    year = f'<{year}>'
                return year
            return InlineButton(f'button_year_{year_number}', get_text(), 'button_choice_year_number')

        row = []
        for year in range(self.user.stage_metadata['year'] - 3, self.user.stage_metadata['year'] + 4):
            row.append(get_year_button(year))
        buttons = [row]
        buttons.append([InlineButton('button_refresh', 'Назад', 'button_refresh')])
        return buttons

    async def get_choice_month_buttons(self):
        today = datetime.today()

        def get_month_button(month_number):
            def get_text():
                month = calendar.month_name[month_number]
                if month_number == today.month and self.user.stage_metadata['year'] == today.year:
                    month = f'|{month}|'
                if month_number == self.user.stage_metadata['month']:
                    month = f'<{month}>'
                return month
            return InlineButton(f'button_month_{month_number}', get_text(), 'button_choice_month_number')

        month_index = 0
        buttons = []
        for i in range(4):
            row = []
            for y in range(3):
                month_index += 1
                row.append(get_month_button(month_index))
            buttons.append(row)
        buttons.append([InlineButton('button_refresh', 'Назад', 'button_refresh')])
        return buttons

    async def get_calendar_buttons(self):
        today = datetime.today()
        month = calendar.monthcalendar(self.user.stage_metadata['year'], self.user.stage_metadata['month'])
        buttons = [
            [
                InlineButton('button_choice_year', self.user.stage_metadata['year'], 'button_choice_year'),
                InlineButton('button_choice_month', calendar.month_name[self.user.stage_metadata['month']], 'button_choice_month'),
            ],
            [
                InlineButton('button_weekday', 'Пн', 'empty'),
                InlineButton('button_weekday', 'Вт', 'empty'),
                InlineButton('button_weekday', 'Ср', 'empty'),
                InlineButton('button_weekday', 'Чт', 'empty'),
                InlineButton('button_weekday', 'Пт', 'empty'),
                InlineButton('button_weekday', 'Сб', 'empty'),
                InlineButton('button_weekday', 'Вс', 'empty')
            ]
        ]

        def get_weekday_button(weekday_number):
            def get_text():
                day = ' ' if weekday_number == 0 else weekday_number
                if weekday_number == today.day and self.user.stage_metadata['month'] == today.month and self.user.stage_metadata['year'] == today.year:
                    day = f'|{day}|'
                if weekday_number == self.user.stage_metadata['day']:
                    day = f'<{day}>'
                return day
            return InlineButton(f'button_{weekday}', get_text(), 'empty' if weekday_number == 0 else 'button_weekday')
        for week in month:
            row = []
            for weekday in week:
                row.append(get_weekday_button(weekday))
            buttons.append(row)
        buttons.append([InlineButton('button_back', 'Назад', 'button_back')])
        return buttons

    async def button_choice_year(self):
        self.user.stage_metadata['meta_stage'] = 'choice_year'
        await self.user.save()
        await self.edit_message('Выберете год: ')

    async def button_choice_year_number(self):
        self.user.stage_metadata['meta_stage'] = 'calendar'
        self.user.stage_metadata['year'] = int(self.action.removeprefix('button_year_'))
        self.user.stage_metadata['month'] = 1
        self.user.stage_metadata['day'] = 1
        await self.user.save()
        await self.button_refresh()

    async def button_choice_month(self):
        self.user.stage_metadata['meta_stage'] = 'choice_month'
        await self.user.save()
        await self.edit_message('Выберете месяц: ')

    async def button_choice_month_number(self):
        self.user.stage_metadata['meta_stage'] = 'calendar'
        self.user.stage_metadata['month'] = int(self.action.removeprefix('button_month_'))
        self.user.stage_metadata['day'] = 1
        await self.user.save()
        await self.button_refresh()

    async def button_weekday(self):
        self.user.stage_metadata['day'] = int(self.action.removeprefix('button_'))
        await self.user.save()
        await self.button_refresh()

    async def empty(self):
        await Calendar.create(user_id=self.user.id, year=self.user.stage_metadata['year'], month=self.user.stage_metadata['month'], day=self.user.stage_metadata['day'], text=self.action)
        await self.button_refresh()

    async def get_doings(self):
        doings = await Calendar.filter(user_id=self.user.id, year=self.user.stage_metadata['year'], month=self.user.stage_metadata['month'], day=self.user.stage_metadata['day'])
        text = ''
        for doing in doings:
            text += doing.text + ' \n'
        return text

    async def button_refresh(self):
        self.user.stage_metadata['meta_stage'] = 'calendar'
        await self.user.save()
        await self.edit_message('События: \n' + await self.get_doings())

    async def main_message(self):
        today = datetime.today()
        self.user.stage_metadata = {'year': today.year, 'month': today.month, 'day': today.day, 'meta_stage': 'calendar'}
        await self.user.save()
        await self.send_message('События: \n' + await self.get_doings())

    async def button_back(self):
        main_view = MainView(self.user, self.message, True)
        await main_view.reroute()


class CalcView(View):
    STAGE = 'calc'

    BUTTONS = [
        [InlineButton(f'button_{i}', str(i), 'button_add_text') for i in range(7, 10)],
        [InlineButton(f'button_{i}', str(i), 'button_add_text') for i in range(4, 7)],
        [InlineButton(f'button_{i}', str(i), 'button_add_text') for i in range(1, 4)],
        [InlineButton('button_0', '0', 'button_add_text'), InlineButton('button_.', '.', 'button_add_text')],
        [
            InlineButton('button_+', '+', 'button_add_text'), InlineButton('button_-', '-', 'button_add_text'),
            InlineButton('button_*', '*', 'button_add_text'), InlineButton('button_/', '/', 'button_add_text')
         ],
        [InlineButton('button_=', '=', 'button_equals')],
        [InlineButton('button_clear', 'Очистить', 'button_clear'), InlineButton('button_back', 'Назад', 'button_back')]
    ]

    async def main_message(self):
        await self.send_message('Выражение: ')

    async def button_add_text(self):
        await self.edit_message(self.message.message.text + self.message.data.removeprefix('button_'))

    async def button_equals(self):
        text = eval(self.message.message.text.removeprefix('Выражение:'))
        await self.edit_message('Выражение:' + str(text))

    async def button_clear(self):
        await self.edit_message('Выражение:')

    async def button_back(self):
        main_view = MainView(self.user, self.message, True)
        await main_view.reroute()


class MainView(View):
    STAGE = 'main'

    BUTTONS = [
        [InlineButton('button_calc', 'Калькулятор', 'button_calc')],
        [InlineButton('button_calendar', 'Календарь', 'button_calendar')],
    ]

    async def main_message(self):
        await self.send_message('Меню')

    async def button_calc(self):
        calc_view = CalcView(self.user, self.message, True)
        await calc_view.reroute()

    async def button_calendar(self):
        calc_view = CalendarView(self.user, self.message, True)
        await calc_view.reroute()


class StartView(View):
    STAGE = 'start'

    @action(message='/start')
    async def start(self):
        if not self.user:
            self.user = await Users.create_from_t_user(self.message.from_user)
        main_view = MainView(self.user, self.message)
        await main_view.reroute()

