class ViewManager:
    _instance = None
    callback = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(ViewManager, self).__new__(self)
            self.callback = self._viewFull
        return self._instance

    def set(self, callback):
        self.callback = callback

    def view(self, obj):
        return self.callback(obj)

    def _viewOnlyIDs(self, obj) -> str:
        id_str = ""
        if obj.id:
            id_str = f"{obj.id}"
        res = f"ID:{id_str}"
        return res

    def _viewTitleWithText(self, obj) -> str:
        title_str = ""
        if obj.title:
            title_str = f" {obj.title} "
        text_str = ""
        if obj.text:
            text_str = f"""{obj.text}"""

        res = f"""
==========={title_str}===========

{text_str}

================================="""
        return res

    def _viewOnlyTitles(self, obj) -> str:
        title_str = ""
        if obj.title:
            title_str = f" {obj.title} "
        res = f"TITLE:'{title_str}'"
        return res

    def _viewTitleTextCategorySubcategory(self, obj) -> str:
        title_str = ""
        if obj.title:
            title_str = f" {obj.title} "
        category_str = ""
        if obj.category:
            category_str = f"\nCAT:{obj.category}"
        subcategory_str = ""
        if obj.subcategory:
            subcategory_str = f"\nSCAT:{obj.subcategory}"
        text_str = ""
        if obj.text:
            text_str = f"""TXT:\n{obj.text}"""
        
        res = f"""
==========={title_str}===========
{category_str}{subcategory_str}

{text_str}

================================="""
        return res

    def _viewFull(self, obj) -> str:
        id_str = ""
        if obj.id:
            id_str = f"\nID:{obj.id}"
        title_str = ""
        if obj.title:
            title_str = f" {obj.title} "
        category_str = ""
        if obj.category:
            category_str = f"\nCAT:{obj.category}"
        subcategory_str = ""
        if obj.subcategory:
            subcategory_str = f"\nSCAT:{obj.subcategory}"
        time_str = ""
        if obj.time_created:
            time_str = f"\nCREATED:{obj.time_created}"
        text_str = ""
        if obj.text:
            text_str = f"""TXT:\n{obj.text}"""
        
        res = f"""
==========={title_str}==========={id_str}
{category_str}{subcategory_str}{time_str}

{text_str}

================================="""
        return res
