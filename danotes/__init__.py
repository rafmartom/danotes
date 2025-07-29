from .handlers.block import *
from .handlers.link import *
from .handlers.file import *

__all__ = ['file_new', 'file_append', 'block_write', 'block_show', 'link_write', 'link_show']

## Momentary snippet for working directly with the danom interactively          ## DEBUGGING

all_core = [ 'Block', 'Danom', 'Content', 'Header', 'is_valid_dan_format' , 'append_after_third_last_line' ]   ## DEBUGGING
__all__.extend(all_core)                                                        ## DEBUGGING
