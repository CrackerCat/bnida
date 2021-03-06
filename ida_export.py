"""ida_export.py: exports IDA analysis data to a json file"""

__author__      = "zznop"
__copyright__   = "Copyright 2018, zznop0x90@gmail.com"
__license__     = "WTFPL"

import idc
import idautils
import json

def get_single_comment(ea, is_func=False):
    """IDA has repeatable and regular comments. BN only has regular comments.
    This function constructs a single comment from both repeatable and regular
    comments
    """
    regular_comment    = ""
    repeatable_comment = ""

    if is_func:
        regular_comment = idc.GetFunctionCmt(ea, 0)
        repeatable_comment = idc.GetFunctionCmt(ea, 1)
    else:
        regular_comment = idc.Comment(ea)
        repeatable_comment = idc.RptCmt(ea)

    if regular_comment is None:
        return repeatable_comment
    elif repeatable_comment is None:
        return regular_comment
    elif repeatable_comment is None and regular_comment is None:
        return None
    else:
        if len(regular_comment) == 0:
            return repeatable_comment

        if len(repeatable_comment) == 0:
            return repeatable_comment

        return regular_comment + "\n" + repeatable_comment

    return None

def get_symbols():
    """Get symbols from IDA database
    """
    symbols = {}
    for addr, name in idautils.Names():
        symbols[addr] = name

    return symbols

def get_sections():
    """Get section names and start/end addrs from IDA database
    """
    sections = {}
    for ea in idautils.Segments():
        curr = {}
        curr["start"] = idc.SegStart(ea)
        curr["end"]   = idc.SegEnd(ea)
        sections[idc.SegName(ea)] = curr

    return sections

def get_comments():
    """Get function and instruction comments from IDA database
    """
    comments = {}
    for ea in idautils.Functions():
        current_function = {}
        end = idc.GetFunctionAttr(ea, idc.FUNCATTR_END)
        current_function["comment"] = get_single_comment(ea, True)
        current_function["comments"] = {}
        for line_ea in idautils.Heads(ea, end):
            instr_comment = get_single_comment(line_ea)
            if instr_comment is not None:
                current_function["comments"][line_ea] = instr_comment
        comments[ea] = current_function

    return comments

def main(json_file):
    """Construct a json file containing analysis data from an IDA database
    """
    json_array = {}
    json_array["sections"] = get_sections()
    json_array["comments"] = get_comments()
    json_array["symbols"]  = get_symbols()

    with open(json_file, "wb") as f:
        f.write(json.dumps(json_array, indent=4))

if __name__ == '__main__':
    main(idc.AskFile(1, "*.json", "Export file name"))
