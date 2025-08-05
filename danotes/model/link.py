"""
Link-related classes.
"""

import re
import json
import pyfiglet
from pathlib import Path
import os
from typing import Self
import yaml
import danotes.model


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
