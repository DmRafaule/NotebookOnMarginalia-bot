from aiogram.filters import BaseFilter
from aiogram.types import Message
from magic_filter.util import in_op, not_in_op, contains_op

from config import i18n_handler

from middleware import StringsMiddleware


class StringsInFilter(BaseFilter):  # [1]
    options = None
    option_key = None

    def __init__(self, option_key: str):
        self.option_key = option_key

    async def __call__(
            self,
            message: Message,
            ) -> bool:
        # Get current locale code 'ru', 'en'
        lk = StringsMiddleware(message.from_user.id)
        with i18n_handler.i18n.context(), i18n_handler.i18n.use_locale(message.from_user.language_code):
            await lk.update_locales(message.from_user.language_code)
        for var in lk.__dict__:
            if var == self.option_key:
                self.options = lk.__dict__[var]
        return in_op(self.options, message.text)


class StringsNotInFilter(BaseFilter):  # [1]
    options = None
    option_key = None

    def __init__(self, option_key: str):
        self.option_key = option_key

    async def __call__(
            self,
            message: Message,
            ) -> bool:
        # Get current locale code 'ru', 'en'
        lk = StringsMiddleware(message.from_user.id)
        with i18n_handler.i18n.context(), i18n_handler.i18n.use_locale(message.from_user.language_code):
            await lk.update_locales(message.from_user.language_code)
        for var in lk.__dict__:
            if var == self.option_key:
                self.options = lk.__dict__[var]
        return not_in_op(self.options, message.text)
