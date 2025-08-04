import re
import json
import pyfiglet
from pathlib import Path
import os
from typing import Self
import yaml

## ----------------------------------------------------------------------------
# @section OBJECT_MODEL_DEFINITIONS(DANOM)


class Header:
    """Manages the header of a Block, from <B={buid}>{label} to <T>."""
    def __init__(self, block: 'Block'):
        self.block = block

    def to_string(self) -> str:
        """Get the Header of a Block as a contiguous string using Block's buid and label."""
        output = []

        if self.block.title_marked:
            output.append(f"<B={self.block.buid}>{self.block.label} (X)")
        else:
            output.append(f"<B={self.block.buid}>{self.block.label}")

        pyfiglet_string = pyfiglet.figlet_format(self.block.label)
        lines = [line.rstrip() for line in pyfiglet_string.split('\n')]
        output.extend(lines)
        # Remove the last two lines of pyfiglet output (empty or decorative)
        if len(lines) > 2:
            lines.pop()
            lines.pop()

        return '\n'.join(output)

class Content(list):
    """List of the lines containing the content of a Block."""
    def to_string(self) -> str:
        """Get the Content as a contiguous string."""
        return '\n'.join(self)


class LinkTarget():
    """Each Individual Link Target in the for of <I={buid}#{iid}>{label}</I>"""
    ## Core methods -------------------
    def __init__(self, label: str, iid: str):
        self.label = label
        self.iid = iid

    def __repr__(self):
        return f"LinkTarget(label={repr(self.label)}, iid={repr(self.iid)})"

class LinksTarget(list):
    """The Container of Link Target Objects within a Block"""
    ## Core methods -------------------
    def __init__(self, block: 'Block'):
        super().__init__()  # Initialize the list properly
        self.block = block
        
    def __repr__(self):
        items = ', '.join(repr(item) for item in self)
        return f"LinksTarget(block={self.block.buid}, items=[{items}])"

    ## Modification methods -----------
    def new_link(self, new_label: str, iid: str):
        self.append(LinkTarget(new_label, iid))
        return self

    ## Output methods -----------------
    def to_string(self) -> str:
        output = []
        for link_target in self:
            # Access attributes directly since LinkTarget is a class, not a dict
            output.append(f"- <L={self.block.buid}#{link_target.iid}>{link_target.label}</L>")

        # Article TOC Tag
        output.append("<T>")

        return '\n'.join(output)


class Block():
    """DAN Block Elements that get printed out and displayed, they contain the Inline elements"""
    ## Core methods -------------------
    def __init__(self, label: str, buid: str, content: Content, title_marked: bool = False, source: str = '', title_cmd: str = '', content_cmd: str = ''):
        self.buid = buid
        self.label = label
        self.content = content
        self.header = Header(self)
        self.links_target = LinksTarget(self)
        self.title_marked = title_marked
        self.source = source
        self.title_cmd = title_cmd
        self.content_cmd = content_cmd
    def __repr__(self):
        content_preview = ', '.join([repr(line.strip()) for line in self.content[:3]])
        if len(self.content) > 3:
            content_preview += f', ...(+{len(self.content)-3} more lines)'
        return f"Block(buid='{self.buid}', label='{self.label}', content=[{content_preview}], links_target={repr(self.links_target)}, title_marked='{self.title_marked}', source='{self.source}', title_cmd='{self.title_cmd}', content_cmd='{self.content_cmd}')"
    def to_dict(self) -> dict[str, any]:
        """Convert the Block to a JSON-serializable dictionary."""
        return {
            'buid': self.buid,
            'label': self.label,
            'content': list(self.content),  # Convert Content to plain list
            'links_target': [
                {'label': lt.label, 'iid': lt.iid} 
                for lt in self.links_target
            ]
        }

    ## Getter Methods -----------------
    def get_links_target(self):
        """Get the LinksTarget property for the given Block"""
        pattern = r'<I=([0-9a-zA-Z]+)#([0-9a-zA-Z]+)>(.*?)</I>'
        
        for line in self.content:
            for match in re.finditer(pattern, line):
                iid = match.group(2)
                label = match.group(3)
                self.links_target.append(LinkTarget(label, iid))
        return self

    ## Helper Methods -----------------
    def get_next_available_iid(self) -> str:
        """Get the next available iid for a Link"""
        if len(self.links_target):
            iid = self.links_target[-1].iid
        else:
            iid = '0'
        iid = get_next_uid(iid)

        return iid


    ## Modification methods -----------
    def append_query(self, query: str):
        """Append query to the last line of the Block's content (same line)"""
        if self.content:
            self.content[-1] += query
        else:
            self.content.append(query)  # fallback if content is empty
        return self

    def append_link(self, new_label): 
        """Append a new Link to the Block, both inside the Content and on the LinksTarget"""
        iid = self.get_next_available_iid()
        self.links_target.new_link(new_label, iid)
        self.append_query(f"<I={self.buid}#{iid}>{new_label}</I>")

        return self

    ## Output methods -----------------
    def to_json(self, indent: int = 2) -> str:
        """Serialize the Block to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_string(self) -> str:

        ## First block cannot start with an empty line
        if self.buid != "0":
            if self.title_marked:
                output = ' (X)' + "\n" + self.header.to_string()
            else:
                output = "\n" + self.header.to_string()
        else:
            output = self.header.to_string()

        output = output + self.links_target.to_string()
        output = output + "\n"
        output = output + self.content.to_string()
        return output

    def to_text(self) -> str:
        """Get the Content of the Block with a horizontal line <hr> at the end"""
        output = self.to_string()
        output = output + '\n'   ## Adding tralining empty line (lower-padding)
        output = output + f'\n</B><L=1>To Document TOC</L> | <L={self.buid}>Back to Article Top</L>\n'
        return output + ('=' * 105)


class Danom(list):
    """The Root Object for the Object Model of a .dan file DAN ObjectModel"""

    ## Getter Methods -----------------
    def load(self, path) -> Self:
        ## Reading line by line the file parsing the Block Tags
        with open(path, 'r', encoding='utf-8') as file:
            inside_block = False
            inside_header = True
            inside_yaml = True
            source = ''
            title_cmd = ''
            content_cmd = ''
            content = Content()

            while True:
                line = file.readline()

                if line == '':
                    if inside_block:  # If file ends while still in a block, save it
                        self.append(Block(label, buid, content, title_marked=title_marked, source=source, title_cmd=title_cmd, content_cmd=content_cmd))
                    break

                if inside_block == False:
                    ## Checking for all the Block Opening Tags Line
                    block_otag_match = re.search(r'(?<=<B=)([0-9a-zA-Z]+)>([^<\n]+)', line)
                    if block_otag_match:
                        inside_block = True
                        inside_header = True
                        inside_yaml = True
                        buid = block_otag_match.group(1)
                        label_unfiltered = block_otag_match.group(2)
                        ## Some of the block Opening Tags Line May be Marked
                        label_match = re.search(r'(.*)( \(X\))', label_unfiltered)
                        if label_match:
                            label = label_match.group(1)
                            title_marked = True
                        else:
                            label = label_unfiltered
                            title_marked = False
                        content = Content()
                else:
                    if inside_header == True:
                        if re.search(r'^<T>$', line):
                            inside_header = False
                    else:
                        if re.search(r'^</B>.*', line):
                            inside_block = False
                            self.append(Block(label, buid, content, title_marked=title_marked, source=source, title_cmd=title_cmd, content_cmd=content_cmd))   ## Create the Danom Block Object
                        else:
                            if inside_yaml:
                                yaml_var = check_yaml_line(line)
                                if yaml_var:
                                    # Extract variables if they exist, else set to None
                                    source = yaml_var.get('source', source)
                                    title_cmd = yaml_var.get('title_cmd', title_cmd)
                                    content_cmd = yaml_var.get('content_cmd', content_cmd)
                                    content.append(line.rstrip('\n')) 
                                else:
                                    inside_yaml = False
                                    content.append(line.rstrip('\n')) 
                            else:
                                content.append(line.rstrip('\n')) 


        ## Deleting the trailing empty line (lower-padding) that is added
        for block in self:
            block.content.pop()
        return self



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

    def get_links_target(self):
        for block in self:
            block.get_links_target()
        return self



    ## Helper Methods ----------------
    def get_next_available_buid(self) -> str:
        """Prints out the next available <buid> within that Danom"""
        return get_next_uid(self[-1].buid)

    ## Modification methods -----------
    def create_new_block(self, buid: str=None, new_label: str="Unnamed Article"):
        """Create a new Block on a given Danom"""
        ## Use the next available buid
        if buid is None:
            buid = self.get_next_available_buid()

        new_block = Block(new_label, buid, Content())
        self.append(new_block)
        return new_block

    def write_to_block(self, buid: str, query: str):
        """Write some query into a determined block of a given Danom"""
        block = self.get_block_by_buid(buid)
        if block:
            block.content.append(query)

    def create_new_header_block(self, path: str):
        """Create a new header block"""
        basename_no_ext = Path(path).stem  
        ## Creating that special new block buid 0
        new_block = self.create_new_block("0", basename_no_ext)


        pyfiglet_string = pyfiglet.figlet_format("danotes", font="univers")

        lines = [line.rstrip() for line in pyfiglet_string.split('\n')]
        lines.pop()
        lines.pop()

        new_block.content.extend(lines)
        new_block.content.append("")
        new_block.content.append("The following lines are used by danotes, modify them only if you know !")
        new_block.content.append("")
        new_block.content.append('dan_ext_list: []')
        new_block.content.append('dan_kw_question_list: []')
        new_block.content.append('dan_kw_nontext_list: []')
        new_block.content.append('dan_kw_linenr_list: []')
        new_block.content.append('dan_kw_warningmsg_list: []')
        new_block.content.append('dan_kw_colorcolumn_list: []')
        new_block.content.append('dan_kw_underlined_list: []')
        new_block.content.append('dan_kw_preproc_list: []')
        new_block.content.append('dan_kw_comment_list: []')
        new_block.content.append('dan_kw_identifier_list: []')
        new_block.content.append('dan_kw_ignore_list: []')
        new_block.content.append('dan_kw_statement_list: []')
        new_block.content.append('dan_kw_cursorline_list: []')
        new_block.content.append('dan_kw_tabline_list: []')
        new_block.content.append('dan_wrap_lines: 105')
        new_block.content.append('dan_indexed_from:')
        new_block.content.append('dan_parsed_on:')
        new_block.content.append(f'dan_title: "{basename_no_ext}"')
        new_block.content.append('dan_description:')
        new_block.content.append('dan_tags: []')

        return new_block

    def create_new_toc_block(self):
        new_block = self.create_new_block("1", "Document TOC")
        return self

    def update_toc_block(self):
        """Update the Content of the special Block buid='1' (toc Block). With all the links formed""" 

        # Reset it to an empty Content Object
        self[1].content = Content()
        for block in self:
            if block.title_marked:
                self[1].content.append(f"- <L={block.buid}>{block.label}</L> (X)")
            else:
                self[1].content.append(f"- <L={block.buid}>{block.label}</L>")
        return self

    def update_from_legacy(self):
        """Update the danom to last version from vim-dan-generator legacy version
        Pre-requisites: transform_legacy_title(path) 
        """

        # Shift the blocks buid + 1 starting from danom[2] 
        self[1].buid = '1'
        for i, block in enumerate(self):
            if i < 2:
                continue
            new_buid = get_next_uid(block.buid)
            block.buid = new_buid

        # Change B=1 label to Document TOC
        self[1].label = 'Document TOC'

        # Delete old figlet from content
        
        # Delete in Block TOC
        for _ in range(6):
            self[1].content.pop(0)

        # Delete in each succesive block
        for i, block in enumerate(self):
            if i < 2:
                continue
            # Calculate the length of the figlet string
            pyfiglet_string = pyfiglet.figlet_format(block.label)
            lines = [line.rstrip() for line in pyfiglet_string.split('\n')]

            no_lines = len(lines)

            for _ in range(no_lines):
                block.content.pop(0)

        # Transform Header
        # ---------

        # Step 1) Parse modeline variables dynamically
        modeline_vars = {
            'dan_ext_list':       11,
            'dan_kw_question_list':  12,
            'dan_kw_nontext_list':   13,
            'dan_kw_linenr_list':    14,
            'dan_kw_warningmsg_list':15,
            'dan_kw_colorcolumn_list':16,
            'dan_kw_underlined_list':17,
            'dan_kw_preproc_list':    18,
            'dan_kw_comment_list':   19,
            'dan_kw_identifier_list':20,
            'dan_kw_ignore_list':    21,
            'dan_kw_statement_list': 22,
            'dan_kw_cursorline_list':23,
            'dan_kw_tabline_list':   24,
        }

        parsed_lists = {}

        for varname, index in modeline_vars.items():
            line = self[0].content[index]
            match = re.search(rf'g:{varname}\s*=\s*"([^"]*)"', line)
            if match:
                items = [item.strip() for item in match.group(1).split(',') if item.strip()]
                parsed_lists[varname] = items
            else:
                print(f"Warning: Could not parse line for {varname}:")

        # Step 2) Create the Header block
        basename_no_ext = self[0].label
        new_block = Block(basename_no_ext, "0", Content())


        new_block.content.append("")

        pyfiglet_string = pyfiglet.figlet_format("danotes", font="univers")
        lines = [line.rstrip() for line in pyfiglet_string.split('\n') if line.strip()]
        new_block.content.extend(lines)
        new_block.content.append("")

        new_block.content.append("")
        new_block.content.append("The following lines are used by danotes, modify them only if you know !")
        new_block.content.append("")

        for key, _ in modeline_vars.items():
            if key in parsed_lists:
                items = parsed_lists[key]
                value_str = ', '.join(f'"{item}"' for item in items)
                new_block.content.append(f'{key}: [{value_str}]')
            else:
                new_block.content.append(f'{key}: []')

        # Other metadata
        new_block.content.append('dan_wrap_lines: 105')
        new_block.content.append('dan_indexed_from:')
        new_block.content.append('dan_parsed_on:')
        new_block.content.append(f'dan_title: "{basename_no_ext}"')
        new_block.content.append('dan_description:')
        new_block.content.append('dan_tags: []')

        self[0].content = new_block.content

        # EOF EOF EOF Transform Header
        # ---------

        return self



    ## Output methods -----------------
    def to_json(self, indent: int = 2) -> str:
        """Convert the Danom to a JSON string."""
        return json.dumps([block.to_dict() for block in self], indent=indent, ensure_ascii=False)

    def to_text(self) -> str:
        """Convert the Danom to a text string.Note: <hr> horizontal separators will be added"""
        output = []
        for block in self:
            ## For Toc Block Update it before writting
            if block.buid == "1":
                self.update_toc_block()
            output.append(block.to_text())
        return ''.join(output)    

    def to_text_notoc(self) -> str:
        """Same as to_text() but doesnt Update the Block Toc (use for conversions of vim-dan-generator)"""
        output = []
        for block in self:
            output.append(block.to_text())
        return ''.join(output)    


    def to_file(self, path):
        """Save the Danom rendered text to a file"""
        text = self.to_text()
        with open(path, 'w', encoding='utf-8') as file:
            file.write(text) 

    def to_file_notoc(self, path):
        """Same as to_file() but withou altering Block Toc"""
        text = self.to_text_notoc()
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


def create_new_header_block(path):
    content = []

    pyfiglet_string = pyfiglet.figlet_format("danotes", font="univers")

    lines = [line.rstrip() for line in pyfiglet_string.split('\n')]
    content.extend(lines)

    content.append("")
    content.append("The following lines are used by danotes, modify them only if you know !")
    content.append("")

    content.append('dan_ext_list: ["javascript"]')
    content.append('dan_kw_question_list: ["^Description"]')
    content.append('dan_kw_nontext_list: ["^Parameters", "^Type"]')
    content.append('dan_kw_linenr_list: ["^Parameter "]')
    content.append('dan_kw_warningmsg_list: ["^Returns"]')
    content.append('dan_kw_colorcolumn_list: []')
    content.append('dan_kw_underlined_list: []')
    content.append('dan_kw_preproc_list: []')
    content.append('dan_kw_comment_list: []')
    content.append('dan_kw_identifier_list: []')
    content.append('dan_kw_ignore_list: []')
    content.append('dan_kw_statement_list: []')
    content.append('dan_kw_cursorline_list: []')
    content.append('dan_kw_tabline_list: []')
    content.append('dan_wrap_lines: 105')
    content.append('dan_indexed_from:')
    content.append('dan_parsed_on:')
    content.append('dan_title: "adobe-ppro"')
    content.append('dan_description:')
    content.append('dan_tags: []')
    content.append('')



def transform_legacy_title(path):
    path = Path(path)
    basename_no_ext = path.stem

    with open(path, 'r', encoding='utf-8') as file:
        original_lines = file.readlines()

    # Prepend <B=0> and <T>
    new_lines = [f"<B=0>{basename_no_ext}\n", "\n<T>\n"] + original_lines

    # Insert </B> before first full-width line of '='
    for i, line in enumerate(new_lines):
        if line.strip('=\n') == '' and len(line.strip()) >= 50:
            new_lines.insert(i, "</B>Something\n")
            break

    # Insert <T> after each <B=n>TitleLine
    result_lines = []
    b_tag_pattern = re.compile(r'^<B=[0-9a-zA-Z]+>.+')

    i = 0
    while i < len(new_lines):
        line = new_lines[i]
        result_lines.append(line)
        if b_tag_pattern.match(line):
            # Only insert <T> if the next line is not already <T>
            if i + 1 >= len(new_lines) or new_lines[i + 1].strip() != '<T>':
                result_lines.append("\n<T>\n")
        i += 1

    # Write back to the file
    with open(path, 'w', encoding='utf-8') as file:
        file.writelines(result_lines)


def check_yaml_line(line):
    try:
        # Attempt to parse the line as YAML
        yaml_content = yaml.safe_load(line)
        # Check if the result is a dictionary (valid YAML key-value pair)
        if isinstance(yaml_content, dict):
            return yaml_content
        return False
    except yaml.YAMLError:
        # Return False if the line is not valid YAML
        return False


## EOF EOF EOF HELPERS 
## ----------------------------------------------------------------------------



## ----------------------------------------------------------------------------
# @section CORE_SUBROUTINES
# @description Subroutines triggered directly by CLI Handlers

def is_valid_dan_format(path):
    """Return if the file has proper .dan format"""
    with open(path, 'r', encoding='utf-8') as file:
            line = file.readline()
            match = re.search(r'^<B=0>.*', line)
            if match:
                return True
            return False



def append_after_third_last_line(file_path, string_to_append, estimated_max_line_length=200):
    # Open in binary mode to work with byte offsets
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()

        # Seek to a reasonable chunk near the end
        seek_back = min(file_size, estimated_max_line_length * 4)
        f.seek(-seek_back, os.SEEK_END)
        tail = f.read()

        # Find the positions of the last 3 newlines
        newline_indices = [i for i, b in enumerate(tail) if b == ord(b'\n')]
        if len(newline_indices) < 3:
            # Not enough lines to skip 3 — append at the end
            insert_pos = file_size
        else:
            insert_pos = file_size - seek_back + newline_indices[-3] + 1

    # Now rewrite the file up to insert_pos, then add your content, then the rest
    with open(file_path, 'rb') as f:
        original = f.read()

    new_content = (
        original[:insert_pos] +
        string_to_append.encode() +
        (b'' if string_to_append.endswith('\n') else b'\n') +
        original[insert_pos:]
    )

    with open(file_path, 'wb') as f:
        f.write(new_content)


## EOF EOF EOF CORE_SUBROUTINES 
## ----------------------------------------------------------------------------


__all__ = [ 'Block', 'Danom', 'Content', 'Header', 'LinkTarget', 'LinksTarget', 'is_valid_dan_format' , 'append_after_third_last_line', 'get_next_uid', 'transform_legacy_title']
