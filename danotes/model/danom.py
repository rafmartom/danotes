"""
Root Dan Object Model (Danom) Implementation.
"""

import re
import json
import pyfiglet
from pathlib import Path, PurePath
import os
from typing import Self
import yaml
from treelib import Node, Tree
import danotes.model



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
            filters = ''
            content = danotes.model.Content()

            while True:
                line = file.readline()

                if line == '':
                    if inside_block:  # If file ends while still in a block, save it
                        self.append(danotes.model.Block(label, buid, content, title_marked=title_marked, source=source, title_cmd=title_cmd, filters=filters, content_cmd=content_cmd))
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
                        content = danotes.model.Content()
                else:
                    if inside_header == True:
                        yaml_var = danotes.model.check_yaml_line(line)
                        if yaml_var:
                            # Extract variables if they exist, else set to None
                            source = yaml_var.get('source', source)
                            title_cmd = yaml_var.get('title_cmd', title_cmd)
                            content_cmd = yaml_var.get('content_cmd', content_cmd)
                            filters = yaml_var.get('filters', filters)
                        else:
                            if re.search(r'^<T>$', line):
                                inside_header = False
                    else:
                        if re.search(r'^</B>.*', line):
                            inside_block = False
                            self.append(danotes.model.Block(label, buid, content, title_marked=title_marked, source=source, title_cmd=title_cmd, filters=filters, content_cmd=content_cmd))   ## Create the Danom Block Object
                            # Need to restart the vars
                            source = ''
                            title_cmd = ''
                            content_cmd = ''
                            filters = ''
                        else:
                            content.append(line.rstrip('\n')) 


        ## Deleting the trailing empty line (lower-padding) that is added
        for block in self:
            block.content.pop()
        return self



    def get_block_by_buid(self, buid: str) -> 'Block | None':
        for block in self:
            if block.buid == buid:
                return block
        return None

    def get_block_by_label(self, label) -> 'Block | None':
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
        return danotes.model.get_next_uid(self[-1].buid)

    ## Modification methods -----------
    def create_new_block(self, buid: str=None, new_label: str="Unnamed Article", source: str=None):
        """Create a new Block on a given Danom"""
        ## Use the next available buid
        if buid is None:
            buid = self.get_next_available_buid()

        content = []
        if source:
            content.append(f'source: "{source}"')

        new_block = danotes.model.Block(label = new_label, buid = buid, content = danotes.model.Content(content), source = source)
        print(f'Creating new_block {new_block.title_marked=} {new_label=} {buid=} {source=}')
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
        new_block = self.create_new_danotes.model.Block("0", basename_no_ext)


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
        ##new_block.content.append('dan_kw_nontext_list: []')
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
        new_block = self.create_new_danotes.model.Block("1", "Document TOC")
        return self

    def update_toc_block(self):
        """Update the Content of the special Block buid='1' (toc Block). With all the links formed""" 

        # Create a tree
        tree = Tree()
        # Create a root node (optional, can be the base directory or a placeholder)
        tree.create_node("/", "root")  # Root of the file system
        # Track directories to avoid duplicates
        created_dirs = set()


        # Reset it to an empty Content Object
        self[1].content = danotes.model.Content()
        for block in self:

            is_a_dir = False
            if danotes.model.is_a_dir_path(block.source):
                is_a_dir = True


            # Normalize the path and split into components
            if not block.source:
                source = ""
            else:
                source = os.path.normpath(block.source)

            if not is_a_dir:
                source = PurePath(source).parent.as_posix()

            path_parts = source.strip("/").split("/")

            # Build the tree path
            current_path = ""
            parent_id = "root"


            # Create directory nodes
            for part in path_parts:
                current_path = os.path.join(current_path, part)
                if current_path not in created_dirs:
                    tree.create_node(part, current_path, parent=parent_id)
                    created_dirs.add(current_path)
                parent_id = current_path


            # Add the label as a leaf node with buid
            leaf_id = f"{current_path}/{block.buid}"

            if block.title_marked:
                tree.create_node(f"<L={block.buid}>{block.label}</L> (X)", leaf_id, parent=current_path)
            else:
                tree.create_node(f"<L={block.buid}>{block.label}</L>", leaf_id, parent=current_path)

            # Get the tree as a string
            tree_string = tree.show(stdout = False)

            # Optionally, convert the string to a list of lines
            tree_lines = tree_string.split("\n")
        self[1].content.extend(tree_lines) 
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
            new_buid = danotes.model.get_next_uid(block.buid)
            block.buid = new_buid

        # Shift all BUID's +1 for Link Sources/Link Targets on Content
        for block in self:
            block.content.shift_links_one_buid()

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
        new_block = danotes.model.Block(basename_no_ext, "0", danotes.model.Content())


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
