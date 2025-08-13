"""
Block Class Implementation
"""

import re
import json
import pyfiglet
from pathlib import Path
import os
from typing import Self
import yaml
import danotes.model
import subprocess

class Block():
    """DAN Block Elements that get printed out and displayed, they contain the Inline elements"""
    ## Core methods -------------------
    def __init__(
        self,
        label: str,
        buid: str,
        content: 'Content',
        title_marked: bool = False,
        source: str = '',
        title_cmd: str = '',
        content_cmd: str = ''
    ):
        """Initialize the object with content and metadata.

        Args:
            label: Identifier label for the content
            buid: Unique identifier string
            content: Content object (forward reference)
            title_marked: Whether title is specially marked (default: False)
            source: Source description (default: '')
            title_cmd: Command to generate title (default: '')
            content_cmd: Command to generate content (default: '')
        """
        self.buid = buid
        self.label = label
        self.content = content
        self.header = danotes.model.Header(self)
        self.links_target = danotes.model.LinksTarget(self)
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
                self.links_target.append(danotes.model.LinkTarget(label, iid))
        return self

    ## Test Methods -------------------
    def is_path(self) -> bool:
        try:
            # Attempt to create a Path object (validates path syntax)
            Path(self.source)
            return True
        except (TypeError, ValueError):
            # Catches illegal paths (e.g., containing null bytes)
            return False

    def is_web_url(self) -> bool:
        return bool(re.match(r'^(http|https|ftp)://', self.source))

    def is_egb(self):
        """
        Return True if is a EGB Externally Generated Block
        Everything will be considered EGB except directory paths or no source
        """
        if not self.source:
            return False
        if self.is_path():
            return False
        else:
            return True



    ## Helper Methods -----------------
    def get_next_available_iid(self) -> str:
        """Get the next available iid for a Link"""
        if len(self.links_target):
            iid = self.links_target[-1].iid
        else:
            iid = '0'
        iid = danotes.model.get_next_uid(iid)

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

    def update_content(self):
        """
        Update the Content text :
            - for a EGB will check self.source self.title_cmd self.content_cmd
        And update the content accordingly
        """
        cmd = self.source
        process = subprocess.run(cmd, shell = True, capture_output= True, text = True)

        # Create Content object directly from the processed lines
#        self.content = danotes.model.Content(process.stdout.splitlines())
        self.content.extend(process.stdout.splitlines())

            #            line.strip() for line in process.stdout.splitlines() if line.strip()
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
