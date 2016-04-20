#!/usr/bin/env python
# Jason Riesa <riesa@isi.edu>
# 9/12/2008
''' Calculate fmeasure and related figures, given two Alignment objects '''

import sys
import re
from collections import defaultdict
from itertools import izip_longest, izip
import argparse 

class Fmeasure:
    def sure(links):
        dic = {}
        for link in links:
            obj = re.match(r"(?P<link>\d+-\d+)(?:\[(?P<linktag>.+)\])?", link)
            linkStr = obj.group("link")
            dic[linkStr] = obj.group("linktag")

        return dic


    evaluateMethod = {
        "link": lambda links: list(map(lambda link: re.match(r"(\d+-\d+)(?:\[(.+)\])?", link).group(1), links)), 
        "all": lambda links: links,
        "sure": sure
    }

    def __init__(self, evaluateMethod = "link"):
        self.correct = 0
        self.numMeTotal = 0
        self.numGoldTotal = 0
        self.evaluateMethod = evaluateMethod


    def accumulate(self, me, gold):
        #Accumulate counts

        meLinks = Fmeasure.evaluateMethod[self.evaluateMethod](me.strip().split())
        goldLinks = Fmeasure.evaluateMethod[self.evaluateMethod](gold.strip().split())

        self.numMeTotal += len(meLinks)
        self.numGoldTotal += len(goldLinks)
        goldLinksDict = goldLinks
        if type(goldLinks) == list:
            goldLinksDict = dict(izip_longest(goldLinks, [None]))
        else: # type is dict
            if self.evaluateMethod == "sure":
                self.numGoldTotal -= goldLinks.values().count("possible")

        for link in meLinks:
            if link in goldLinksDict:
                if self.evaluateMethod == "sure":
                    if goldLinksDict[link] == "possible":
                        self.numMeTotal -= 1
                        self.correct -= 1.0

                self.correct += 1.0

    def accumulate_o(self, edge, goldmatrix):

        self.numMeTotal += len(edge.links)
        goldIndices = nonzero(goldmatrix)
        self.numGoldTotal += len(goldIndices[0])

        for link in edge.links:
            if goldmatrix[link[0]][link[1]] == 1:
                self.correct += 1.0

    '''
    def accumulate_m(self, model, gold):
        # model and gold are matrices, each representing
        # links in an alignment; a cell holding '1' denotes a link

        self.numMeTotal += sum(model)
        self.numGoldTotal += sum(gold)
        # sum matrices together; cells that hold a '2' are correct links
        self.correct += len(nonzero((model+gold)==2)[0])
    '''

    def report(self):
        ''' Report f-score and related figures '''

        precision = self.precision()
        recall = self.recall()
        if (precision + recall) == 0:
            fscore = 0.0
        else:
            fscore = (2.0*precision*recall)/(precision + recall)

        #fscore = self.f1score()

        sys.stdout.write('F-score: %1.5f\n' % (fscore))
        sys.stdout.write('Precision: %1.5f\n' % (precision))
        sys.stdout.write('Recall: %1.5f\n' % (recall))
        sys.stdout.write('# Correct: %d\n' % (self.correct))
        sys.stdout.write('# Hyp Total: %d\n' % (self.numMeTotal))
        sys.stdout.write('# Gold Total: %d\n' % (self.numGoldTotal))
        return fscore

    def precision(self):
        if self.numMeTotal == 0 and self.numGoldTotal == 0:
            return 1.0
        elif self.numMeTotal == 0 or self.numGoldTotal == 0:
            return 0.0
        else:
            return float(self.correct)/self.numMeTotal

    def recall(self):
        if self.numMeTotal == 0 and self.numGoldTotal == 0:
            return 1.0
        elif self.numMeTotal == 0 or self.numGoldTotal == 0:
            return 0.0
        else:
            return float(self.correct)/self.numGoldTotal

    def f1score(self):
        prec = self.precision()
        rec = self.recall()
        if prec + rec == 0:
            return 0.0
        else:
            return 2.0*prec*rec/(prec + rec)

    def reset(self):
        self.correct = 0.0
        self.numGoldTotal = 0.0
        self.numMeTotal = 0.0


def score(file1, file2, evaluateMethod):

    fmeasure = Fmeasure(evaluateMethod)
    for (me_str, gold_str) in izip(open(file1, 'r'), open(file2, 'r')):
        fmeasure.accumulate(me_str, gold_str)

    fmeasure.report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
""")
    parser.add_argument('alignment', type=str, help='Alignment')
    parser.add_argument('gold_alignment', type=str, help='Gold alignment')
    parser.add_argument('--evaluate', type=str, choices=["link", "all", "sure"], default="link", help='Gold alignment')

    args = parser.parse_args()
    score(args.alignment, args.gold_alignment, args.evaluate)
