from search import joyusearch
from search import keywordsearch
import argparse


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(prog='JavDB Craw', usage='%(prog)s [options]')
    parser.add_argument('-m', '--mode', choices=['joyu', 'keyword'],default='keyword' ,help="search mode, joyu or keyword")
    parser.add_argument('-d', '--detail', action='store_true', help="whether or not if you want verbose info")
    parser.add_argument('-p', '--pages' , help="How many pages you wanna search (a page contains roughly 40 entries)")
    args = parser.parse_args()
    
    if args.pages:
        PAGE = int(args.pages)
    else:
        PAGE = 50
    
    if args.mode == 'keyword':
        keywordsearch(DETAIL=args.detail, MAX_PAGE=PAGE)
        
    if args.mode == 'joyu':
        joyusearch(DETAIL=args.detail, MAX_PAGE=PAGE)