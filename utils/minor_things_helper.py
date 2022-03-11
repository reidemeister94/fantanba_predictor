def fix_name(dunkest_bot, name):
    name = name.lower().strip().replace(".", "").replace("\"", "")
    name_ = name.split(" ")
    if len(name_) == 1 and name != "nene":
        return name.lower()
    if name_[-1].lower() == "edrice":
        name_[-1] = "bam"
    if name == "neto raul":
        return "raulzinho neto"
    if name == "porter jr otto":
        return "otto porter"
    if name == "nance jr larry":
        return "larry nance"
    if name == "mbah a moute luc":
        return "luc richard mbah a moute"
    if name_[-1].lower() == "malcom":
        name_[-1] = "malcolm"
    if len(name_) > 1:
        name = name_[-1].lower() + " "
        for i in range(0, len(name_) - 1):
            name += name_[i].lower()
            if i < len(name_) - 2:
                name += " "
    return name


def fix_sisal_name_teams(dunkest_bot, teams_string):
    teams_string_list = teams_string.lower().split("-")
    teams_string_list[0] = teams_string_list[0].strip()
    teams_string_list[1] = teams_string_list[1].strip()
    return (teams_string_list[0], teams_string_list[1])


def compute_position(role_tag):
    if role_tag == "GUARD":
        return "G"
    elif role_tag == "FORWARD":
        return "A"
    elif role_tag == "CENTER":
        return "C"
    elif role_tag == "COACH":
        return "HC"
