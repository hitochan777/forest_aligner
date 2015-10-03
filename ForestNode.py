#!/usr/bin/env python
# hitochan777@gmail.com (Otsuki Hitoshi)

import sys
import weakref
from HyperEdge import HyperEdge

class ForestNode:
    def __init__(self, data = None):
        self.setup(data)

    def setup(self, data):
        self.partialAlignments = []
        self.partialAlignments_hope = []
        self.partialAlignments_fear = []
        self.data = data
        self.parent = []
        self.hyperEdges = []
        self.terminals = []
        self.eIndex = -1
        self.hope = None
        self.oracle = None
        self.fear = None
        self.i = -1
        self.j = -1
        self.order = 0
        self.span = None
        # self.nodeList = None # list including weakref to each node; sorted by id

    def setTerminals(self):
        if len(self.hyperEdges) > 0:
            for hyperEdge in self.hyperEdges:
                for child in hyperEdge.tail:
                    self.terminals += child.setTerminals()
        else:
            self.terminals = [weakref.ref(self)]
        return self.terminals

    def getAllNodes(self):
        return self.nodeList

    def getNodeByIndex(self, index):
        """
        Return node with index i
        Store only weak references to node
        """
        return self.nodeList[index]

    def getTreeTerminals(self):
        """
        Iterator over terminals.
        """
        # print len(self.terminals)
        if len(self.terminals)==0:
            self.setTerminals()
        for t in self.terminals:
            yield t()

    def isTerminal(self):
        return len(self.hyperEdges) == 0

    def span_start(self):
        return self.i

    def span_end(self):
        return self.j - 1

    def get_span(self):
        if self.span is None:
            start = self.span_start()
        end = self.span_end()
        self.span = (start,end)
        return self.span

    def addParent(self, parent, score):
      self.parent.append({"parent": parent, "score": score})

    def addHyperEdge(self, head, tail, score):
        self.hyperEdges.append(HyperEdge(head, tail,score))

    def depth(self,d = 0): #TODO: implement depth
        return 1

    def containsSpan(self, fspan):
        """
        Does span of node currentNode wholly contain span fspan?
        """
        span = self.get_span()
        return span[0] <= fspan[0] and span[1] >= fspan[1]
