import argparse
import sys
from .handlers.block import *
from .handlers.link import *


## ----------------------------------------------------------------------------
# @section TRAMPOLINE_FUNCTIONS
# @description This functions are defined so the CLI Prints out the return 
#   statement of the library functions


def cli_block_write(args):
    # Handle stdin if no query provided
    if args.query is None and not sys.stdin.isatty():
        args.query = sys.stdin.read()

    result = block_write(path=args.path, buid=args.buid, query=args.query, new_label=args.new_label, json=args.json, text=args.text)
    if result is not None:
        print(result, end='')

def cli_block_show(args):
    result = block_show(path=args.path, buid=args.buid, label=args.label, json=args.json, text=args.text)
    if result is not None:
        print(result, end='')

def cli_link_write(args):
    result = link_write(path=args.path, buid=args.buid, uuid=args.uuid, label=args.label, json=args.json, text=args.text)
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

        Most Common Uses:

          # Start a new document from the scratch
          danotes block write file.dan --buid 0

          # Start a new article
          danotes block write file.dan --label "My New Article"

          Output: 4f

          # Append some text to the new article
          danotes block write file.dan --buid 4f --query "Here is some text"

          # Append some text to the new article (stdin)
          echo "Here is some other text" | danotes block write file.dan --buid 4f

          # Append a Dan Link to that article
          danotes link write file.dan --buid 4f --label "New Link"

          Output: 1

          # Update the whole Document
          danotes block write file.dan
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Top-level command")


    ## EOF EOF EOF TOP_LEVEL_PARSER 
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

    link_write_parser_filterby =  link_write_parser.add_mutually_exclusive_group(required=True)
    link_write_parser_filterby.add_argument("-b", "--buid", help="Target Block by buid")
    link_write_parser_filterby.add_argument("-u", "--uuid", help="[Experimental] Select a determined uuid if it does exist it will substitute the previous link")

    link_write_parser.add_argument("path", help="File to be modified , if not set would output to stdout")


    link_write_parser.add_argument("-l", "--label", help="Text Label of the Link (If not present defaults to stdin)")


    # link show
    link_show_parser = link_subparsers.add_parser("show", help=link_show.__doc__, description=link_show.__doc__)

    link_show_parser_outputtype = link_show_parser.add_mutually_exclusive_group()
    link_show_parser_outputtype.add_argument("--json", help="Output to stdout as Danom Object", action="store_true")
    link_show_parser_outputtype.add_argument("--text", help="Output to stdout as formated dan text", action="store_true")

    link_show_parser_filterby = link_show_parser.add_mutually_exclusive_group(required=True)
    link_show_parser_filterby.add_argument("-b", "--buid", help="Target Link buid")
    link_show_parser_filterby.add_argument("-u", "--uuid", help="Target Link uuid")
    link_show_parser_filterby.add_argument("-l", "--label", help="[Experimental] Target Link by Block label (must be unambiguous)")


    link_show_parser.add_argument("path", help="Input file")


    ## EOF EOF EOF LINK 
    ## ----------------------------------------------------------------------------




    ## ----------------------------------------------------------------------------
    # @section PARSE_AND_DISPATCH

    args = parser.parse_args()

    if args.command == "block":
        if args.subcommand == "write":
            cli_block_write(args)

        elif args.subcommand == "show":
            cli_block_show(args)

    elif args.command == "link":
        if args.subcommand == "write":
            cli_link_write(args)
        elif args.subcommand == "show":
            cli_link_show(args)


    ## EOF EOF EOF PARSE_AND_DISPATCH 
    ## ----------------------------------------------------------------------------


if __name__ == "__main__":
    main()
