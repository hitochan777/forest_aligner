#!/usr/bin/env python3

import argparse

def combineLine(sline, spline):
    if sline == "":
        sset = set()
    else:
        sset = set(sline.split(" "))

    if spline == "":
        spset = set()
    else:
        spset = set(spline.split(" "))

    result = []
    pset = spset - sset
    for element in sset:
        result.append("%s[%s]" % (element, "sure"))

    for element in pset:
        result.append("%s[%s]" % (element, "possible"))

    return " ".join(result)

def combine(sure, surePossible):
    with open(sure, "r") as s, open(surePossible, "r") as sp:
        while True:
            sline = s.readline()
            spline = sp.readline()
            if sline == "" or spline == "":
                break

            sline = sline.strip()
            spline = spline.strip()
            spset = set()
            print(combineLine(sline, spline))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    This scripts combine two files containing sure alignments and sure-possbile alignments.
    Each line in each file must have the form 
    i1-j1 i2-j2 ...
    which means i1-th word in a source sentence is aligned to j1-th word in a target sentence and so on...
    Running this script will generate a file of the form
    i1-j1[S] i2-j2[P] ...
    where S and P represents Sure and Possible alignments respectively.
""")

    parser.add_argument('sure', type=str, help='an integer for the accumulator')
    parser.add_argument('surePossible', type=str, help='sum the integers (default: find the max)')

    args = parser.parse_args()
    combine(args.sure, args.surePossible)  
