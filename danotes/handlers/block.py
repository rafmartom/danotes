def block_write(path, buid, query, label, json=False, text=True):
    """Write a determined Dan Block Object. 
    If not target Block given write on next <buid>.
    If target Block already exists will append text to it"""

    print(f"Writing {json=} {text=} {buid=} {path=} {query=} {label=} ")


def block_show(path, buid, label, json=False, text=True):
    """Show and update a determined Dan Block Object
    If no --json and --text are given. Update in place the determined block
    If no --buid or --label are given. Show all the document from buid=0 to last
    """
    print(f"Showing {json=} {text=} {buid=} {label=} {path=}")

