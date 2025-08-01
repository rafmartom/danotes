from .handlers.block import *
from .handlers.link import *
from .handlers.file import *

__all__ = ['file_new', 'file_append', 'block_write', 'block_show', 'link_write', 'link_show']

## Momentary snippet for working directly with the danom interactively          ## DEBUGGING

all_core = [ 'Block', 'Danom', 'Content', 'Header', 'LinkTarget', 'LinksTarget', 'is_valid_dan_format' , 'append_after_third_last_line', 'get_next_uid', 'transform_legacy_title']

__all__.extend(all_core)                                                        ## DEBUGGING
