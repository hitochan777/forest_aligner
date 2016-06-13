#!/usr/bin/env python

import svector
import pickle
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
""")
    parser.add_argument('in_weight', type=str, help='in_weight')
    args = parser.parse_args()

    with open(args.in_weight, "rb") as in_weight:
        weights = pickle.load(in_weight)
        for feature in weights: 
            sys.stdout.write("%s = %f\n" % (feature, weights[feature]))
