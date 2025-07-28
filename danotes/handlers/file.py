from ..model.core import *

def file_new(path, json=False, text=True):
    """Create the Header and TOC blocks of a New File"""
    print(f"Creating a new file {path=}")

    danom = Danom()
    danom.create_new_header_block(path)
    danom.create_new_block('1', "Document TOC")

    target = danom

    # Outputting info in the desired format
    if json:
        return target.to_json()
    elif text:
        return target.to_text()
    else:
        danom.to_file(path)
        return f"File {path} has been successfully created.\n"
  
def file_append(path, query):
    """Append text to a .dan formated file without parsing the Danom (dumber but faster on huge files)"""
    append_after_third_last_line(path, query)

