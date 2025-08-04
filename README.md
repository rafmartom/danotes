# danotes

Standalone program to manipulate Notes files on .dan format from vim-dan


## Developer note

The project is under current development and basic functionalities are not yet working.
At the moment and for allowing not breaking backwards compatibility with `.dan` files , it is using `.dano` files as extension.

## Installation

```
python3 -m venv venv
pip install -e .
danotes --help
```

## Help System

Use the help system to guide you through the CLI Interface

```
danotes --help
danotes block --help
danotes block write --help
```

## System Explained


`danotes` documents are formed of succesive blocks, each block has asigned a unique id **buid** and a **label** which doesn't have to be unique.
The first two blocks `buid = 0' and `buid = 1` are unique:

- Block `buid = 0` : Danotes Header
- Block `buid = 1` : General TOC 
- Block `buid = 2` , Block `buid= 3` , ... : Article blocks

Each block starts with `< B={buid}>{label}$` and finnish with a `</B>` followed by a horizontal line made of `=`
Note: the buid is a combination of ever increasing alphanumeric chars `[a-zA-Z0-9]+`

### Danotes Header

Block `buid = 0` is the header of the document. Formed of a Title of the Document in ASCII art and a `yaml` syntaxed set of variables which is used for document metadata storage, most of this metadata can be used for different purposes such as categorize the document, see when it was generated (if it comes from an automated documentation parser such as `vim-dan-generator`), or help the text editor syntax highlight.

Example

```
<B=0>Danotes Header
           _       _                                      
  __ _  __| | ___ | |__   ___       _ __  _ __  _ __ ___  
 / _` |/ _` |/ _ \| '_ \ / _ \_____| '_ \| '_ \| '__/ _ \ 
| (_| | (_| | (_) | |_) |  __/_____| |_) | |_) | | | (_) |
 \__,_|\__,_|\___/|_.__/ \___|     | .__/| .__/|_|  \___/ 
                                   |_|   |_|              
                                                                           
         88                                                                
         88                                     ,d                         
         88                                     88                         
 ,adPPYb,88 ,adPPYYba, 8b,dPPYba,   ,adPPYba, MM88MMM ,adPPYba, ,adPPYba,  
a8"    `Y88 ""     `Y8 88P'   `"8a a8"     "8a  88   a8P_____88 I8[    ""  
8b       88 ,adPPPPP88 88       88 8b       d8  88   8PP"""""""  `"Y8ba,   
"8a,   ,d88 88,    ,88 88       88 "8a,   ,a8"  88,  "8b,   ,aa aa    ]8I  
 `"8bbdP"Y8 `"8bbdP"Y8 88       88  `"YbbdP"'   "Y888 `"Ybbd8"' `"YbbdP"'  


The following lines are used by danotes, modify them only if you know !

dan_ext_list: ["javascript"]
dan_kw_question_list: ["^Description"]
dan_kw_nontext_list: ["^Parameters", "^Type"]
dan_kw_linenr_list: ["^Parameter "]
dan_kw_warningmsg_list: ["^Returns"]
dan_kw_colorcolumn_list: []
dan_kw_underlined_list: []
dan_kw_preproc_list: []
dan_kw_comment_list: []
dan_kw_identifier_list: []
dan_kw_ignore_list: []
dan_kw_statement_list: []
dan_kw_cursorline_list: []
dan_kw_tabline_list: []
dan_wrap_lines: 105
dan_indexed_from: "https://ppro-scripting.docsforadobe.dev/"
dan_parsed_on: []
dan_title: "adobe-ppro"
dan_description: "" 
dan_tags: []
</B>
=========================================================================================================
```

### General TOC

Block `buid = 1` is the General TOC of the document. Full of **DAN link sources** which let you navigate to the rest of the blocks quickly.

Example

```
<B=1>General TOC
 _____ ___   ____
|_   _/ _ \ / ___|
  | || | | | |
  | || |_| | |___
  |_| \___/ \____|

- <L=0>Table of Contents TOC</L>
- <L=1>First Article</L>
- <L=2>Second Article</L>

</B><L=1>To General TOC</L>
=========================================================================================================
```

### Article Blocks

From `block = 2` onwards they are all Article blocks, they share the same structure:
- The label is shown in ASCII art at the top.
- An Article specific TOC (until `<T>`)
- The Content part (can hold plain text and DAN Inline Objects)
- The lower boundary of the block `</B>...` followed by a horizontal line of equal signs `=`

```
<B=2>First Article
 _____ _          _        _         _   _      _
|  ___(_)_ __ ___| |_     / \   _ __| |_(_) ___| | ___
| |_  | | '__/ __| __|   / _ \ | '__| __| |/ __| |/ _ \
|  _| | | |  \__ \ |_   / ___ \| |  | |_| | (__| |  __/
|_|   |_|_|  |___/\__| /_/   \_\_|   \__|_|\___|_|\___|


- <L=1#1>Part A</L>
- <L=1#2>Part B</L>
- <L=1#3>Part C</L>
<T>

<I=1#1>Part A</I>
Some text here explaining something

```javascript
var myVar = "this code";
console.log(myVar)
```

<I=1#2>Part B</I>
<I=1#3>Part C</I>

</B><L=1>To General TOC</L> | <L=2>To Article Top</L>
=========================================================================================================
<B=3>Second Article
 ____                           _      _         _   _      _
/ ___|  ___  ___ ___  _ __   __| |    / \   _ __| |_(_) ___| | ___
\___ \ / _ \/ __/ _ \| '_ \ / _` |   / _ \ | '__| __| |/ __| |/ _ \
 ___) |  __/ (_| (_) | | | | (_| |  / ___ \| |  | |_| | (__| |  __/
|____/ \___|\___\___/|_| |_|\__,_| /_/   \_\_|   \__|_|\___|_|\___|


- <L=2#1>Part A</L>
- <L=2#2>Part B</L>
<T>

<I=2#1>Part A</I>
<I=2#2>Part B</I>

</B><L=1>To General TOC</L> | <L=3>To Article Top</L>
=========================================================================================================
```

The Article TOC is Similar to the General TOC, but this allow you quick navigation to the **LinkTarget**'s made of `< I={buid}#{iid}>{label}`
There are also `Codeblocks` which take the syntax of markdown specifying the filetype, so the text-processor can syntax highlight their contents accordingly.

Note that the Inline Links have a New Component `iid` **Inline ID** , which is not unique across the Document, but across the article. Put together with the hash, they will be recognised by `ctags` as placeholders for quick navigation.



## Purpose of .dan documents

This documents have originated for quick navigation of big documentations, dumped into one text file offering:

- Tags navigation emulating html hyperlinks.
- Basic Syntax Highlighting capabilities.

This can result in extremely light-weight documents that can store huge documentations, with a Web Feel, extremely fast to navigate in.
Originated for the use with `vim`, and based on `vimhelp` format but extensible to any `ctags`-aware text-editor.
As the markup is minimum, it can be visualized without any special text-editor, just as plain un-highlighted un-linked text.

Created for automated Indexing of Documentations with [vim-dan-generator](https://github.com/rafmartom/vim-dan-generator), extended now for the use of personal notes.

With `danotes` you can pipe text coming from any source and append it as new blocks, new text into an existing document. Doing it manually, integrated in your text editor, creating new Links, new Articles, or Batch Automate from the `CLI`.



## Program outline


User should be able to take either a Block or a Inline  and perform one of these action; Show or Write
The most important commands you can give is:


```
stdin | danotes block write --buid <buid> <file.dan>
```
If --buid is non-existent will create the Title and lower boundaries of the Article , `-l  <label>` is preferable to use on there. Stdin will be text within the article.
You cannot write to --buid 0 or 1
If --json or --text , the output will be to stdout



```
danotes block show --buid <buid> --json --text
```
If no --json or --text is selected , will update the block in place
 -l can be used instead of --buid, but have to be unambiguous.
If no buid , will default to all the document iterating from 0 to last


```
danotes block update --buid <buid>
```
It is an alias of `danotes block show ` without --json or --text. So will modify that certain block.
Will update in place the determined block (useful to refresh block 0, 1, or any block for the TOC) , if no --buid is given will iterate all the document from <buid>=0 to last.


```
dannotes link write -b <buid>
```
Will create a link in a certain article on the next available -i <iid>
If --json or --text is given output  will be showing it to stdout (in that case -id <iid> is required)

```
dannotes link show -b <buid> -i <iid> --text --json
```
--text will be the output by default and will give out the <label> otherwise will output the <json> object



## Usage

### CLI Interface

CLI Interface Porcelain Commands (most used commands for users):
```
# Start a new document from the scratch
danotes file new test-sample/file.dan

# Start a new article
danotes block write test-sample/file.dan --new-label "My New Article"

# Append some text to the new article
echo -e "Here is\nsome text" | danotes block write test-sample/file.dan
printf "Here is" | danotes block write test-sample/file.dan
printf "Contiguous text" | danotes block write test-sample/file.dan

# Append some text to the new article via --query (only one line text supported), you can specify the buid too
danotes block write test-sample/file.dan --buid 2 --query "Here is some text"

# Append a Dan Link to that article
danotes link write test-sample/file.dan --new-label "New Link"

# Update the Block Toc and the file 
danotes file update toc
```

### Library Usage


```
python3 -i -c 'from danotes import *'


# Start a new document from the scratch
danom = Danom()
path = 'test-sample/file.dan'
danom.create_new_header_block(path)
danom.create_new_block('1', "Document TOC")

# Start a new article
block = danom.create_new_block(new_label="Article Name")

# Append some text to the new article
block.append_query('Here is\nsome text')

# Append some text to the last article
danom[-1].append_query('Here is\nsome text')


# Append a Dan Link to that last article
block.append_link('New Link')

# Save to a file
danom.to_file('test-sample/file.dan')
```


## Externally generated Blocks


With `danotes` `.dan` files you have also the ability to create Blocks that generate from external sources.
We have seen that we can create new blocks and write any notes there within those Blocks.
Now also you can have some blocks that are generated from external sources, meaning this Blocks can be URL's to certain resources, or local references to certain files you want to get the information from.
These Blocks are meant to only be used for reference. After writting them on the .dan file you shoudln't be altering them, because all the changes are prone to be deleted upon an update on the sources.
May the `(X)` annotation tags persist accross updates only. But not even that.
If you use them you are advised that you may loose those tags.


For these we have added three properties. The `source` the `title_cmd` and the `content_cmd`.

I will refer to User Blocks as UBlocks and Externaly Generated Blocks as EGBlocks

### source
If a Block doesn't provide of any, then it is unequivocally a `User Block` UBlock
If the source is a subdir is also a `User Block`
If the source is a file path or a url then is a EGBlock

Example User Block
```
<B=3>Second Article (X)
 ____                           _      _         _   _      _
/ ___|  ___  ___ ___  _ __   __| |    / \   _ __| |_(_) ___| | ___
\___ \ / _ \/ __/ _ \| '_ \ / _` |   / _ \ | '__| __| |/ __| |/ _ \
 ___) |  __/ (_| (_) | | | | (_| |  / ___ \| |  | |_| | (__| |  __/
|____/ \___|\___\___/|_| |_|\__,_| /_/   \_\_|   \__|_|\___|_|\___|

- <L=3#1>Part A</L>
- <L=3#2>Part B</L>
<T>
source: ""

<I=2#1>Part A</I>
<I=2#2>Part B</I>

</B><L=1>To Document TOC</L> | <L=3>Back to Article Top</L>
```

Example EGBlock
```
<B=4>Unnamed Article (X)
 _   _                                      _      _         _   _      _
| | | |_ __  _ __   __ _ _ __ ___   ___  __| |    / \   _ __| |_(_) ___| | ___
| | | | '_ \| '_ \ / _` | '_ ` _ \ / _ \/ _` |   / _ \ | '__| __| |/ __| |/ _ \
| |_| | | | | | | | (_| | | | | | |  __/ (_| |  / ___ \| |  | |_| | (__| |  __/
 \___/|_| |_|_| |_|\__,_|_| |_| |_|\___|\__,_| /_/   \_\_|   \__|_|\___|_|\___|

<T>
source: "./path/to/unnamed.html"
title_cmd: "cat ${FILE} | pup -i 0 --pre 'h1' | pandoc -f html -t plain"
content_cmd: "cat ${FILE} | pup -i 0 --pre 'body' | pandoc -f html -t plain -V dpath=${DPATH} -V title=${TITLE} -V buid=${BUID} -V file_processed=${PATH} -L ${DANP}/indexing-links-target.lua"




</B><L=1>To Document TOC</L> | <L=4>Back to Article Top</L>
```

### title_cmd and content_cmd

These two other variables are used to keep the information of the generation of the title `title_cmd` which generates the Block label
The `content_cmd` is used to generate the content of the Block.

In there you find with `sh` syntax the shortest possible command in order to replicate both title a content

In order to keep this as short as possible we use some conventions such as these special vars:

- `FILE` : Is the local path where the source file will be placed. It is `${DPATH}/${SOURCE}`
- `TITLE` : Only usable in content_cmd , is the result of `title_cmd`
- `LPATH` : Local Path . Expanded where the Document Specific Resources are Stored . It stores resources generated as `title-links-parsed.csv` and `DPATH`, also Specific pandoc-fitlers
- `DPATH` : Download Path. Expanded to the temporary dir where the source files will be downloaded. It is `${LPATH}/downloaded`
- `DANP` : Danotes Path. It is the local path where `danotes` resources are installed. This will be used for pandoc general filters and the like.
- `BUID` : Block User Id , of the current Article, so the Writer can generate Links accordingly.

A coming `danotes-generator` repository, will wrap the creation of `.dan` files with public available resources for certain topics.
Say you want to have a `.dan` file with the `MDN Javascript` documentation, this repository will have scripts to generate that `.dan` file with all the Objects and Methods from their documentation sites. Also there will be a dump file ready to download (so you dont need to Crawl and process them)


## Pending to add in tests of the CLI Handlers and module itself



```
danotes block show test-sample/new-format.dano
python3 -c 'from danotes import *; func_return = block_show("test-sample/new-format.dano") ; print(func_return)'

danotes block show test-sample/new-format.dano --buid 1
python3 -c 'from danotes import *; func_return = block_show("test-sample/new-format.dano", buid="1") ; print(func_return)'

danotes block show test-sample/new-format.dano --buid 1 --json
python3 -c 'from danotes import *; func_return = block_show("test-sample/new-format.dano", buid="1", json=True) ; print(func_return)'

danotes block show test-sample/new-format.dano --text
python3 -c 'from danotes import *; func_return = block_show("test-sample/new-format.dano", text=True) ; print(func_return)'

danotes block show test-sample/new-format.dano --json
python3 -c 'from danotes import *; func_return = block_show("test-sample/new-format.dano", json=True) ; print(func_return)'

danotes block show test-sample/new-format.dano --label 'Document TOC' --text
python3 -c 'from danotes import *; func_return = block_show("test-sample/new-format.dano", label="Table of Contents TOC", text=True) ; print(func_return)'

danotes block show test-sample/new-format.dano --label 'Table of Contents TOC' --json
python3 -c 'from danotes import *; func_return = block_show("test-sample/new-format.dano", label="Table of Contents TOC", json=True) ; print(func_return)'


danotes block write test-sample/new-format.dano --new-label "Articulo Paco"
python3 -c 'from danotes import *; func_return = block_write("test-sample/new-format.dano", new_label="Articulo Pepe") ; print(func_return)'


## Create an Unnamed new Block
danotes block write test-sample/new-format.dano

## Append no text to buid='2' (doesnt have much sense)
danotes block write test-sample/new-format.dano --buid 2 --text

## Append a query to buid='2'
danotes block write test-sample/new-format.dano --buid 2 --query "Some one-liner" --text

## Append a multiline stdin query to buid='2' 
echo -e "Mai\nMultiline\nTrods" | danotes block write test-sample/new-format.dano --buid 2 --text

## Create a new Block, appending a multiline stdin query
echo -e "Mai\nMultiline\nTrods" | danotes block write test-sample/new-format.dano --new-label 'Mai Article' --text


## Append to .dan file in a dumb way (not parsing danom) (will append to last block)
echo -e "Mai\nMultiline\nTrods" | danotes file append test-sample/new-format.dano


## Create the Header and TOC block
danotes file new test-sample/new-file.dano --text
danotes file new test-sample/new-file.dano --json

### Refresh the TOC Block
danotes block write test-sample/new-format.dano --buid 1
# or
danotes file update toc test-sample/new-format.dano

## Parse link target
danotes link show test-sample/new-format.dano --buid 2 --json

## Update links target for all the file
danotes link show test-sample/new-format.dano

## Create a new link
danotes link write test-sample/new-format.dano --new-label 'My link'



## Debugging interactively
python3 -i -c 'from danotes import *'
danom = Danom()
danom.load('test-sample/new-format.dan')
print(danom[2].links_target)

danom.create_new_header_block('test-sample/new-file.dano')


## Local Debugging
gitToTermbin -x "*README.md" -x "*test-sample*"
```
