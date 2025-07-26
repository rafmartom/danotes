from ..model.core import *

def block_write(path, buid=None, query=None, new_label=None, json=False, text=False):
    """Write a determined Dan Block Object. 
    If not target Block given write on next <buid>.
    If target Block already exists will append text to it
    If target Block doesnt exist give an error
    """
    print(f"Writing {json=} {text=} {buid=} {path=} {query=} {new_label=} ")

    if not is_valid_dan_format(path):
        raise ValueError(f"{path} Invalid file type. Expected .dan syntax within. If the path is correct you may want to fix it")

    danom = parse_danom(path)

    ## Assign next buid if not given
    if not buid:
        buid = get_next_available_buid(danom)
        if not new_label:
            new_label = "Unnamed Article"
        create_new_block(danom, buid, new_label) 
        write_danom(danom,path)
        return buid
        
    else:
        if not get_block_by_buid(danom, buid):
            raise ValueError(f"{buid=} does not exists within the file. What Block do you want to append text to?")

        

              #    if text:
              #        print(block.get_content())
              #        return
              #    else:
              #        print(block.to_json())



def block_show(path, buid=None, label=None, json=False, text=False):
    """Show and update a determined Dan Block Object
    If no --json and --text are given. Update in place the determined block
    If no --buid or --label are given. Show all the document from buid=0 to last
    """
    print(f"Showing {json=} {text=} {buid=} {label=} {path=}")

    if not is_valid_dan_format(path):
        raise ValueError(f"{path} Invalid file type. Expected .dan syntax within. If the path is correct you may want to fix it")

    danom = parse_danom(path)


    if not label and not buid:
        if json:
            return danom_to_json(danom)
        elif text:
            return render_danom(danom)
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
