from aiogram import BaseMiddleware
from aiogram.utils.i18n import gettext as _
from typing import Any, Callable, Dict, Awaitable
from aiogram.types import TelegramObject


from config import i18n_handler, bot_dispatcher, bot
import callbacks as CB


class StringsMiddleware(BaseMiddleware):
    _instance = {
        0: None,
    }
    current_locale = 'ru'
    with i18n_handler.i18n.context():
        search_options = {
                _('Искать везде'): {
                    'searcher': CB.GetNotes,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _('Искать по заголовку'): {
                    'searcher': CB.GetNotes,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _('Искать по содержимому'): {
                    'searcher': CB.GetNotes,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _('Искать по категориям'): {
                    'searcher': CB.GetNotes,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _('Искать по подкатегориям'): {
                    'searcher': CB.GetNotes,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _("Искать по времени до 'YYYY-MM-DD'"): {
                    'searcher': CB.GetAllNotesBeforePeriod,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _("Искать по времени после 'YYYY-MM-DD'"): {
                    'searcher': CB.GetAllNotesAfterPeriod,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _("Найти подкатегории, категории"): {
                    'searcher': CB.GetAllSubcategoriesOfCategory,
                    'viewer': CB.SimpleListView,
                    'volatile': False,
                    'remove_action': 'remove_category',
                    'edit_action': 'edit_category'},
        }

        order_options = {
                _('С самых ранних'): None,
                _('С самых поздних'): None
        }

        note_preview_options = {
                _('Необходимая информации'): CB.NoteNesessaryView,
                _('Вся информация'): CB.NoteFullView,
                _('Минимум информации'): CB.NoteMinimalView,
                _('Только существующая'): CB.NoteAllPossibleView,
        }

        other_search_options = {
                _("Заметки за всё время"): {
                    'searcher': CB.GetAllNotes,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _("Заметки за сегодня"): {
                    'searcher': CB.GetAllNotesForToday,
                    'viewer': CB.NoteNesessaryView,
                    'volatile': True,
                    'remove_action': 'remove_note',
                    'edit_action': 'edit_note'},
                _("Все существующие категории"): {
                    'searcher': CB.GetAllCategories,
                    'viewer': CB.SimpleListView,
                    'volatile': False,
                    'remove_action': 'remove_category',
                    'edit_action': 'edit_category'},
        }
        other_options = {
                _('« Назад'): None,
                _('Настройки'): None,
                _('Другое'): None,
        }

        note_change_options = {
                _('Изменить заголовок'): {'field': 'title'},
                _('Изменить категорию'): {'field': 'category'},
                _('Изменить подкатегорию'): {'field': 'subcategory'},
                _('Изменить содержимое'): {'field': 'text'},
        }

    def __new__(self, id: None):
        if id is None:
            id = 0
        if self._instance.get(id) is None:
            self._instance[id] = super(StringsMiddleware, self).__new__(self)
        return self._instance[id]

    async def update_locales(self, locale: str):
        with i18n_handler.i18n.context(), i18n_handler.i18n.use_locale(locale):
            self.search_options = {
                    _('Искать везде'): {
                        'searcher': self.search_options[list(self.search_options.keys())[0]]['searcher'],
                        'viewer': self.search_options[list(self.search_options.keys())[0]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _('Искать по заголовку'): {
                        'searcher': self.search_options[list(self.search_options.keys())[1]]['searcher'],
                        'viewer': self.search_options[list(self.search_options.keys())[1]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _('Искать по содержимому'): {
                        'searcher': self.search_options[list(self.search_options.keys())[2]]['searcher'],
                        'viewer': self.search_options[list(self.search_options.keys())[2]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _('Искать по категориям'): {
                        'searcher': self.search_options[list(self.search_options.keys())[3]]['searcher'],
                        'viewer': self.search_options[list(self.search_options.keys())[3]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _('Искать по подкатегориям'): {
                        'searcher': self.search_options[list(self.search_options.keys())[4]]['searcher'],
                        'viewer': self.search_options[list(self.search_options.keys())[4]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _("Искать по времени до 'YYYY-MM-DD'"): {
                        'searcher': self.search_options[list(self.search_options.keys())[5]]['searcher'],
                        'viewer': self.search_options[list(self.search_options.keys())[5]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _("Искать по времени после 'YYYY-MM-DD'"): {
                        'searcher': self.search_options[list(self.search_options.keys())[6]]['searcher'],
                        'viewer': self.search_options[list(self.search_options.keys())[6]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _("Найти подкатегории, категории"): {
                        'searcher': self.search_options[list(self.search_options.keys())[7]]['searcher'],
                        'viewer': self.search_options[list(self.search_options.keys())[7]]['viewer'],
                        'volatile': False,
                        'remove_action': 'remove_category',
                        'edit_action': 'edit_category'},
            }

            self.order_options = {
                    _('С самых ранних'): None,
                    _('С самых поздних'): None
            }

            self.note_preview_options = {
                    _('Необходимая информации'): CB.NoteNesessaryView,
                    _('Вся информация'): CB.NoteFullView,
                    _('Минимум информации'): CB.NoteMinimalView,
                    _('Только существующая'): CB.NoteAllPossibleView,
            }

            self.other_search_options = {
                    _("Заметки за всё время"): {
                        'searcher': self.other_search_options[list(self.other_search_options.keys())[0]]['searcher'],
                        'viewer': self.other_search_options[list(self.other_search_options.keys())[0]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _("Заметки за сегодня"): {
                        'searcher': self.other_search_options[list(self.other_search_options.keys())[1]]['searcher'],
                        'viewer': self.other_search_options[list(self.other_search_options.keys())[1]]['viewer'],
                        'volatile': True,
                        'remove_action': 'remove_note',
                        'edit_action': 'edit_note'},
                    _("Все существующие категории"): {
                        'searcher': self.other_search_options[list(self.other_search_options.keys())[2]]['searcher'],
                        'viewer': self.other_search_options[list(self.other_search_options.keys())[2]]['viewer'],
                        'volatile': False,
                        'remove_action': 'remove_category',
                        'edit_action': 'edit_category'},
            }
            self.other_options = {
                _('« Назад'): None,
                _('Настройки'): None,
                _('Другое'): None,
            }

            self.note_change_options = {
                _('Изменить заголовок'): {'field': 'title'},
                _('Изменить категорию'): {'field': 'category'},
                _('Изменить подкатегорию'): {'field': 'subcategory'},
                _('Изменить содержимое'): {'field': 'text'},
            }

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # Get current locale code 'ru', 'en'
        self.current_locale = await i18n_handler.get_locale(event=event, data=data) or i18n_handler.i18n.default_locale
        # Update our strings
        await self.update_locales(self.current_locale)
        # Save them to telegram dictionary
        data['search_options'] = self.search_options
        data['order_options'] = self.order_options
        data['note_preview_options'] = self.note_preview_options
        data['other_search_options'] = self.other_search_options
        data['other_options'] = self.other_options
        data['note_change_options'] = self.note_change_options
        return await handler(event, data)
