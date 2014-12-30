from os import walk
from os.path import split, join
import argparse

from sub_matcher import SubMatcher


def main():
    # Receives arguments from argparse and calls the main matching function
    parser = argparse.ArgumentParser(description='Match sub and video files by season and episode number.')
    parser.add_argument('-r', action='store_true', help='Recurse to subdirectories')
    parser.add_argument('-v', action='store_true', help='Display matching dirs for subs and videos.')
    parser.add_argument('-i', action='store_true',
                        help='Display the elements of a filename as interpreted by the regex.\n \
                             The final argument should be a file name. All other arguments are ignored.')
    parser.add_argument('-n', action='store',
                        help='Standardize all filenames with the string *s* given.\n \
                             All video and subtitle files found will be converted to: *s*.S*xx*E*xx*.*extension*')
    parser.add_argument('match_target', metavar='matchdirname', help='Target directory or file')
    args = parser.parse_args()

    if args.i:
        target_dir = split(args.match_target)[0] if split(args.match_target)[0] else '.'
        matcher = SubMatcher(target_dir, verbose=True)
        print matcher.parse_name(split(args.match_target)[1])
        exit()

    if args.r:
        matcher = SubMatcher(args.match_target, showdir=True)
        matcher.match_subs()
        for root, dirs, files in walk(args.match_target):
            for subdir in dirs:
                matcher.directory = join(root, subdir)
                matcher.match_subs()
        exit()

    matcher = SubMatcher(args.match_target, verbose=args.v, normalized_name=args.n)
    matcher.match_subs()


if __name__ == '__main__':
    main()
