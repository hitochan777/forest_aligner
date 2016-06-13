#!/usr/bin/env python3

import argparse

def tag(sure, tag = "sure"):
    buf = []
    with open(sure, "r") as s:
        for line in s:
            links = line.strip().split(" ")
            buf.append(" ".join(map(lambda link: "%s[%s]" % (link, tag), links)))
        print("\n".join(buf), end = "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    This script tags each alignment link with 'sure' tag .
    Each line in each file must have the form 
    i1-j1 i2-j2 ...
    which means i1-th word in a source sentence is aligned to j1-th word in a target sentence and so on...
    Running this script will generate a file of the form
    i1-j1[S] i2-j2[S] ...
""")

    parser.add_argument('sure', type=str, help='an integer for the accumulator')
    parser.add_argument('--tag', type=str, default='sure', help='tag; default = sure')
    args = parser.parse_args()
    tag(args.sure)
