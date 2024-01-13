from NotebookMarginalia.data_manager.manager import DataManagerLocal
from config import FILE_PATH
from operator import itemgetter
from datetime import datetime
from aiogram.utils.i18n import gettext as _
from config import i18n_handler


def GetAllNotes(args) -> []:
    user_id = str(args["user_id"])
    order = args["order"]
    dm = DataManagerLocal(FILE_PATH)
    result = []
    # Get all related to user notes
    for record in dm.data:
        if record['user_id'] == user_id:
            result.append(record)

    match order:
        case "С самых ранних":
            result = sorted(result, key=itemgetter("time_created"), reverse=False)
        case "С самых поздних":
            result = sorted(result, key=itemgetter("time_created"), reverse=True)

    return result


def GetAllCategories(args) -> []:
    user_id = str(args["user_id"])
    dm = DataManagerLocal(FILE_PATH)
    result = []
    # Get all related to user notes
    for record in dm.data:
        if record['user_id'] == user_id and record['category'] is not None:
            result.append(record['category'])

    result = list(set(result))

    return result


def GetAllSubcategoriesOfCategory(args) -> []:
    user_id = str(args["user_id"])
    category_name = args['query']
    dm = DataManagerLocal(FILE_PATH)
    subcategories = []
    for record in dm.data:
        if record['user_id'] == user_id:
            if record['subcategory'] is not None and record['category'] is not None:
                if record['category'] == category_name:
                    subcategories.append(record['subcategory'])
    subcategories = list(set(subcategories))

    return subcategories


def GetAllNotesAfterPeriod(args) -> []:
    period = args['query']
    user_id = str(args["user_id"])
    date = datetime.strptime(period, "%Y-%m-%d")
    date = date.strftime("%Y-%m-%d")
    dm = DataManagerLocal(FILE_PATH)
    result = []
    for record in dm.data:
        if record['user_id'] == user_id:
            date_created = datetime.strptime(record['time_created'], "%Y-%m-%d %H:%M:%S.%f")
            date_created = date_created.strftime("%Y-%m-%d")
            if date_created >= date:
                result.append(record)

    return result


def GetAllNotesBeforePeriod(args) -> []:
    period = args['query']
    user_id = str(args["user_id"])
    date = datetime.strptime(period, "%Y-%m-%d")
    date = date.strftime("%Y-%m-%d")
    dm = DataManagerLocal(FILE_PATH)
    result = []
    for record in dm.data:
        if record['user_id'] == user_id:
            date_created = datetime.strptime(record['time_created'], "%Y-%m-%d %H:%M:%S.%f")
            date_created = date_created.strftime("%Y-%m-%d")
            if date_created <= date:
                result.append(record)

    return result


def GetAllNotesForToday(args) -> []:
    user_id = str(args["user_id"])
    date = datetime.today()
    date = date.strftime("%Y-%m-%d")
    dm = DataManagerLocal(FILE_PATH)
    result = []
    for record in dm.data:
        if record['user_id'] == user_id:
            date_created = datetime.strptime(record['time_created'], "%Y-%m-%d %H:%M:%S.%f")
            date_created = date_created.strftime("%Y-%m-%d")
            if date_created == date:
                result.append(record)

    return result


def GetNotes(args) -> []:
    query = args["query"]
    user_id = str(args["user_id"])
    notes_number = int(args["notes_number"])
    where = args["where"]
    order = args["order"]
    view = args["view"]
    dm = DataManagerLocal(FILE_PATH)
    result = []
    # Get all related to user notes
    for record in dm.data:
        if record['user_id'] == user_id:
            result.append(record)
    buff = []
    keys = []
    # Set up keys to check
    match where:
        case "Искать везде" | "Search everywhere":
            keys.append('title')
            keys.append('text')
            keys.append('category')
            keys.append('subcategory')
        case "Искать по заголовку" | "Search by title":
            keys.append('title')
        case "Искать по содержимому" | "Search by text":
            keys.append('text')
        case "Искать по категориям" | "Search by category":
            keys.append('category')
        case "Искать по подкатегориям" | "Search by subcategory":
            keys.append('subcategory')
    # Loop through each user note
    for record in result:
        # Loop through each key in note dict
        for key in record:
            # If value of key-value pair not None and if key was requested by user
            if record[key] is not None and key in keys:
                # If query is present in requested key-value pair
                if record[key].find(query) != -1:
                    buff.append(record)
    # Remove duplicates
    buff = {frozenset(item.items()):
            item for item in buff}.values()
    result = buff

    match order:
        case "С самых ранних" | "Earliest first":
            result = sorted(result, key=itemgetter("time_created"), reverse=False)
        case "С самых поздних" | "Latest first":
            result = sorted(result, key=itemgetter("time_created"), reverse=True)

    return result


def GetNote(id: str) -> {}:
    note = None
    dm = DataManagerLocal(FILE_PATH)
    for record in dm.data:
        if record['id'] == id:
            note = record
            break
    return note


def RemoveNote(id: str):
    status = False
    dm = DataManagerLocal(FILE_PATH)
    for record in dm.data:
        if record['id'] == id:
            dm.data.remove(record)
            status = True
            break
    dm.updateDataBase()
    return status


def RemoveBy(prev_field_value: str, field: str, user_id: str):
    status = False
    dm = DataManagerLocal(FILE_PATH)
    for record in dm.data:
        if record['user_id'] == user_id:
            if record[field] == prev_field_value:
                status = True
                dm.data.remove(record)
    dm.updateDataBase()
    return status


def ChangeNote(id: str, field: str, new_data: str):
    dm = DataManagerLocal(FILE_PATH)
    for record in dm.data:
        if record['id'] == id:
            record[field] = new_data
            break
    dm.updateDataBase()


def ChangeNotesBy(prev_field_value: str, field: str, new_data: str, user_id: str):
    dm = DataManagerLocal(FILE_PATH)
    for record in dm.data:
        if record['user_id'] == user_id:
            if record[field] == prev_field_value:
                record[field] = new_data
    dm.updateDataBase()


def NoteFullView(data_list: []) -> []:
    result = []
    for data in data_list:
        text_str = f"{data['text']}"
        date_str = f"<b>DATE</b>:\t{data['time_created']}\n"
        id_str = f"<b>ID</b>:\t{data['id']}\n"
        title_str = _("БЕЗ НАЗВАНИЯ\n")
        if data['title'] is not None:
            title_str = f"<b>TITLE</b>:\t<u><b>{data['title']}</b></u>\n"
        category_str = _("БЕЗ КАТЕГОРИИ\n")
        if data['category'] is not None:
            category_str = f"<b>CAT</b>:\t{data['category']}\n"
        subcategory_str = _("БЕЗ ПОДКАТЕГОРИИ\n")
        if data['subcategory'] is not None:
            subcategory_str = f"<b>SCAT</b>:\t{data['subcategory']}\n"
        result.append({'msg': f"{id_str}{date_str}\n{title_str}{category_str}{subcategory_str}\n{text_str}", 'id': data['id']})

    return result


def NoteNesessaryView(data_list: []) -> []:
    result = []
    for data in data_list:
        text_str = f"{data['text']}"
        title_str = _("БЕЗ НАЗВАНИЯ\n")
        if data['title'] is not None:
            title_str = f"<b>TITLE</b>:\t<u><b>{data['title']}</b></u>\n"
        category_str = _("БЕЗ КАТЕГОРИИ\n")
        if data['category'] is not None:
            category_str = f"<b>CAT</b>:\t{data['category']}\n"
        subcategory_str = _("БЕЗ ПОДКАТЕГОРИИ\n")
        if data['subcategory'] is not None:
            subcategory_str = f"<b>SCAT</b>:\t{data['subcategory']}\n"
        result.append({'msg': f"{title_str}{category_str}{subcategory_str}\n{text_str}", 'id': data['id']})

    return result


def NoteMinimalView(data_list: []) -> []:
    result = []
    for data in data_list:
        text_str = f"{data['text']}"
        title_str = _("БЕЗ НАЗВАНИЯ\n")
        if data['title'] is not None:
            title_str = f"<u><b>{data['title']}</b></u>\n"
        result.append({'msg': f"{title_str}\n{text_str}", 'id': data['id']})

    return result


def NoteAllPossibleView(data_list: []) -> []:
    result = []
    for data in data_list:
        text_str = f"{data['text']}"
        date_str = f"<b>DATE</b>:\t{data['time_created']}\n"
        id_str = f"<b>ID</b>:\t{data['id']}\n"
        title_str = ""
        if data['title'] is not None:
            title_str = f"<b>TITLE</b>:\t<u><b>{data['title']}</b></u>\n"
        category_str = ""
        if data['category'] is not None:
            category_str = f"<b>CAT</b>:\t{data['category']}\n"
        subcategory_str = ""
        if data['subcategory'] is not None:
            subcategory_str = f"<b>SCAT</b>:\t{data['subcategory']}\n"
        result.append({'msg': f"{id_str}{date_str}{title_str}{category_str}{subcategory_str}\n{text_str}", 'id': data['id']})

    return result


def SimpleListView(data_list: []):
    result = []
    for data in data_list:
        result.append({'msg': data, 'id': None})
    return result
