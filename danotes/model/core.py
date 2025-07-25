import re
import json
import pyfiglet

## ----------------------------------------------------------------------------
# @section OBJECT_MODEL_DEFINITIONS(DANOM)


class DanObject:
    """Base class for all DAN objects."""
    def __init__(self, label: str):
        self.label = label

class Block(DanObject):
    """DAN Block Elements that get printed out and displayed, they contain the Inline elements"""
    ## Core methods -------------------
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

    ## Output methods -----------------
    def to_json(self, indent: int = 2) -> str:
        """Serialize the Block to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    def get_content(self) -> str:
        """Get the Content of the Block as it is"""
        return ''.join(self.content)

    def render_content(self) -> str:
        """Get the Content of the Block with a horizontal line <hr> at the end"""
        content_str = self.get_header()
        content_str = content_str + self.get_content()
        content_str = content_str + f'\n</B><L=1>To Document TOC</L> | <L={self.buid}>Back to Article Top</L>\n'
        return content_str + ('=' * 105) + "\n"

    def get_header(self) -> str:
        output = []

        output.append(f"<B={self.buid}>{self.label}")
        pyfiglet_string = pyfiglet.figlet_format(self.label)
        lines = [line.rstrip() for line in pyfiglet_string.split('\n')]

        output.extend(lines)
        lines.pop()
        lines.pop()

        output.append(f"<T>")

        return '\n'.join(output)



class Danom(list):
    """The Root Object for the Object Model of a .dan file DAN ObjectModel"""

    ## Getter Methods -----------------
    def get_block_by_buid(self, buid: str) -> Block | None:
        for block in self:
            if block.buid == buid:
                return block
        return None

    def get_block_by_label(self, label) -> Block | None:
        for block in self:
            if block.label == label:
                return block
        return None

    ## Helper Methods ----------------
    def get_next_available_buid(self) -> str:
        """Prints out the next available <buid> within that Danom"""
        return get_next_uid(self[-1].buid)

    ## Modification methods -----------
    def create_new_block(sef, buid: str, new_label: str="Unnamed Article"):
        """Create a new Block on a given Danom"""
        content = print_article_header(buid, new_label)
        self.append(Block(new_label, buid, content))

    def write_to_block(self, buid: str, query: str):
        """Write some query into a determined block of a given Danom"""
        block = self.get_block_by_buid(buid)
        if block:
            block.content.append(query)

    ## Output methods -----------------
    def to_json(self, indent: int = 2) -> str:
        """Convert the Danom to a JSON string."""
        return json.dumps([block.to_dict() for block in self], indent=indent, ensure_ascii=False)

    def render_content(self) -> str:
        """Convert the Danom to a text string.Note: <hr> horizontal separators will be added"""
        output = []
        for block in self:
            output.append(block.render_content())
        return ''.join(output)    

    def get_content(self) -> str:
        """Convert the Danom to a text string.Without <hr>"""
        output = []
        for block in self:
            output.append(block.get_content())
        return ''.join(output)    


    def save_text(self, path):
        """Save the Danom rendered text to a file"""
        text = self.render()
        with open(path, 'w', encoding='utf-8') as file:
            file.write(text) 



## EOF EOF EOF OBJECT_MODEL_DEFINITIONS(DANOM) 
## ----------------------------------------------------------------------------


## ----------------------------------------------------------------------------
# @section HELPERS
# @description Helper functions in use by the Core Subroutines


def get_next_uid(uid):
    """
    Given a DAN UID (0-9, a-z, A-Z), returns the next UID in sequence.
    Examples:
        'l5' -> 'l6'
        'la' -> 'lb'
        'lZ' -> 'm0'
        'ZZ' -> '000' (overflow, adds a digit)
    """
    # Define the alphanumeric characters in order
    alphanumeric = [str(d) for d in range(10)] + [chr(c) for c in range(ord('a'), ord('z')+1)] + [chr(C) for C in range(ord('A'), ord('Z')+1)]
    base = len(alphanumeric)
    char_to_value = {c: i for i, c in enumerate(alphanumeric)}

    # Convert UID to decimal
    decimal = 0
    for char in uid:
        decimal = decimal * base + char_to_value[char]

    # Increment
    decimal += 1

    # Convert back to UID
    if decimal == 0:
        return alphanumeric[0]

    next_uid = []
    while decimal > 0:
        decimal, remainder = divmod(decimal, base)
        next_uid.append(alphanumeric[remainder])

    return ''.join(reversed(next_uid))


def print_article_header(buid, label):
    output = []

    output.append(f"<B={buid}>{label}")
    pyfiglet_string = pyfiglet.figlet_format(label)

    lines = [line.rstrip() for line in pyfiglet_string.split('\n')]
    output.extend(lines)
    lines.pop()
    lines.pop()

    output.append(f"<T>")

    output.append(f"")
    output.append(f"")

    output.append(f"</B><L=1>To Main TOC</L> | <L={buid}>Back to Article Top</L>")


#    return output
    return '\n'.join(output)



## EOF EOF EOF HELPERS 
## ----------------------------------------------------------------------------



## ----------------------------------------------------------------------------
# @section CORE_SUBROUTINES
# @description Subroutines triggered directly by CLI Handlers

def parse_danom(path):
    danom = Danom()  # danom is a list of all the Block Objects (Dicts)

    ## Reading line by line the file parsing the Block Tags
    with open(path, 'r', encoding='utf-8') as file:
        inside_block = False
        inside_header = True
        content = []

        while True:
            line = file.readline()

            if line == '':
                if inside_block:  # If file ends while still in a block, save it
                    danom.append(Block(label, buid, content))
                break

            if inside_block == False:
                block_otag_match = re.search(r'(?<=<B=)([0-9a-zA-Z]+)>([^<\n]+)', line)
                if block_otag_match:
                    inside_block = True
                    inside_header = True
                    buid = block_otag_match.group(1)
                    label = block_otag_match.group(2)
                    content = []
            else:
                if inside_header == True:
                    if re.search(r'^<T>$', line):
                        inside_header = False
                else:
                    if re.search(r'^</B>.*', line):
                        inside_block = False
                        danom.append(Block(label, buid, content))   ## Create the Danom Block Object
                    else :
                        content.append(line) 
    return danom




def parse_danom_old(path):
    danom = Danom()  # danom is a list of all the Block Objects (Dicts)

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
                    inside_header = True
                    buid = block_otag_match.group(1)
                    label = block_otag_match.group(2)
                    content = []  # Reset content for new block
#                    content.append(line) 

            ## When inside a Block, program is checking for a Block Closing Tag
            else:
                if inside_header == False:
                    print('WANG!!')                    ## DEBUGGING
                    ## If found the Closing Tag change inside_block flag
                    if re.search(r'^</B>.*', line):
                        inside_block = False
                        inside_header = False
    #                    content.append(line) 
                        danom.append(Block(label, buid, content))   ## Create the Danom Block Object
                        content = []  # Reset content after creating block

                    else:
                    # Append each line in the content list
                        content.append(line) 
                else:
                    print('LANG!!')                    ## DEBUGGING
                    print(f'[DEBUG]: {inside_header=}')                    ## DEBUGGING
                    if re.search(r'^<T>$', line):
                        print('BANG!!')                    ## DEBUGGING
                        inside_header == False
    return danom


def is_valid_dan_format(path):
    """Return if the file has proper .dan format"""
    with open(path, 'r', encoding='utf-8') as file:
            line = file.readline()
            match = re.search(r'^<B=0>.*', line)
            if match:
                return True
            return False

     

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

__all__ = [ 'DanObject', 'Block', 'Danom', 'parse_danom', 'is_valid_dan_format' ]
#__all__ = ['DanObject', 'Block', 'Header', 'GeneralToc', 'Article', 'Inline', 'LinkTarget']
