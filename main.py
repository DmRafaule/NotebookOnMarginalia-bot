import asyncio
import logging
import sys

from aiogram.types import Message
from aiogram import F, types
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup


from config import FILE_PATH, bot_dispatcher, bot
from filters import StringsInFilter, StringsNotInFilter
from middleware import StringsMiddleware
import callbacks as CB
from NotebookMarginalia.data_manager.manager import DataManagerLocal, Note


# создаём форму и указываем поля
class NoteSteps(StatesGroup):
    text = State()
    title = State()
    category = State()
    subcategory = State()


class NoteChangeSteps(StatesGroup):
    select_change_option = State()
    changing_category = State()
    changing = State()


class Search(StatesGroup):
    start_search = State()
    setup_search = State()
    searching = State()
    end_search = State()


# For handling data sending via inline button
class NotesCallbackData(CallbackData, prefix="notes"):
    action: str
    id: Optional[str] = None
    length: Optional[int] = None
    counter: Optional[int] = None
    step: Optional[int] = None
    step_offset: Optional[int] = None


# Init default values(only once) to be used by bot
async def InitDefaults(state: FSMContext, search_options, order_options, note_preview_options):
    data = await state.get_data()
    if data.get('notes_number') is None:
        await state.update_data(notes_number=2)
    if data.get('current_search_option') is None:
        await state.update_data(current_search_option=list(search_options.keys())[0])
    if data.get('current_order_option') is None:
        await state.update_data(current_order_option=list(order_options.keys())[0])
    if data.get('current_note_preview_option') is None:
        await state.update_data(current_note_preview_option=list(note_preview_options.keys())[0])


# Build a search menu for 'search_options' keyboard
async def BuildSearchMenu(current_search_option, search_options, other_options):
    builder = ReplyKeyboardBuilder()
    for key in search_options:
        if key == current_search_option:
            builder.add(types.KeyboardButton(text=f'» {current_search_option} «', ))
        else:
            builder.add(types.KeyboardButton(text=f'{key}'), )
    for key in other_options:
        builder.add(types.KeyboardButton(text=f'{key}'), )
    builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 3)
    return builder


async def BuildSettingsMenu(state):
    data = await state.get_data()
    note_preview = data['current_note_preview_option']
    current_order_option = data['current_order_option']
    note_num = data['notes_number']
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=_('Заметки: {note_preview}').format(note_preview=note_preview)))
    builder.add(types.KeyboardButton(text=_('Порядок: {current_order_option}').format(current_order_option=current_order_option)))
    builder.add(types.KeyboardButton(text=_('Количество: По {note_num} за раз').format(note_num=note_num)))
    builder.add(types.KeyboardButton(text=_('« Назад')))
    builder.adjust(1)
    return builder


# Build a menu for 'other_search_options' keyboard
async def BuildSearchOtherMenu(container, selector):
    builder = ReplyKeyboardBuilder()
    for option in container:
        if selector is not None and option == selector:
            builder.add(types.KeyboardButton(text=f'» {option} «'))
        else:
            builder.add(types.KeyboardButton(text=f'{option}'))
    builder.add(types.KeyboardButton(text=_('« Назад')))
    builder.adjust(1)
    return builder


# Build a keyboard for adding new notes
async def BuildAddProccessMenu(keys):
    builder = ReplyKeyboardBuilder()
    for key in keys:
        builder.add(types.KeyboardButton(text=f'{key}'), )
    builder.adjust(2, 2)
    return builder


# Build a menu for main menu
async def BuildMainMenu():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=_('Добавить новую')), )
    builder.add(types.KeyboardButton(text=_('Поиск заметок')))
    return builder


# Handle /start command
@bot_dispatcher.message(CommandStart())
async def command_start(message: Message, state: FSMContext, search_options, order_options, note_preview_options) -> None:
    await InitDefaults(state, search_options, order_options, note_preview_options)
    link_builder = InlineKeyboardBuilder()
    link_builder.button(text=_('Web версия'), url="https://timthewebmaster.com/ru/tools/notepad_on_marginalia/")
    link_builder.button(text=_('CLI версия'), url="https://github.com/DmRafaule/NotebookMarginalia/")
    await message.answer(_("""
    <b>NotepadOnMarginalia</b>
    от <i>Тимы зе Вебмастера</i>

    Заметки в телеграм.
    """),
        reply_markup=link_builder.as_markup(resize_keyboard=True))
    # I needed a way to attach a keyboard to bottom.
    # So this message appeared
    menu_builder = await BuildMainMenu()
    await message.answer(
            _("Спасибо что выбрал(а) меня."),
            reply_markup=menu_builder.as_markup(resize_keyboard=True)
    )


# Handle /help command
@bot_dispatcher.message(Command("help"))
async def command_help(message: Message, state: FSMContext, search_options, order_options, note_preview_options) -> None:
    await InitDefaults(state, search_options, order_options, note_preview_options)
    await message.answer(_("""Доступные команды для ввода:
    /start - запускает бота.
    /help - отправляет данную справку.
    /add - добавить новую заметку
    /search - ищет заметки
    /search_other - другие поисковые возможности
    /settings - настройки работы бота
    """))


# Handle /search command
@bot_dispatcher.message(Command('search'))
@bot_dispatcher.message(F.text == __('Поиск заметок'))
async def command_search(message: Message, state: FSMContext, search_options, order_options, note_preview_options, other_options) -> None:
    await InitDefaults(state, search_options, order_options, note_preview_options)
    # Set state to start_search to handle next user input in 'command_search_update' function
    await state.set_state(Search.start_search)
    # Build up an keyboard
    data = await state.get_data()
    builder = await BuildSearchMenu(data['current_search_option'], search_options, other_options)
    # Send a message
    await message.answer(_("Выбран режим: {rem}").format(rem=data['current_search_option']), reply_markup=builder.as_markup())


# This is an update function for /search command.
# The only reason to almost duplicate a function above
# It is because I couldn't find a way to split 'message.text' and data['current_search_option']
# In such a way that it will be work in one function.
# If be honest I'm not even try hard. Time is mone.
@bot_dispatcher.message(StateFilter(Search.start_search), StringsInFilter(option_key="search_options"))
async def command_search_by_option(message: Message, state: FSMContext, search_options, other_options) -> None:
    # Update state data
    await state.update_data(current_search_option=message.text)
    await state.update_data(current_search_options=search_options)
    # Build up an keyboard
    builder = await BuildSearchMenu(message.text, search_options, other_options)
    # Send a message
    await message.answer(_('Выбран режим: {rem}').format(rem=message.text), reply_markup=builder.as_markup())


# Pagination function.
# It must be called by some handler or by some command
async def Paginate(
        notes,
        length,
        counter,
        step,
        step_offset,
        current_search_option,
        current_search_options,
        sender):
    # Get a representation of each record

    for view in current_search_options[current_search_option]['viewer'](notes[counter:step_offset]):
        action_buttons = InlineKeyboardBuilder()
        # Add a remove button
        action_buttons.button(
            text="⨯",
            callback_data=NotesCallbackData(
                action=current_search_options[current_search_option]['remove_action'],
                id=view['id']
            )
        )
        # Add a edit button
        action_buttons.button(
            text="✎",
            callback_data=NotesCallbackData(
                action=current_search_options[current_search_option]['edit_action'],
                id=view['id']
            )
        )
        # Make them layout horizontal
        action_buttons.adjust(2)
        # Send a record to user
        await sender.answer(view['msg'], reply_markup=action_buttons.as_markup())
    # Set up an Inline(attached to an message ) buttons
    paginator_buttons = InlineKeyboardBuilder()
    up_limit = step_offset
    # If we get to the end set up only back button
    if up_limit >= length:
        up_limit = length
        # And only if number of notes more than pagination step
        if length > step:
            paginator_buttons.button(text=_("Назад"), callback_data=NotesCallbackData(
                action="next_notes",
                length=length,
                counter=counter - step,
                step=step,
                step_offset=step_offset - step
                )
            )
    # If we are on start of pagination set up only next button
    elif up_limit <= step:
        # And only if number of notes more than pagination step
        if length > step:
            paginator_buttons.button(text=_("Дальше"), callback_data=NotesCallbackData(
                action="next_notes",
                length=length,
                counter=counter + step,
                step=step,
                step_offset=step_offset + step
                )
            )
    # And If we are in a middle then create both back and next buttons
    else:
        paginator_buttons.button(text=_("Назад"), callback_data=NotesCallbackData(
            action="next_notes",
            length=length,
            counter=counter - step,
            step=step,
            step_offset=step_offset - step
            )
        )
        paginator_buttons.button(text=_("Дальше"), callback_data=NotesCallbackData(
            action="next_notes",
            length=length,
            counter=counter + step,
            step=step,
            step_offset=step_offset + step
            )
        )
        # Make them line up horizontal
        paginator_buttons.adjust(2)
    # Display an answer depends on how many records was displayed by 'viewer callback'
    if length > 0:
        if length == 1:
            await sender.answer(_("Нашёл одну запись."), reply_markup=paginator_buttons.as_markup())
        elif length > 1 and length < 5:
            await sender.answer(_("Нашёл {length} записи. (от {one} до {up_limit})").format(length=length,one=counter + 1,up_limit=up_limit), reply_markup=paginator_buttons.as_markup())
        else:
            await sender.answer(_("Нашёл {length} записей. (от {one} до {up_limit})").format(length=length,one=counter + 1,up_limit=up_limit), reply_markup=paginator_buttons.as_markup())
    else:
        await sender.answer(_("Ничего не нашёл."), reply_markup=paginator_buttons.as_markup())


# This is an handler for user input after 'search_options' have been choosen
# It is caller of Paginate func
@bot_dispatcher.message(
        StateFilter(Search.start_search),
        StringsNotInFilter(option_key="other_options"),
        F.text.not_contains('/add'))
async def command_search_by_option_queryHandler(message: Message, state: FSMContext, search_options) -> None:
    data = await state.get_data()
    current_search_option = data['current_search_option']
    # Find notes by query, sended by user
    note_data = search_options[current_search_option]['searcher']({
        "query": message.text,
        "user_id": message.from_user.id,
        "notes_number": data['notes_number'],
        "where": data['current_search_option'],
        "order": data['current_order_option'],
        "view": data['current_note_preview_option'],
    })
    # Update state data for search by option
    await state.update_data(notes=note_data)
    # This state data needed to 'remove' or 'edit' whole categories
    # This is not good by the way. TODO. SubCategory because dealing with categories in 'other_search_options'
    await state.update_data(field='subcategory')
    await state.update_data(current_search_option=current_search_option)
    await state.update_data(current_search_options=search_options)
    # For now only that work. Update translated dicts
    lk = StringsMiddleware(message.from_user.id)
    search_options = lk.search_options
    # Start to paginate
    await Paginate(
            notes=note_data,
            length=len(note_data),
            counter=0,
            step=data['notes_number'],
            step_offset=data['notes_number'],
            current_search_option=current_search_option,
            current_search_options=search_options,
            sender=message
    )


# Build a menu for other search options iem 'other_search_options' dict
# Possibly there is a way to combine 'search_by_other' and 'search_by_option' function
# But need to change data structures.
@bot_dispatcher.message(Command('search_other'))
@bot_dispatcher.message(StateFilter(Search.start_search), F.text == __('Другое'))
async def command_search_by_other(message: Message, state: FSMContext, other_search_options, search_options, order_options, note_preview_options) -> None:
    await InitDefaults(state, search_options, order_options, note_preview_options)
    await state.set_state(Search.setup_search)
    builder = await BuildSearchOtherMenu(other_search_options, None)
    await message.answer(_('Другие поисковые функции'), reply_markup=builder.as_markup(resize_keyboard=True))


# This is an handler for user input after 'other_search_options' have been choosen
# It is caller of Paginate func
@bot_dispatcher.message(StateFilter(Search.setup_search), StringsInFilter(option_key="other_search_options"))
async def command_search_by_other_queryHandler(message: Message, state: FSMContext, other_search_options) -> None:
    data = await state.get_data()
    current_search_option = message.text
    # Find notes by query, sended by user
    note_data = other_search_options[current_search_option]['searcher']({
        "query": message.text,
        "user_id": message.from_user.id,
        "notes_number": data['notes_number'],
        "where": data['current_search_option'],
        "order": data['current_order_option'],
        "view": data['current_note_preview_option'],
    })
    # Update state data for search by option
    await state.update_data(notes=note_data)
    # This state data needed to 'remove' or 'edit' whole categories
    # This is not good by the way. TODO. Category because dealing with categories in 'other_search_options'
    await state.update_data(field='category')
    await state.update_data(current_search_option=message.text)
    await state.update_data(current_search_options=other_search_options)
    lk = StringsMiddleware(message.from_user.id)
    other_search_options = lk.other_search_options
    # Start to paginate
    await Paginate(
            notes=note_data,
            length=len(note_data),
            counter=0,
            step=data['notes_number'],
            step_offset=data['notes_number'],
            current_search_option=message.text,
            current_search_options=other_search_options,
            sender=message
    )


# Function to update pagination for user. Get next or prev notes.
# If there is such notes
# It is caller of Paginate func
@bot_dispatcher.callback_query(NotesCallbackData.filter(F.action == 'next_notes'))
async def update_search_queryHandler(
        callback: types.CallbackQuery,
        callback_data: NotesCallbackData,
        state: FSMContext
        ):
    data = await state.get_data()
    # Update pagination
    await Paginate(
            notes=data['notes'],
            length=callback_data.length,
            counter=callback_data.counter,
            step=callback_data.step,
            step_offset=callback_data.step_offset,
            current_search_option=data['current_search_option'],
            current_search_options=data['current_search_options'],
            sender=callback.message,
    )


# Delete a note by id
@bot_dispatcher.callback_query(NotesCallbackData.filter(F.action == 'remove_note'))
async def delete_note(
        callback: types.CallbackQuery,
        callback_data: NotesCallbackData,
        state: FSMContext
        ):
    if CB.RemoveNote(callback_data.id):
        await callback.message.answer(_("Заметка удалена."))
    else:
        await callback.message.answer(_("Не смог удалить заметку."))


# Delete a notes by selected category
@bot_dispatcher.callback_query(NotesCallbackData.filter(F.action == 'remove_category'))
async def delete_category(
        callback: types.CallbackQuery,
        callback_data: NotesCallbackData,
        state: FSMContext
        ):
    data = await state.get_data()
    cat_to_delete = callback.message.text
    field = data['field']
    if CB.RemoveBy(cat_to_delete, field, str(callback.from_user.id)):
        await callback.message.answer(_("(Под)категория удалена."))
    else:
        await callback.message.answer(_("(Под)категория не удалена."))


# Edit an selected by id note
@bot_dispatcher.callback_query(NotesCallbackData.filter(F.action == 'edit_note'))
async def edit_note(
        callback: types.CallbackQuery,
        callback_data: NotesCallbackData,
        state: FSMContext,
        note_change_options
        ):
    await state.set_state(NoteChangeSteps.select_change_option)
    note = CB.GetNote(callback_data.id)
    await state.update_data(note_id=callback_data.id)
    # Build up an keyboard for 'note_change_options'
    builder = await BuildSearchOtherMenu(note_change_options, None)
    for view in CB.NoteFullView([note]):
        await callback.message.answer(_("{msg}").format(msg=view['msg']))
    await callback.message.answer(_("Выбери поле, которое будешь редактировать."), reply_markup=builder.as_markup(resize_keyboard=True))


# Set specific state, change keyboard and prepare for user query
##  F.text.in_(StringsMiddleware.note_change_options.keys())
@bot_dispatcher.message(StringsInFilter(option_key="note_change_options"))
async def edit_note_handler(message: Message, state: FSMContext, note_change_options):
    for option in note_change_options:
        if option == message.text:
            # Update a state for handlinq user query
            await state.set_state(NoteChangeSteps.changing)
            # Save selected field
            await state.update_data(note_field=note_change_options[option]['field'])
    builder = await BuildSearchOtherMenu(note_change_options, message.text)
    await message.answer(_("Теперь введи новое значение"), reply_markup=builder.as_markup(resize_keyboard=True))


# Handle user query and edit record
@bot_dispatcher.message(
        StateFilter(NoteChangeSteps.changing),
        StringsNotInFilter(option_key="note_change_options"),
        #F.text.not_in(StringsMiddleware.note_change_options.keys()),
        F.text != __('« Назад'))
async def edit_note_field_handler(message: Message, state: FSMContext, note_change_options):
    # Get note and change it
    data = await state.get_data()
    note_id = data['note_id']
    note_field = data['note_field']
    CB.ChangeNote(note_id, note_field, message.text)
    # Update state to be able change other fields
    await state.set_state(NoteChangeSteps.select_change_option)
    # Build up a keyboard, without selection
    builder = await BuildSearchOtherMenu(note_change_options, None)
    # Send a message
    await message.answer(_("Заметка изменена."), reply_markup=builder.as_markup(resize_keyboard=True))


# Handle edit inline button for record of type category or subcategory
@bot_dispatcher.callback_query(NotesCallbackData.filter(F.action == 'edit_category'))
async def edit_category(
        callback: types.CallbackQuery,
        callback_data: NotesCallbackData,
        state: FSMContext
        ):
    await state.set_state(NoteChangeSteps.changing_category)
    await state.update_data(prev_field_value=callback.message.text)
    await callback.message.answer(_("Теперь введи новое значение"))


# Handle user input query and change all notes by selected field
@bot_dispatcher.message(StateFilter(NoteChangeSteps.changing_category))
async def edit_category_field_handler(message: Message, state: FSMContext, search_options, other_options):
    # Change notes by selected fields
    data = await state.get_data()
    note_field = data['field']
    prev_note_field_value = data['prev_field_value']
    CB.ChangeNotesBy(prev_note_field_value, note_field, message.text, str(message.from_user.id))
    # Set state to get back to search menu
    await state.set_state(Search.start_search)
    # Build up a keyboard
    builder = await BuildSearchMenu(list(search_options.keys())[0], search_options, other_options)
    # Send a message back
    await message.answer(_("(Под)категория изменена."), reply_markup=builder.as_markup(resize_keyboard=True))


# To handle /settings command
@bot_dispatcher.message(Command('settings'))
@bot_dispatcher.message(StateFilter(Search.start_search), F.text == __("Настройки"))
async def command_settings(message: Message, state: FSMContext, search_options, order_options, note_preview_options) -> None:
    await InitDefaults(state, search_options, order_options, note_preview_options)
    # Update state
    await state.set_state(Search.setup_search)
    # Build up keyboard
    builder = await BuildSettingsMenu(state)
    await message.answer(_('Настройки поиска'), reply_markup=builder.as_markup())


# Handler to change how many notes gonna be displayed at once
@bot_dispatcher.message(StateFilter(Search.setup_search), F.text.startswith('Количество: По ') & F.text.endswith(' за раз'))
@bot_dispatcher.message(StateFilter(Search.setup_search), F.text.startswith('Number: From ') & F.text.endswith(' per page'))
async def settings_increase_note_number(message: Message, state: FSMContext) -> None:
    # Increase number for 1 untill 10 is reached
    data = await state.get_data()
    note_num = data['notes_number']
    note_num += 1
    if note_num > 10:
        note_num = 2
    # Update note_num in state storage
    await state.update_data(notes_number=note_num)
    # Build up keyboard
    builder = await BuildSettingsMenu(state)
    await message.answer(_('Увеличил количество отображаемых заметок за раз.'), reply_markup=builder.as_markup())


# Handler to change an order of displayed notes
# TODO ,
@bot_dispatcher.message(StateFilter(Search.setup_search), F.text.contains("С самых ранних")) 
@bot_dispatcher.message(StateFilter(Search.setup_search), F.text.contains("С самых поздних")) 
@bot_dispatcher.message(StateFilter(Search.setup_search), F.text.contains("Earliest first")) 
@bot_dispatcher.message(StateFilter(Search.setup_search), F.text.contains("Latest first")) 
async def settings_by_order(message: Message, state: FSMContext, order_options) -> None:
    # Find neede keyword i settings keyboard options.
    # In this case it is sended by user text
    option = message.text[message.text.find(':') + 2:]
    # Get next order  option
    next_option = None
    temp = iter(order_options)
    for key in temp:
        if key == option:
            next_option = next(temp, None)
    if next_option is None:
        next_option = list(order_options.keys())[0]
    # Update an order in which notes gonna appear
    await state.update_data(current_order_option=next_option)
    # Build up keyboard
    builder = await BuildSettingsMenu(state)
    await message.answer(_('Изменил порядок вывода заметок'), reply_markup=builder.as_markup())


# Handler to change an previews of notes
@bot_dispatcher.message(StateFilter(Search.setup_search), F.text.startswith('Заметки: '))
@bot_dispatcher.message(StateFilter(Search.setup_search), F.text.startswith('Notes: '))
async def settings_note_preview(message: Message, state: FSMContext, note_preview_options, search_options, other_search_options) -> None:
    # Update state
    await state.set_state(Search.setup_search)
    # Get current previewer option
    data = await state.get_data()
    option = data['current_note_preview_option']
    # Get next previewer option
    next_option = None
    temp = iter(note_preview_options)
    for key in temp:
        if key == option:
            next_option = next(temp, None)
    if next_option is None:
        next_option = list(note_preview_options.keys())[0]

    # Change viewers for volatile commands and handlers
    lk = StringsMiddleware(message.from_user.id)
    for key in lk.search_options:
        if lk.search_options[key]['volatile']:
            lk.search_options[key]['viewer'] = lk.note_preview_options[next_option]

    # Change viewers for volatile commands and handlers
    for key in lk.other_search_options:
        if lk.other_search_options[key]['volatile']:
            lk.other_search_options[key]['viewer'] = lk.note_preview_options[next_option]

    # Update an order in which notes gonna appear
    await state.update_data(current_note_preview_option=next_option)
    # Build up keyboard
    builder = await BuildSettingsMenu(state)
    await message.answer(_('Отображение заметок измененно.'), reply_markup=builder.as_markup())


# Handle /add command. Add new notes to database
@bot_dispatcher.message(Command('add'))
@bot_dispatcher.message(F.text == __('Добавить новую'))
async def command_add_note(message: Message, state: FSMContext, search_options, order_options, note_preview_options) -> None:
    await InitDefaults(state, search_options, order_options, note_preview_options)
    # Init more default values
    await state.update_data(id="0_0")
    await state.update_data(text=None)
    await state.update_data(title=None)
    await state.update_data(category=None)
    await state.update_data(subcategory=None)
    await state.set_state(NoteSteps.text)
    # Build up keyboard
    builder = await BuildAddProccessMenu([_('Отменить добавление')])
    await message.answer(
            _("Введи текст заметки"),
            reply_markup=builder.as_markup(resize_keyboard=True))


# Handle user query to save it as text
@bot_dispatcher.message(
        StateFilter(NoteSteps.text),
        F.text != __('Отменить добавление'),
        F.text != __('Предыдущий шаг'),
        F.text != __('Пропустить'),
        F.text != __('Сохранить как есть'))
async def set_text(message: Message, state: FSMContext):
    # Save data
    await state.update_data(text=message.text)
    # Build up keyboard
    builder = await BuildAddProccessMenu([
        _('Отменить добавление'),
        _('Предыдущий шаг'),
        _('Пропустить'),
        _('Сохранить как есть')
    ])
    await state.set_state(NoteSteps.title)
    await message.answer(_("Введи заголовок"), reply_markup=builder.as_markup(resize_keyboard=True))


# Handle user query to save it as title
@bot_dispatcher.message(
        StateFilter(NoteSteps.title),
        F.text != __('Отменить добавление'),
        F.text != __('Предыдущий шаг'),
        F.text != __('Пропустить'),
        F.text != __('Сохранить как есть'))
async def set_title(message: Message, state: FSMContext):
    # Save data
    await state.update_data(title=message.text)
    # Build up keyboard
    builder = await BuildAddProccessMenu([
        _('Отменить добавление'),
        _('Предыдущий шаг'),
        _('Пропустить'),
        _('Сохранить как есть')
    ])
    await state.set_state(NoteSteps.category)
    await message.answer(
            _("Введи название категории"),
            reply_markup=builder.as_markup(resize_keyboard=True))


# Handle user query to save it as category
@bot_dispatcher.message(
        StateFilter(NoteSteps.category),
        F.text != __('Отменить добавление'),
        F.text != __('Предыдущий шаг'),
        F.text != __('Пропустить'),
        F.text != __('Сохранить как есть'))
async def set_category(message: Message, state: FSMContext):
    # Save data
    await state.update_data(category=message.text)
    # Build up keyboard
    builder = await BuildAddProccessMenu([
        _('Отменить добавление'),
        _('Предыдущий шаг'),
        _('Пропустить'),
        _('Сохранить как есть')
    ])
    await state.set_state(NoteSteps.subcategory)
    await message.answer(
            _("Введи название подкатегории"),
            reply_markup=builder.as_markup(resize_keyboard=True))


# Handle user query to save it as subcategory
@bot_dispatcher.message(
        StateFilter(NoteSteps.subcategory),
        F.text != __('Отменить добавление'),
        F.text != __('Предыдущий шаг'),
        F.text != __('Пропустить'),
        F.text != __('Сохранить как есть'))
async def set_subcategory(message: Message, state: FSMContext):
    await state.update_data(subcategory=message.text)
    await state.set_state(None)
    builder = await BuildAddProccessMenu([
        _('Отменить добавление'),
        _('Показать результат'),
        _('Сохранить как есть')
    ])
    await message.answer(
            _("Создание заметки закончено. Не забудь сохранить её."),
            reply_markup=builder.as_markup(resize_keyboard=True))


# Display result note to user
@bot_dispatcher.message(
        StateFilter(None),
        F.text == __('Показать результат'))
async def command_show_result_note(message: Message, state: FSMContext, note_preview_options):
    data = await state.get_data()
    option = data['current_note_preview_option']
    note_data = await state.get_data()
    for view in note_preview_options[option]([note_data]):
        await message.answer(_("{view}").format(view=view['msg']))


# Handle cancel command
@bot_dispatcher.message(F.text == __('Отменить добавление'))
async def command_cancel(message: Message, state: FSMContext):
    # Clear state data
    await state.clear()
    # Build up a main meun keyboard
    builder = await BuildMainMenu()
    await message.answer(
        text=_("Создание новой заметки отменено."),
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


# Handle skip command
@bot_dispatcher.message(F.text == __('Пропустить'))
async def command_skip(message: Message, state: FSMContext):
    match await state.get_state():
        case NoteSteps.text:
            pass
        case NoteSteps.title:
            await state.set_state(NoteSteps.category)
            await message.answer(text=_("Шаг пропущен."),)
            await message.answer(text=_("Введи название категории"),)
        case NoteSteps.category:
            await state.set_state(NoteSteps.subcategory)
            await message.answer(text=_("Шаг пропущен."),)
            await message.answer(text=_("Введи название подкатегории"),)
        case NoteSteps.subcategory:
            builder = await BuildAddProccessMenu([
                _('Отменить добавление'),
                _('Показать результат'),
                _('Сохранить как есть')
            ])
            await state.set_state(None)
            await message.answer(text=_("Шаг пропущен."),)
            await message.answer(
                    text=_("Создание заметки закончено. Не забудь сохранить её."),
                    reply_markup=builder.as_markup(resize_keyboard=True))


# Handle back command.
# Behaviour depends on current state
@bot_dispatcher.message(F.text == __('Предыдущий шаг'))
@bot_dispatcher.message(F.text == __('« Назад'))
async def command_back(message: Message, state: FSMContext, search_options, other_options):
    match await state.get_state():
        case NoteSteps.text:
            await state.clear()
            # Build up keyboard
            builder = await BuildMainMenu()
            # Send a message
            await message.answer(
                text=_("Создание новой заметки отменено."),
                reply_markup=builder.as_markup(resize_keyboard=True)
            )
        case NoteSteps.title:
            await state.set_state(NoteSteps.text)
            # Build up keyboard
            builder = await BuildAddProccessMenu([
                _('Отменить добавление')
            ])
            # Send a message
            await message.answer(
                text=_("Введи текст заметки"),
                reply_markup=builder.as_markup(resize_keyboard=True)
            )
        case NoteSteps.category:
            await state.set_state(NoteSteps.title)
            # Build up keyboard
            builder = await BuildAddProccessMenu([
                _('Отменить добавление'),
                _('Предыдущий шаг'),
                _('Пропустить'),
                _('Сохранить как есть')
            ])
            # Send a message
            await message.answer(
                text=_("Введи заголовок"),
                reply_markup=builder.as_markup(resize_keyboard=True)
            )
        case NoteSteps.subcategory:
            await state.set_state(NoteSteps.category)
            # Build up keyboard
            builder = await BuildAddProccessMenu([
                _('Отменить добавление'),
                _('Предыдущий шаг'),
                _('Пропустить'),
                _('Сохранить как есть')
            ])
            # Send a message
            await message.answer(
                text=_("Введи название категории"),
                reply_markup=builder.as_markup(resize_keyboard=True)
            )
        case Search.start_search:
            await state.set_state(None)
            # Build up keyboard
            builder = await BuildMainMenu()
            # Send a message
            await message.answer(
                text=_("Вернулся в главное меню"),
                reply_markup=builder.as_markup(resize_keyboard=True)
            )
        case Search.setup_search:
            await state.set_state(Search.start_search)
            current_search_option = list(search_options.keys())[0]
            await state.update_data(current_search_option=current_search_option)
            # Build up keyboard
            builder = await BuildSearchMenu(current_search_option, search_options, other_options)
            # Send a message
            await message.answer(
                text=_("Вернулся в меню поиска заметок"),
                reply_markup=builder.as_markup(resize_keyboard=True)
            )
        case NoteChangeSteps.select_change_option | NoteChangeSteps.changing:
            await state.set_state(Search.start_search)
            current_search_option = list(search_options.keys())[0]
            await state.update_data(current_search_option=current_search_option)
            # Build up keyboard
            builder = await BuildSearchMenu(search_options, search_options, other_options)
            # Send a message
            await message.answer(
                text=_("Вернулся в меню поиска заметок"),
                reply_markup=builder.as_markup(resize_keyboard=True)
            )

    await message.answer(text=_("Возвращение на шаг назад."))


# Save created note
@bot_dispatcher.message(F.text == __('Сохранить как есть'))
async def command_save(message: Message, state: FSMContext):
    note_data = await state.get_data()
    # Get an user id to attach to note record
    note_data['user_id'] = str(message.from_user.id)
    # Convert note_data to Note class object
    note = Note(note_data)
    # Save note to database
    manager = DataManagerLocal(FILE_PATH)
    manager.save(note)
    # Build up a main meun keyboard
    builder = await BuildMainMenu()
    # Clear state storage
    await state.clear()
    await message.answer(
        text=_("Заметка сохранена"),
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


async def main() -> None:
    bot_dispatcher.update.outer_middleware(StringsMiddleware(None))
    await bot_dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
