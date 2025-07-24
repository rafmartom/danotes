from ..model.core import *

def block_write(path, buid, query, label, json, text):
    """Write a determined Dan Block Object. 
    If not target Block given write on next <buid>.
    If target Block already exists will append text to it"""
    print(f"Writing {json=} {text=} {buid=} {path=} {query=} {label=} ")


def block_show(path, buid, label, json, text):
    """Show and update a determined Dan Block Object
    If no --json and --text are given. Update in place the determined block
    If no --buid or --label are given. Show all the document from buid=0 to last
    """
    print(f"Showing {json=} {text=} {buid=} {label=} {path=}")

    danom = parse_danom(path)


    if not label and not buid:
        if json:
            print(danom_to_json(danom))
            return
        elif text:
            for block in danom:
                print(block.get_content())
                print('=' * 105)
            return
        else:
            print(danom_to_json(danom))
            return
    if label:
        block = get_block_by_label(danom, label)
    else:
        block = get_block_by_buid(danom, buid)
    if text:
        print(block.get_content())
        return
    else:
        print(block.to_json())






#    block_update(path, buid, label, json, text)
#
#    match (buid, label, json, text):
#        case (None, None, _, _):
#            block_update_all()
#        case (None, None, True, False):
#            block_show_all(json=True)
#        case (None, None, False, True):
#            block_show_all(text=True)
#        case (buid, None, _, _):
#            block_update(buid)
#        case (None, None, True, False):
#            block_show_all(json=True)
#        case (None, None, False, True):
#            block_show_all(text=True)
#
#        case (buid, None, _, _):
#        case _:
#            raise ValueError("Unexpected parameters received")
#    if buid:
#
#        block_
#    elif not buid:
#    else:
