from ..model import *


def block_write(path, buid=None, query=None, new_label=None, source=None, json=False, text=False):
    """Write a determined Dan Block Object. 
    If --new-label , it will create a New Block on the next available <buid>.
    If not --new-label , but --query , it will append on the last block
    If target Block already exists will append text to it
    If target Block doesnt exist give an error
    If target Block --buid 1 , will update the Toc Block (General Toc)
    """
    print(f"Writing {json=} {text=} {buid=} {path=} {query=} {new_label=} {source=} ")

    if not is_valid_dan_format(path):
        raise ValueError(f"{path} Invalid file type. Expected .dan syntax within. If the path is correct you may want to fix it")

    danom = Danom()
    danom.load(path)
    danom.get_links_target()


    ## Adding the source for hierarchy
    if not source:
        source = None

    ## Getting the block
    if buid:
        ## Exceptions for buid=0 and buid=1
        if buid == '0':
            raise ValueError(f"{buid=} 0 cannot be modified")
        elif buid == '1':
            danom.update_toc_block()
            block = danom.get_block_by_buid(buid)
        else:
            ## Block need to exists
            if danom.get_block_by_buid(buid):
                block = danom.get_block_by_buid(buid)
            else:
                raise ValueError(f"{buid=} does not exists within the file. What Block do you want to append text to?")
    ## If there is not buid create a new one
    elif not query:

        buid = danom.get_next_available_buid()
        block = danom.create_new_block(buid, new_label, source)
        ## Upadte the Toc Block
        danom.update_toc_block()
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
    """Show/update a determined Dan Block Object
    If no --json and --text are given. Update in place the determined block
    If no --buid or --label are given. Show all the document from buid=0 to last
    """
    print(f"Showing {json=} {text=} {buid=} {label=} {path=}")

    if not is_valid_dan_format(path):
        raise ValueError(f"{path} Invalid file type. Expected .dan syntax within. If the path is correct you may want to fix it")

    danom = Danom()
    danom.load(path)
    danom.get_links_target()


    ## Selecting target by block or whole danom
    match (buid, label):
        case (None, None):
            target = danom
        case (buid, None) if buid is not None:  # Check buid is not None
            if buid == '1':
                danom.update_toc_block()
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




def block_source(path, buid=None, source=None, title=None, content=None, json=False, text=False):
    """Sourcing a block or the whole document (Updating according to source information)
    """
    print(f"Sourcing the block {path} {buid=} {source=} {title=} {content=} {json=} {text=}")

    if not is_valid_dan_format(path):
        raise ValueError(f"{path} Invalid file type. Expected .dan syntax within. If the path is correct you may want to fix it")

    danom = Danom()
    danom.load(path)
    danom.get_links_target()

    ## Create a new Block if source is been inputed
    if source:
        block = danom.create_new_block(buid, title)
        block.source = source
        block.content.append(f'source: "{source}"')
        if title:
            block.title_cmd = title
            block.content.append(f'title_cmd: "{title}"')
        if content:
            block.content_cmd = content
            block.content.append(f'content_cmd: "{content}"')
        block.update_content(path)
    else:
        for block in danom:
            block.update_content(path)

    danom.to_file(path)
    return block.buid
