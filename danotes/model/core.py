import re
import json

## ----------------------------------------------------------------------------
# @section OBJECT_MODEL_DEFINITIONS(DANOM)


class DanObject:
    """Base class for all DAN objects."""
    def __init__(self, label: str):
        self.label = label

class Block(DanObject):
    """DAN Block Elements that get printed out and displayed, they contain the Inline elements"""
    def __init__(self, label: str, buid: str, content: list):
        super().__init__(label)
        self.buid = buid
        self.content = content
    def __repr__(self):
        content_preview = ', '.join([repr(line.strip()) for line in self.content[:3]])
        if len(self.content) > 3:
            content_preview += f', ...(+{len(self.content)-3} more lines)'
        return f"Block(buid='{self.buid}', label='{self.label}', content=[{content_preview}])"
    def to_dict(self) -> dict[str, any]:
        """Convert the Block to a JSON-serializable dictionary."""
        return {
            'buid': self.buid,
            'label': self.label,
            'content': self.content  # Already a list (JSON-compatible)
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize the Block to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    def get_content(self) -> str:
        """Get the Content of the Block as it is"""
        return ''.join(self.content)


## EOF EOF EOF OBJECT_MODEL_DEFINITIONS(DANOM) 
## ----------------------------------------------------------------------------


## ----------------------------------------------------------------------------
# @section HELPERS
# @description Helper functions in use by the Core Subroutines


def parse_danom(path):
    danom = []  # danom is a list of all the Block Objects (Dicts)

    ## Reading line by line the file parsing the Block Tags
    with open(path, 'r', encoding='utf-8') as file:
        inside_block = False
        content = []

        while True:
            line = file.readline()

            ## Exit condition if found no more data in the file exit the loop
            if line == '':
                if inside_block:  # If file ends while still in a block, save it
                    danom.append(Block(label, buid, content))
                break

            ## Begin by matching an Block Opening Tag parsing its <buid> and <label>
            if inside_block == False:
                block_otag_match = re.search(r'(?<=<B=)([0-9a-zA-Z]+)>([^<\n]+)', line)
                if block_otag_match:
                    inside_block = True
                    buid = block_otag_match.group(1)
                    label = block_otag_match.group(2)
                    content = []  # Reset content for new block
                    content.append(line) 

            ## When inside a Block, program is checking for a Block Closing Tag
            else:
                ## If found the Closing Tag change inside_block flag
                if re.search(r'^</B>.*', line):
                    inside_block = False
                    danom.append(Block(label, buid, content))   ## Create the Danom Block Object
                    content = []  # Reset content after creating block

                else:
                    # Append each line in the content list
                    content.append(line) 

    return danom


#def is_valid_dan_format(path):
#    """Return if the file has proper .dan format"""
     
def get_block_by_buid(danom, buid):
    for block in danom:
        if block.buid == buid:
            return block
    return None

def get_block_by_label(danom, label):
    for block in danom:
        if block.label == label:
            return block
    return None

def danom_to_json(danom, indent: int = 2) -> str:
    """Convert a list of Block objects to a JSON string."""
    return json.dumps([block.to_dict() for block in danom], indent=indent, ensure_ascii=False)



## EOF EOF EOF HELPERS 
## ----------------------------------------------------------------------------



## ----------------------------------------------------------------------------
# @section CORE_SUBROUTINES
# @description Subroutines triggered directly by CLI Handlers


#def create_new_article(label):
#    """Create a new Article Object on the Next Available <buid>"""
#    Article()


#def block_show_json_all(path)
#    """Show all the Dan Blocks in a Given file output it in JSON"""
    


#def append_text_to_block(...):


#def get_block_by_buid(...):



## EOF EOF EOF CORE_SUBROUTINES 
## ----------------------------------------------------------------------------





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

__all__ = ['DanObject', 'Block', 'parse_danom', 'get_block_by_buid', 'get_block_by_label', 'danom_to_json' ]
#__all__ = ['DanObject', 'Block', 'Header', 'GeneralToc', 'Article', 'Inline', 'LinkTarget']
