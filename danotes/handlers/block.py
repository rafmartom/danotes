from ..model.core import *

def block_write(path, buid, query, label, json, text):
    """Write a determined Dan Block Object. 
    If not target Block given write on next <buid>.
    If target Block already exists will append text to it"""
    print(f"Writing {json=} {text=} {buid=} {path=} {query=} {label=} ")


def block_show(path, buid=None, label=None, json=False, text=False):
    """Show and update a determined Dan Block Object
    If no --json and --text are given. Update in place the determined block
    If no --buid or --label are given. Show all the document from buid=0 to last
    """
    print(f"Showing {json=} {text=} {buid=} {label=} {path=}")

    danom = parse_danom(path)


    if not label and not buid:
        if json:
            return danom_to_json(danom)
        elif text:
            output = []
            for block in danom:
                output.append(block.get_content())
                output.append('=' * 105)
            return '\n'.join(output)
        else:
            return 
    if label:
        block = get_block_by_label(danom, label)
    else:
        block = get_block_by_buid(danom, buid)
    if json:
        return block.to_json()
    elif text:
        return block.get_content()
    else:
        return 






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
