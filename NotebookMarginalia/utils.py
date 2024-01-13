def categories_to_list(src: list) -> list:
    res = []
    for item in src:
        res += list(item.keys())
    return res


def subcategories_to_list(src: list) -> list:
    res = []
    for item in src:
        res += item.values()
    return sum(res, [])


def get_subcategories_of_category(key: str, categories) -> dict:
    res = []
    next(item for item in categories if item["name"] == "Pam")
    for cat in categories:
        print(list(cat.keys()))
        if key in list(cat.keys()):
            print(cat)
            res = cat.values()
    return res


def list_to_linestr(src: list) -> str:
    res = ""
    for item in src:
        res += item + ','
    return res
