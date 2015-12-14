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
