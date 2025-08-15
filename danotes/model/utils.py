"""
Cross-project utility functions (stateless helpers)
"""

import re
import json
import pyfiglet
from pathlib import Path
from pathlib import PurePath
import os
from typing import Self
import yaml
import danotes.model
import urllib.parse
import subprocess


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


def is_a_dir_path(path_str: str) -> bool:
    """Check if a string looks like a directory path (without filesystem checks)."""
    # Manually check for trailing slash (PurePath strips it)
    return path_str.endswith('/') or path_str.endswith('\\')

def is_url(string: str) -> bool:
    """Basic check if the string is a URL."""
    return bool(re.match(r'^(?:http|https|ftp)://\S+\.\S+$', string))


def index_file(url: str, path: str) -> tuple[Path, str]:
    """
    Download a file from a URL to a local directory structure under DOCU_PATH.
    Creates necessary subdirectories if they don't exist.

    Args:
        url (str): The URL of the file to download.
        path (str): Base path for downloads.

    Returns:
        tuple[Path, str]: (download_directory, filename)
    """
    # Parse URL and handle filename
    parsed_url = urllib.parse.urlparse(url)
    url_path = f"{parsed_url.netloc}/{parsed_url.path.lstrip('/')}"


    # Split into directory path and filename
    *dirparts, last_part = url_path.split('/') if url_path else []
    dirpath = '/'.join(dirparts)
    filename = last_part or "index.html"

    # Create base paths using pathlib
    base_path = Path(path).parent / Path(path).stem
    downloaded_path = base_path / "downloaded"

    # Create the full target directory path
    full_dirpath = downloaded_path / dirpath
    full_dirpath.mkdir(parents=True, exist_ok=True)

    # Construct the wget command
    cmd = [
        "wget",
        "-nc",  # No-clobber
        "--adjust-extension",
        f"--directory-prefix={full_dirpath}",
        url
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully downloaded {url} to {full_dirpath/filename}")
        return (full_dirpath, filename)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {url}: {e.stderr}")
        raise  # Re-raise the exception for the caller to handle



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

__all__ = [ 'is_valid_dan_format' , 'append_after_third_last_line', 'get_next_uid', 'transform_legacy_title', 'check_yaml_line', 'is_a_dir_path', 'is_url', 'index_file']
