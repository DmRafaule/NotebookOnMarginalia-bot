import os
import json
import uuid
from datetime import datetime


class Note:
    user_id = str
    id = str
    time_created = str
    title = str
    text = str
    category = str
    subcategory = str

    def __init__(self, data: dict):
        key = 'user_id'
        if key in data and data[key] is not None:
            self.user_id = data[key]
        else:
            self.user_id = None
        key = 'id'
        if key in data and data[key] != '0_0':
            self.id = data[key]
        else:
            self.id = uuid.uuid1().hex
        key = 'time_created'
        if key in data and data[key] is not None:
            self.time_created = data[key]
        else:
            self.time_created = str(datetime.now())
        key = 'title'
        if key in data and data[key] is not None:
            self.title = data[key]
        else:
            self.title = None
        key = 'text'
        if key in data and data[key] is not None:
            self.text = data[key]
        else:
            self.text = None
        key = 'category'
        if key in data and data[key] is not None:
            self.category = data[key]
        else:
            self.category = None
        key = 'subcategory'
        if key in data and data[key] is not None:
            self.subcategory = data[key]
        else:
            self.subcategory = None


class DataManager:
    _instance = None
    path = str
    data = None

    def __new__(self, dataFileName, dataFilePreset=[]):
        if self._instance is None:
            self._instance = super(DataManager, self).__new__(self)
            self.path = dataFileName
            self.data = dataFilePreset
            if not os.path.exists(dataFileName):
                with open(dataFileName, "w", encoding="utf-8") as F:
                    json.dump(dataFilePreset, F, indent=2)
            else:
                self.load(self)
        return self._instance

    def save(self, note: Note) -> None:
        with open(self.path, "r", encoding="utf-8") as F:
            self.data = json.load(F)

            self.data.append({
                'user_id': note.user_id,
                'id': note.id,
                'time_created': note.time_created,
                'category': note.category,
                'subcategory': note.subcategory,
                'title': note.title,
                'text': note.text,
            })
        with open(self.path, "w", encoding="utf-8") as F:
            json.dump(self.data, F, indent=2)

    def load(self) -> list:
        with open(self.path, "r", encoding="utf-8") as F:
            self.data = json.load(F)
        return self.data

    # Used for updating data in memory (temporarly) database
    def update(self, new_data: list) -> None:
        self.data = new_data

    # Used for updating database on hard drive (replace by data in memory)
    def updateDataBase(self) -> None:
        with open(self.path, "w", encoding="utf-8") as F:
            json.dump(self.data, F, indent=2)


class DataManagerLocal:
    path = str
    data = None

    def __init__(self, dataFileName, dataFilePreset=[]):
        self.path = dataFileName
        self.data = dataFilePreset
        if not os.path.exists(dataFileName):
            with open(dataFileName, "w", encoding="utf-8") as F:
                json.dump(dataFilePreset, F, indent=2)
        else:
            self.load()

    def save(self, note: Note) -> None:
        with open(self.path, "r", encoding="utf-8") as F:
            self.data = json.load(F)

            self.data.append({
                'user_id': note.user_id,
                'id': note.id,
                'time_created': note.time_created,
                'category': note.category,
                'subcategory': note.subcategory,
                'title': note.title,
                'text': note.text,
            })
        with open(self.path, "w", encoding="utf-8") as F:
            json.dump(self.data, F, indent=2)

    def load(self) -> list:
        with open(self.path, "r", encoding="utf-8") as F:
            self.data = json.load(F)
        return self.data

    # Used for updating data in memory (temporarly) database
    def update(self, new_data: list) -> None:
        self.data = new_data

    # Used for updating database on hard drive (replace by data in memory)
    def updateDataBase(self) -> None:
        with open(self.path, "w", encoding="utf-8") as F:
            json.dump(self.data, F, indent=2)
