class DanObject:
    """Base class for all DAN objects."""
    def __init__(self, label: str):
        self.label = label

class Block(DanObject):
    """DAN Block Elements that get printed out and displayed, they contain the Inline elements"""
    def __init__(self, label: str, buid: str, content: str, path: str, inlines: list):
        super().__init__(label)
        self.buid = buid
        self.path = path
        self.content = content
        self.inlines = inlines  # Fixed to use passed inlines

class Header(Block):
    """
    The First Block displayed in a DAN Document
    """
    def __init__(self, content):
        super().__init__(label="Danotes Header", buid="0", content=content, path=None, inlines=None)
        self.content = content

class GeneralToc(Block):
    """
    The second Block displayed in a DAN Document
    """
    def __init__(self, content):
        super().__init__(label="General Toc", buid="1", content=content, path=None, inlines=None)
        self.content = content

class Article(Block):
    """
    A DAN Article (specialized Block without iid)
    It represents all the Blocks of the DAN Document that within it have the actual
    Information
    Simplified example:
    ======================
    <B={buid}>{label}
    {label_in_figlet}

    <T>
    {content}
    </B><L=0>To General TOC</L> | <L={buid}>Back to Article Top</L>
    """
    def __init__(self, label: str, buid: str, content: str, path: str, inlines):
        super().__init__(label, buid, content, path, inlines)

class Inline(DanObject):
    def __init__(self, label: str, iid: str):
        super().__init__(label)
        self.iid = iid

class LinkTarget(Inline):
    """
    Represents strings of the form <I={buid}#{iid}>{label}</I>
    Meant to be placed all over the .dan file as placeholders,
    They will be parsed by ctags as link targets
    """
    def __init__(self, label: str, iid: str):
        super().__init__(label, iid=iid)


__all__ = ['DanObject', 'Block', 'Header', 'GeneralToc', 'Article', 'Inline', 'LinkTarget']

# Example usage
#link_one = LinkTarget('To Patxie', '0')
#link_two = LinkTarget('To Peps', '1')
#
#article_one = Article('My Article', '2', 'Wallazopa come on <I=2#0>To Patxie</I><I=2#1>To Peps</I>', None, [link_one, link_two])
#
#print(article_one)
#print(article_one.inlines)
#print(article_one.inlines[0])
#print(article_one.inlines[0].label)
#print(article_one.buid)
#print(article_one.inlines[0].iid)
