from ..model.core import *

def link_write(path, buid, uuid, new_label=None, json=False, text=True):
    """Write a determined Dan Link Object"""
    print(f"Writing {json=} {text=} {buid=} {uuid=} {new_label=} {path=}")

    danom = Danom()
    danom = danom.load(path)
    danom.get_links_target()

    if uuid:
        # @todo
        raise ValueError(f"Feature not implemented")

    ## Getting the block
    if buid:
        ## Block needs to exist
        if danom.get_block_by_buid(buid):
            block = danom.get_block_by_buid(buid)
        elif buid == '0' or buid == '1':
            raise ValueError(f"{buid=} 0 or 1 cannot be modified")
        else:
            raise ValueError(f"{buid=} does not exists within the file. What Block do you want to append text to?")
    ## If there is query but not buid get the last block
    else :
        block = danom[-1]

    iid = block.append_link(new_label)
    danom.to_file(path)
    return iid


def link_show(path, buid, uuid, label, json=False, text=True):
    """For a block show/update the LinkTarget list of that Block
    For the Document show/update all the LinkTarget for each Block
    """
    print(f"Showing {json=} {text=} {buid=} {uuid=} {label=} {path=}")

    danom = Danom()
    danom = danom.load(path)

    ## Selecting target by block or whole danom
    match (buid, label):
        case (None, None):
            target = danom
            target.get_links_target()
        case (buid, None) if buid is not None:  # Check buid is not None
            if danom.get_block_by_buid(buid):
                target = danom.get_block_by_buid(buid)
                target.get_links_target()
            else:
                raise ValueError(f"{buid=} does not exist.")
        case (None, label) if label is not None:  # Check label is not None
            if danom.get_block_by_label(label):
                target = danom.get_block_by_label(label)
                target.get_links_target()
            else:
                raise ValueError(f"{label=} does not exist.")
        case _:
            raise ValueError("Cannot specify both buid and label.")


    # Outputting info in the desired format
    if json:
        return target.to_json()
    elif text:
        return target.to_text()
    else:
        danom.to_file(path)
        return f"{path} danom has been successfully updated.\n"
