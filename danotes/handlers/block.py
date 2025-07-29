from ..model.core import *

def block_write(path, buid=None, query=None, new_label=None, json=False, text=False):
    """Write a determined Dan Block Object. 
    If --new-label , it will create a New Block on the next available <buid>.
    If not --new-label , but --query , it will append on the last block
    If target Block already exists will append text to it
    If target Block doesnt exist give an error
    """
    print(f"Writing {json=} {text=} {buid=} {path=} {query=} {new_label=} ")

    if not is_valid_dan_format(path):
        raise ValueError(f"{path} Invalid file type. Expected .dan syntax within. If the path is correct you may want to fix it")

    danom = Danom()
    danom.load(path)


    ## Getting the block
    if buid:
        ## Block needs to exist
        if danom.get_block_by_buid(buid):
            block = danom.get_block_by_buid(buid)
        elif buid == '0' or buid == '1':
            raise ValueError(f"{buid=} 0 or 1 cannot be modified")
        else:
            raise ValueError(f"{buid=} does not exists within the file. What Block do you want to append text to?")
    ## If there is not buid create a new one
    elif not query:
        buid = danom.get_next_available_buid()
        block = danom.create_new_block(buid, new_label)
    ## If there is query but not buid get the last block
    else :
        block = danom[-1]

    ## If there is query append to the block
    if query:
        block.append_query(query)

    # Outputting info in the desired format
    if json:
        return block.to_json()
    elif text:
        return block.to_text()
    else:
        danom.to_file(path)
        return block.buid




def block_show(path, buid=None, label=None, json=False, text=False):
    """Show and update a determined Dan Block Object
    If no --json and --text are given. Update in place the determined block
    If no --buid or --label are given. Show all the document from buid=0 to last
    """
    print(f"Showing {json=} {text=} {buid=} {label=} {path=}")

    if not is_valid_dan_format(path):
        raise ValueError(f"{path} Invalid file type. Expected .dan syntax within. If the path is correct you may want to fix it")

    danom = Danom(path)
    danom.load(path)


    ## Selecting target by block or whole danom
    match (buid, label):
        case (None, None):
            target = danom
        case (buid, None) if buid is not None:  # Check buid is not None
            if danom.get_block_by_buid(buid):
                target = danom.get_block_by_buid(buid)
            else:
                raise ValueError(f"{buid=} does not exist.")
        case (None, label) if label is not None:  # Check label is not None
            if danom.get_block_by_label(label):
                target = danom.get_block_by_label(label)
            else:
                raise ValueError(f"{label=} does not exist.")
        case _:
            raise ValueError("Cannot specify both buid and label.")
            target = danom

    # Outputting info in the desired format
    if json:
        return target.to_json()
    elif text:
        return target.to_text()
    else:
        danom.to_file(path)
        return f"{path} danom has been successfully updated.\n"
