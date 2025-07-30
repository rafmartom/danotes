from ..model.core import *

def file_new(path, json=False, text=True):
    """Create the Header and TOC blocks of a New File"""
    print(f"Creating a new file {path=}")

    danom = Danom()
    danom.create_new_header_block(path)
    danom.create_new_block('1', "Document TOC")

    # Outputting info in the desired format
    if json:
        return danom.to_json()
    elif text:
        return danom.to_text()
    else:
        danom.to_file(path)
        return f"File {path} has been successfully created.\n"
  
def file_append(path, query):
    """Append text to a .dan formated file without parsing the Danom (dumber but faster on huge files)"""
    append_after_third_last_line(path, query)

def file_update_toc(path):
    """Alias for danotes block write --buid 1"""
    danom = Danom()
    danom.load(path)
    danom.get_links_target()
    danom.update_toc_block()
    danom.to_file(path)
    return f"{path} toc block has been succesfully update alongside its danom.\n"

def file_refresh(path):
    """Alias for danotes block write which updates all the file"""
    danom = Danom()
    danom = danom.load(path)
    danom.get_links_target()
    danom.to_file(path)
    return f"{path} danom has been successfully updated.\n"
