from search import joyusearch, better_joyusearch
from search import keywordsearch, better_keywordsearch
from search import listsearch
import argparse


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(prog='JavDB Craw', usage='%(prog)s [options]')
    parser.add_argument('-m', '--mode', choices=['joyu', 'keyword','list'],default='keyword' ,help="search mode, joyu or keyword")
    parser.add_argument('-d', '--detail', action='store_true', help="whether or not if you want verbose info")
    parser.add_argument('-p', '--pages' , help="How many pages you wanna search (a page contains roughly 40 entries)")
    args = parser.parse_args()
    
    if args.pages:
        PAGE = int(args.pages)
    else:
        PAGE = 50
    
    if args.mode == 'keyword':
        better_keywordsearch(DETAIL=args.detail, MAX_PAGE=PAGE)
        
    if args.mode == 'joyu':
        better_joyusearch(DETAIL=args.detail, MAX_PAGE=PAGE)
        
    if args.mode == 'list':
        listsearch(DETAIL==args.detail)