#!/usr/bin/env python
# otsuki@nlp (Otsuki Hitoshi)

class DependencyTreeNode:
    def __init__(self, data = None, depLM = None):
        self.data = data
        self.parent = None
        self.children = []
        self.score = None
        # self.depLM = depLM

    def addChild(self, child):
        self.children.append(child)

    def partitionChildren(self):
        left = [] # items smaller than pivot
        right = [] # items bigger than pivot
        pivot = self.data["id"]
        for child in self.children:
            if child.data["id"] < pivot:
                left.append(child)
            elif child.data["id"] > pivot:
                right.append(child)
            else:
                raise ValueError("item and pivot cannot have the same value because they are node ID")
        sorted(left, key=lambda x: x.data["id"], reverse=True)
        # By default reverse is False, but this is just for emphasizing right is not reversed as opposed to left
        sorted(right, key=lambda x: x.data["id"], reverse=False) 
        return left, right

    # def calcScore(self, clearCache = False):
    #     if clearCache:
    #         self.score = None
    #     if self.score is not None:
    #         return
    #     self.score = 0.0
    #     for child in children:
    #         self.score += child.score
    #     left, right = self.partitionChildren()
    #     if len(left) > 0:
    #         self.score += depLM.probLeft.stupidBackoffProb(["___none", depLM.countkey(left[0].parent)+"___head", depLM.countkey(left[0])])
    #     for index in xrange(1, len(left)):
    #         self.score += depLM.probLeft.stupidBackoffProb([depLM.countkey(left[index-1]), depLM.countkey(left[index].parent)+"___head", depLM.countkey(left[index])])
    #
    #     if len(right) > 0:
    #         self.score += depLM.probRight.stupidBackoffProb(["___none", depLM.countkey(right[0].parent)+"___head", depLM.countkey(right[0])])
    #     for index in xrange(1, len(right)):
    #         self.score += depLM.probRight.stupidBackoffProb([depLM.countkey(right[index-1]), depLM.countkey(right[index].parent)+"___head", depLM.countkey(right[index])])
    #
