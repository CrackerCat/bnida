import idc
import idautils
import idaapi
import json

def sanitize_name(name):
    """Remove characters from BN names that IDA doesn't like
    """
    name = name.replace("!", "_")
    name = name.replace("@", "_")
    return name

def import_comments(comments):
    """Import BN comments
    """
    for addr, comment in comments.items():
        addr = int(addr)
        comment = comment.encode("utf-8")
        current_comment = idc.Comment(addr)

        # make a new comment
        if not current_comment:
            idc.MakeComm(addr, comment)
            continue

        # ensure comments hasn't already been imported
        if comment in current_comment:
            continue

        # append to comment
        idc.MakeComm(addr, current_comment + " " + comment)

def import_symbols(names):
    """Import BN symbol names
    """
    for addr, name in names.items():
        addr = int(addr)
        name = sanitize_name(name).encode("utf-8")
        idc.MakeName(addr, name)

def get_json(json_file):
    """Read JSON data file
    """
    json_array = None
    if json_file is None:
        print("JSON file not specified")
        return json_array

    try:
        f = open(json_file, "rb")
        json_array = json.load(f)
    except Exception as e:
        print("Failed to parse json file {} {}".format(json_file, e))
    return json_array

def main(json_file):
    """Import data from BN
    """
    json_array = get_json(json_file)
    if not json_array:
        return

    import_symbols(json_array["names"])
    import_comments(json_array["comments"])

if __name__ == "__main__":
    main(idc.AskFile(1, "*.json", "Import file name"))
