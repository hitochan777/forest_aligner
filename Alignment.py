#!/usr/bin/env python

from collections import defaultdict
import sys
import re

def readAlignmentString(str, inverse = False):
    """
    Read a string of f-e links an return a dictionary
    of link tuples (f,e)
    """
    d = { }
    for link in str.split():
        try:
            matchObj = re.match(r"(\d+)-(\d+)(?:\[(.+)\])?", link)
            f, e, linkTag = matchObj.groups() 
            if inverse:
                f, e = e, f

            if linkTag is None:
                linkTag = False

            d[(int(f), int(e))] = linkTag 

        except:
            sys.stderr.write("Couldn't process link '%s'\n" %(link))
            sys.stderr.write("Alignment: %s\n" %(str))
            sys.exit(1)
    return d

class Alignment(object):
    def __init__(self, str, inverse = False):
        self.score = 0
        self.scoreVector = []
        self.links_dict = { }
        # Index links by column, or e index
        self.eLinks = defaultdict(list)
        # Index links also by row, or f index
        self.numLinksInSpan = { }
        self.linksInSpan = { }
        self.read(str, inverse)

    def read(self, links_str, inverse = False, delim = '-'):
        """
        Reads and records a string encoded sequence of links, f-e f-e f-e ...
        """
        for linkstr in links_str.strip().split():
            matchObj = re.match(r"(\d+)-(\d+)(?:\[(.+)\])?", linkstr)
            f, e, linkTag = matchObj.groups() 
            f, e = int(f), int(e)
            if inverse:
                f, e = e, f

            if linkTag is None:
                linkTag = False

            link = (f,e)
            self.eLinks[e].append(link)
            self.links_dict[link] = linkTag 

    def getLinksByEIndex(self, span):
        """
        Return a list of links (f,e) s.t. span[0] <= e <= span[1]
        """
        links = self.linksInSpan.get(span, None)
        if links is None:
            links = []
            for e in range(span[0], span[1]+1):
                links += self.eLinks[e]
            self.linksInSpan[span] = links
        return links
