#!/usr/bin/env python
# hitochan777@gmail.com (Otsuki Hitoshi)

import sys
import weakref
from collections import defaultdict
from HyperEdge import HyperEdge

class ForestNode:
    def __init__(self, data = None):
        self.setup(data)

    def setup(self, data):
        self.partialAlignments = {"hyp": [], "oracle": []}
        self.data = data
        self.parent = []
        self.hyperEdges = []
        self.oracle = None
        self.childnum = -1
        self.unprocessedChildNum = -1 # the number of children whose k-best hasn't been calculated yet
        self.terminals = None
        # self.eIndex = -1
        self.i = -1
        self.j = -1
        self.order = 0
        self.span = None
        self.root = None # pointer to root node
        # self.nodeList = None # list including weakref to each node; sorted by id
  
    def setTerminals(self):
        visited = defaultdict(bool)
        if len(self.hyperEdges) > 0:
            self.terminals = set()
            for hyperEdge in self.hyperEdges:
                for child in hyperEdge.tail:
                    if not visited[child.data["id"]]:
                        self.terminals = self.terminals.union(child.setTerminals())
                        visited[child.data["id"]] = True
        else:
            self.terminals = set([weakref.ref(self)])
        return self.terminals
  
    def getTerminals(self):
        """
        Iterator over terminals.
        """
        if self.terminals == None:
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
  
    def containsSpan(self, fspan):
        """
        Does span of node currentNode wholly contain span fspan?
        """
        span = self.get_span()
        return span[0] <= fspan[0] and span[1] >= fspan[1]

    def getDeepestNodeConveringSpan(self, fspan):
        minSpan = (0,self.j)
        coveringNode = None
        queue = []
        for terminal in self.getTerminals():
            queue.append(terminal)
        while len(queue) > 0:
            currentNode = queue.pop(0)
            span = currentNode.get_span()
            for edgeToParent in currentNode.parent:
                queue.append(edgeToParent["parent"]) 
            if span[1] - span[0] < minSpan[1] - minSpan[0] and currentNode.containsSpan(fspan):
                minSpan = span
                coveringNode = currentNode
        return coveringNode
    
    def getNodesByIndex(self, index):
        assert self.data["pos"] == "TOP", "%s can only be used at root node. " % self.getNodesByIndex.func_name
        return self.data["nodeTable"][index] 

    def getParentNodes(self):
        return map(lambda d: d["parent"], self.parent)

    def isConnectedTo(self, node):
        assert self != node, "You cannot compare the same two nodes..."
        if self in node.getParentNodes() or node in self.getParentNodes():
            return 1
        return 0
