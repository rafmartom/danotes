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
from bs4 import BeautifulSoup, Comment
from importlib import resources

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
        content_cmd: str = '',
        filters: str = ''
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
        self.filters = filters
    def __repr__(self):
        content_preview = ', '.join([repr(line.strip()) for line in self.content[:3]])
        if len(self.content) > 3:
            content_preview += f', ...(+{len(self.content)-3} more lines)'
        return f"Block(buid='{self.buid}', label='{self.label}', content=[{content_preview}], links_target={repr(self.links_target)}, title_marked='{self.title_marked}', source='{self.source}', title_cmd='{self.title_cmd}', content_cmd='{self.content_cmd}, filters='{self.filters}')"
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

    def update_content(self, path):
        """
        Update the Content text :
            - for a EGB will check self.source self.title_cmd self.content_cmd
        And update the content accordingly
        There is 3 conditions for a existing source to generate an EGB:
            - Run the string and Exit Status 0 . Stdout as content (DANGEROUS Code Injection!!)
            - If the String is an existing local path (if is a text file cat it , if is .html use pandoc)
            - Is a URL (use wget, and if Exit Status 0 , apply pandoc with self.title_cmd , and self.content_cmd)
        """

        ## If it is not an EGB leave it as it is
        if not self.source or danotes.model.is_a_dir_path(self.source) and not danotes.model.is_url(self.source):
            return self
        
        ## Re-instating the content from 0
        self.content = danotes.model.Content()

        process = subprocess.run(self.source, shell = True, capture_output= True, text = True)

        if process.returncode == 0:
            self.content.extend([''])
            self.content.extend(process.stdout.splitlines())
            return self
        else:
            ## Downloading if it is a url
            if danotes.model.is_url(self.source):
                try:
                    download_dir, filename = danotes.model.index_file(self.source, path)
                    file_path = download_dir / filename
                    
                    with open(file_path) as file:
                        soup = BeautifulSoup(file, features="lxml")

                        # Remove all JavaScript (<script> tags)
                        for script in soup.find_all("script"):
                            script.decompose()  # Remove the entire tag

                        # Remove all inline styles and external CSS (<style> tags)
                        for style in soup.find_all("style"):
                            style.decompose()

                        # Remove ALL 'style' attributes from any tag
                        for tag in soup.find_all(True):  # True = match all tags
                            if 'style' in tag.attrs:
                                del tag.attrs['style']

                        # Remove all HTML comments from the soup
                        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                            comment.extract()  # Remove the comment

                        if self.title_cmd:
                            title = soup.select(self.title_cmd)[0].get_text(strip=True)
                        else:
                            title = Path(filename).stem
                        if self.content_cmd:
                            content = soup.select(self.content_cmd)[0]
                        else:
                            content = soup.body

                        if self.filters:
                            filters = self.filters.split(',')
                            filters_cmd = ''

                            for filter_name in filters:
                                # Check user filters first
                                resource = resources.files("danotes.filters.user").joinpath(f"{filter_name}.lua")
                                if resource.is_file():
                                    with resources.as_file(resource) as path:
                                        filters_cmd += f' -L {str(path)}'
                                    continue  # skip checking builtin if found in user

                                # Check builtin filters
                                resource = resources.files("danotes.filters.builtin").joinpath(f"{filter_name}.lua")
                                if resource.is_file():
                                    with resources.as_file(resource) as path:
                                        filters_cmd += f' -L {str(path)}'
                        else:
                            filters_cmd = ''


                    cmd = f'echo "{content}" | pandoc -f html -t plain {filters_cmd}'
                    process = subprocess.run(cmd, shell = True, capture_output= True, text = True)

                    self.label = title

                    self.content.extend([''])
                    self.content.extend(process.stdout.splitlines())
                    return self
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"Failed to download or process file: {e.stderr}") from e
                except FileNotFoundError as e:
                    raise RuntimeError(f"File not found: {file_path}") from e
                except Exception as e:
                    raise RuntimeError(f"Unexpected error processing {self.source}: {str(e)}") from e
            ## Case for local file
            else:
                ## Regularize if it is a relative path
                if not Path(self.source).is_absolute():
                    regularized_path = Path(path).parent.joinpath(Path(self.source))
                else:
                    regularized_path = Path(path).joinpath(Path(self.source))

                if regularized_path.is_file():
                    with open(regularized_path) as file:
                        ## Case that local file an .html
                        if re.match(r'\.(?:html|htm)', Path(self.source).suffix):
                            soup = BeautifulSoup(file, features="lxml")

                            # Remove all JavaScript (<script> tags)
                            for script in soup.find_all("script"):
                                script.decompose()  # Remove the entire tag

                            # Remove all inline styles and external CSS (<style> tags)
                            for style in soup.find_all("style"):
                                style.decompose()

                            # Remove ALL 'style' attributes from any tag
                            for tag in soup.find_all(True):  # True = match all tags
                                if 'style' in tag.attrs:
                                    del tag.attrs['style']

                            # Remove all HTML comments from the soup
                            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                                comment.extract()  # Remove the comment


                            if self.title_cmd:
                                title = soup.select(self.title_cmd)[0].get_text(strip=True)
                            else:
                                title = Path(self.source).stem
                            if self.content_cmd:
                                content = soup.select(self.content_cmd)[0]
                            else:
                                content = soup

                            if self.filters:
                                filters = self.filters.split(',')

                                for filter_name in filters:
                                    # Check user filters first
                                    resource = resources.files("danotes.filters.user").joinpath(f"{filter_name}.lua")
                                    if resource.is_file():
                                        with resources.as_file(resource) as path:
                                            filters_cmd += f' -L {str(path)}'
                                        continue  # skip checking builtin if found in user

                                    # Check builtin filters
                                    resource = resources.files("danotes.filters.builtin").joinpath(f"{filter_name}.lua")
                                    if resource.is_file():
                                        with resources.as_file(resource) as path:
                                            filters_cmd += f' -L {str(path)}'
                            else:
                                filters_cmd = ''


                            cmd = f'echo "{content}" | pandoc -f html -t plain {filters_cmd}'

                            process = subprocess.run(cmd, shell = True, capture_output= True, text = True)
                            
                            self.label = title

                            self.content.extend([''])
                            self.content.extend(process.stdout.splitlines())

                        ## If not dump its content
                        else:
                            if self.title_cmd:
                                title = self.title_cmd
                            else:
                                title = Path(self.source).stem
                            self.label = title
                            self.content.extend([''])
                            self.content.extend(file.read().splitlines())
                        return self
                else:
                    print(f"[Warning]: Was not possible to parse content from {path=} {self.source=}")
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
