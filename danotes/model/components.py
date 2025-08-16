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

        output.append('')
        output.append('')

        return '\n'.join(output)

class Content(list):
    """List of the lines containing the content of a Block."""
    def to_string(self) -> str:
        """Get the Content as a contiguous string."""
        return '\n'.join(self)

__all__ = [ 'Header', 'Content']
