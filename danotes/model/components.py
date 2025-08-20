"""
Rest of Classes Implementations
"""

import re
import json
import pyfiglet
from pathlib import Path
import os
from typing import Self
import yaml
import danotes.model


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
            lines.pop()

        ## Append the EGB info
        if self.block.source:
            output.append(f'source: "{self.block.source}"')
        if self.block.title_cmd:
            output.append(f'title_cmd: "{self.block.title_cmd}"')
        if self.block.content_cmd:
            output.append(f'content_cmd: "{self.block.content_cmd}"')
        if self.block.filters:
            output.append(f'filters: "{self.block.filters}"')


        output.append('')
        output.append('')

        return '\n'.join(output)

class Content(list):
    """List of the lines containing the content of a Block."""
    def to_string(self) -> str:
        """Get the Content as a contiguous string."""
        return '\n'.join(self)

    def shift_links_one_buid(self) :
        """
        Shift all the links in content from BUID , to BUID+1 , either link sources
        to link targets. 
        This is to be used in danotes file migrate
        This is to match with the shift in BUID done to the Block Tags
        """

        for i, line in enumerate(self):  # Track index with enumerate()
            # Shift Link Sources
            matches = re.findall(r'<L=([a-zA-Z0-9]*)', line)
            if matches:
                for match in matches:
                    buid = danotes.model.get_next_uid(match)
                    pattern = fr'(?<=<L=){re.escape(match)}'
                    line = re.sub(pattern, buid, line)  # Update line
            
            # Shift Link Targets (same approach)
            matches = re.findall(r'<I=([a-zA-Z0-9]*)', line)
            if matches:
                for match in matches:
                    buid = danotes.model.get_next_uid(match)
                    pattern = fr'(?<=<I=){re.escape(match)}'
                    line = re.sub(pattern, buid, line)
            
            self[i] = line  # Update the list with modified line
        return self



__all__ = [ 'Header', 'Content']
