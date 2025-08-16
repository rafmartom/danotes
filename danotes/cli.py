import argparse
import sys
from .handlers.block import *
from .handlers.link import *
from .handlers.file import *


## ----------------------------------------------------------------------------
# @section TRAMPOLINE_FUNCTIONS
# @description This functions are defined so the CLI Prints out the return 
#   statement of the library functions

def cli_file_new(args):
    result = file_new(path=args.path, json=args.json, text=args.text)
    if result is not None:
        print(result, end='')

def cli_file_append(args):
    # Handle stdin if no query provided
    if args.query is None and not sys.stdin.isatty():
        args.query = sys.stdin.read()

    # Check if query is still None or empty/whitespace
    if not args.query or args.query.strip() == "":
        print("Error: Not valid parameters or insufficient parameters.", file=sys.stderr)
        sys.exit(1)

    result = file_append(path=args.path, query=args.query)
    if result is not None:
        print(result, end='')

def cli_file_update_toc(args):
    result = file_update_toc(path=args.path)
    if result is not None:
        print(result, end='')

def cli_file_update_notoc(args):
    result = file_update_notoc(path=args.path)
    if result is not None:
        print(result, end='')


def cli_file_refresh(args):
    result = file_refresh(path=args.path)
    if result is not None:
        print(result, end='')

def cli_file_migrate(args):
    result = file_migrate(path=args.path)
    if result is not None:
        print(result, end='')



def cli_block_write(args):
    # Handle stdin if no query provided
    if args.query is None and not sys.stdin.isatty():
        args.query = sys.stdin.read()

    # Use default "Unnamed Article" if new_label is None
    new_label = args.new_label if args.new_label is not None else "Unnamed Article"

    result = block_write(path=args.path, buid=args.buid, query=args.query, new_label=new_label, source=args.source, json=args.json, text=args.text)
    if result is not None:
        print(result, end='')

def cli_block_show(args):
    result = block_show(path=args.path, buid=args.buid, label=args.label, json=args.json, text=args.text)
    if result is not None:
        print(result, end='')

def cli_block_source(args):
    result = block_source(path=args.path, buid=args.buid, source=args.source, title=args.title, content=args.content, filters=args.filters, json=args.json, text=args.text)
    if result is not None:
        print(result, end='')


def cli_link_write(args):
    # Use default "Unnamed Article" if new_label is None
    new_label = args.new_label if args.new_label is not None else "NewLink"

    result = link_write(path=args.path, buid=args.buid, uuid=args.uuid, new_label=new_label, json=args.json, text=args.text)
    if result is not None:
        print(result, end='')

def cli_link_show(args):
    result = link_show(path=args.path, buid=args.buid, uuid=args.uuid, label=args.label, json=args.json, text=args.text)
    if result is not None:
        print(result, end='')


## EOF EOF EOF TRAMPOLINE_FUNCTIONS 
## ----------------------------------------------------------------------------



def main():
    ## ----------------------------------------------------------------------------
    # @section TOP_LEVEL_PARSER

    parser = argparse.ArgumentParser(
        prog="danotes",
        description="""
        danotes: .dan format notes writer

        CLI Interface Porcelain Commands (most used commands for users):

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

          # (For EGB) Update a certain EGB block acording to source
          danotes block source test-sample/new-format.dan --buid 6

          # (For EGB) Update all EGB blocks according to their sources
          danotes block source test-sample/new-format.dan

          # (For EGB) Create a new EGB block with a certain source

          ## For webs
          danotes block source test-sample/new-format.dan --source "https://requests.readthedocs.io/en/latest/" --title "h1" --content "section" --filters "helloworld"

          ## For readable files
          danotes block source test-sample/new-format.dan --source "/etc/hostname"

          ## For man pages
          danotes block source test-sample/new-format.dan --source "man true"  --title "true"
          ## For help
          danotes block source test-sample/new-format.dan --source "true --help" 
          ## For cmd's (you need to specify --title)
          danotes block source test-sample/new-format.dan --source "hostnamectl | grep -E 'Operating System|Kernel|Architecture'" --title "Operative System Keynel Architecture"


          # Update the Block Toc and the file 
          danotes file update toc test-sample/file.dan
          danotes block write test-sample/file.dan

          # Update file without Toc Block and not individual Block Toc
          danotes file update notoc test-sample/file.dan

        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Top-level command")


    ## EOF EOF EOF TOP_LEVEL_PARSER 
    ## ----------------------------------------------------------------------------


    ## ----------------------------------------------------------------------------
    # @section FILE
    # @description Description

    file_parser = subparsers.add_parser("file", help="Dan file Operations")
    file_subparsers = file_parser.add_subparsers(dest="subcommand", required=True)


    # file new
    file_new_parser = file_subparsers.add_parser("new", help=file_new.__doc__, description=file_new.__doc__)
    file_new_parser.add_argument("path", help="Input file")

    file_new_parser_outputtype = file_new_parser.add_mutually_exclusive_group()
    file_new_parser_outputtype.add_argument("--json", help="Output to stdout as Danom Object", action="store_true")
    file_new_parser_outputtype.add_argument("--text", help="Output to stdout as formated dan text", action="store_true")


    # file append
    file_append_parser = file_subparsers.add_parser("append", help=file_append.__doc__, description=file_append.__doc__)
    file_append_parser.add_argument("path", help="Input file")

    file_append_parser.add_argument("-q", "--query", help="Text to Input (If not present defaults to stdin)")

    # file refresh
    file_refresh_parser = file_subparsers.add_parser("refresh", help=file_refresh.__doc__, description=file_refresh.__doc__)
    file_refresh_parser.add_argument("path", help="Input file")


    # file update (subcommand group)
    file_update_parser = file_subparsers.add_parser("update", help="Update operations")
    file_update_subparsers = file_update_parser.add_subparsers(dest="update_target", required=True)

    # file update toc
    file_update_toc_parser = file_update_subparsers.add_parser("toc", help="Update TOC")
    file_update_toc_parser.add_argument("path", help="Input file")

    # file update toc
    file_update_notoc_parser = file_update_subparsers.add_parser("notoc", help="Whole file except the Toc Block,for each file no Block Toc will be generated")
    file_update_notoc_parser.add_argument("path", help="Input file")

    # file migrate
    file_migrate_parser = file_subparsers.add_parser("migrate", help=file_migrate.__doc__, description=file_migrate.__doc__)
    file_migrate_parser.add_argument("path", help="Input file")


    ## EOF EOF EOF FILE 
    ## ----------------------------------------------------------------------------



    ## ----------------------------------------------------------------------------
    # @section BLOCK

    block_parser = subparsers.add_parser("block", help="Dan Block Objects Operations")
    block_subparsers = block_parser.add_subparsers(dest="subcommand", required=True)


    # block write
    block_write_parser = block_subparsers.add_parser("write", help=block_write.__doc__, description=block_write.__doc__)

    block_write_parser_outputtype = block_write_parser.add_mutually_exclusive_group()
    block_write_parser_outputtype.add_argument("--json", help="Output to stdout as Danom Object", action="store_true")
    block_write_parser_outputtype.add_argument("--text", help="Output to stdout as formated dan text", action="store_true")

    block_write_parser.add_argument("-b", "--buid", help="Target Block by buid")


    block_write_parser.add_argument("--source", help="Path source of the Block (for tree hierarchy)")
    block_write_parser.add_argument("-q", "--query", help="Text to Input (If not present defaults to stdin)")
    block_write_parser.add_argument("-n", "--new-label", help="Text Label of the New Block Target (for when creating a new block)")


    block_write_parser.add_argument("path", help="Input file")

    # block show
    block_show_parser = block_subparsers.add_parser("show", help=block_show.__doc__, description=block_show.__doc__)
    block_show_parser_outputtype = block_show_parser.add_mutually_exclusive_group()
    block_show_parser_outputtype.add_argument("--json", help="Output to stdout as Danom Object", action="store_true")
    block_show_parser_outputtype.add_argument("--text", help="Output to stdout as formated dan text", action="store_true")

    block_show_parser_filterby = block_show_parser.add_mutually_exclusive_group()
    block_show_parser_filterby.add_argument("-b", "--buid", help="Target Block by buid")
    block_show_parser_filterby.add_argument("-l", "--label", help="Target Block by label (must be unambiguous)")

    block_show_parser.add_argument("path", help="Input file")


    # block source
    block_source_parser = block_subparsers.add_parser("source", help=block_source.__doc__, description=block_source.__doc__)
    block_source_parser_outputtype = block_source_parser.add_mutually_exclusive_group()
    block_source_parser_outputtype.add_argument("--json", help="Output to stdout as Danom Object", action="store_true")
    block_source_parser_outputtype.add_argument("--text", help="Output to stdout as formated dan text", action="store_true")

    block_source_parser_filterby = block_source_parser.add_mutually_exclusive_group()
    block_source_parser_filterby.add_argument("-b", "--buid", help="Target Block by buid")

    block_source_parser.add_argument("path", help="Input file")

    block_source_parser.add_argument("--source", help="Path/URL/cmd source of the Generated Content")
    block_source_parser.add_argument("--title", help="Title parsing rules")
    block_source_parser.add_argument("--content", help="Content parsing rules")
    block_source_parser.add_argument("--filters", help="Pandoc filters to be applied (comma separated string to be read from ./danotes/filters/user/ or ./danotes/filters/builtin/")
    ## EOF EOF EOF BLOCK 
    ## ----------------------------------------------------------------------------




    ## ----------------------------------------------------------------------------
    # @section LINK

    link_parser = subparsers.add_parser("link", help="Dan Link Objects Operations")
    link_subparsers = link_parser.add_subparsers(dest="subcommand", required=True)


    # link write
    link_write_parser = link_subparsers.add_parser("write", help=link_write.__doc__, description=link_write.__doc__)

    link_write_parser_outputtype = link_write_parser.add_mutually_exclusive_group()
    link_write_parser_outputtype.add_argument("--json", help="Output to stdout as Danom Object", action="store_true")
    link_write_parser_outputtype.add_argument("--text", help="Output to stdout as formated dan text", action="store_true")

    link_write_parser_filterby =  link_write_parser.add_mutually_exclusive_group()
    link_write_parser_filterby.add_argument("-b", "--buid", help="Target Block by buid")
    link_write_parser_filterby.add_argument("-u", "--uuid", help="[Experimental] Select a determined uuid if it does exist it will substitute the previous link")

    link_write_parser.add_argument("path", help="File to be modified , if not set would output to stdout")

    link_write_parser.add_argument("-n", "--new-label", help="Text Label of the New Link")


    # link show
    link_show_parser = link_subparsers.add_parser("show", help=link_show.__doc__, description=link_show.__doc__)

    link_show_parser_outputtype = link_show_parser.add_mutually_exclusive_group()
    link_show_parser_outputtype.add_argument("--json", help="Output to stdout as Danom Object", action="store_true")
    link_show_parser_outputtype.add_argument("--text", help="Output to stdout as formated dan text", action="store_true")

    link_show_parser_filterby = link_show_parser.add_mutually_exclusive_group()
    link_show_parser_filterby.add_argument("-b", "--buid", help="Target Link buid")
    link_show_parser_filterby.add_argument("-u", "--uuid", help="Target Link uuid")
    link_show_parser_filterby.add_argument("-l", "--label", help="[Experimental] Target Link by Block label (must be unambiguous)")


    link_show_parser.add_argument("path", help="Input file")


    ## EOF EOF EOF LINK 
    ## ----------------------------------------------------------------------------




    ## ----------------------------------------------------------------------------
    # @section PARSE_AND_DISPATCH

    args = parser.parse_args()

    if args.command == "file":
        if args.subcommand == "new":
            cli_file_new(args)
        if args.subcommand == "append":
            cli_file_append(args)
        if args.subcommand == "update":
            if args.update_target == "toc":
                cli_file_update_toc(args)
            if args.update_target == "notoc":
                cli_file_update_notoc(args)
        if args.subcommand == "refresh":
            cli_file_refresh(args)
        if args.subcommand == "migrate":
            cli_file_migrate(args)


    if args.command == "block":
        if args.subcommand == "write":
            cli_block_write(args)
        elif args.subcommand == "show":
            cli_block_show(args)
        elif args.subcommand == "source":
            cli_block_source(args)


    elif args.command == "link":
        if args.subcommand == "write":
            cli_link_write(args)
        elif args.subcommand == "show":
            cli_link_show(args)


    ## EOF EOF EOF PARSE_AND_DISPATCH 
    ## ----------------------------------------------------------------------------


if __name__ == "__main__":
    main()
