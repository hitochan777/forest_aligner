# -*- coding: utf-8 -*-

import sys

class DependencyTreeNode:
    def __init__(self):
        self.children = []
        self.data = None
        self.parent = None
        self.isDummy = False
        self.lmScore = None
        self.nodeRefList = None
    
    def addChild(self, child):
        """
        child: instance of DecodingPath
        """
        self.children.append(child)

    def partitionChildren(self):
        left = [] # items smaller than pivot
        right = [] # items bigger than pivot
        pivot = self.data["word_id"]
        for child in self.children:
            child.parent = self
            if child.data["word_id"] < pivot:
                left.append(child)
            elif child.data["word_id"] > pivot:
                right.append(child)
            else:
                raise ValueError("item and pivot cannot have the same value because they are node ID")

        left = sorted(left, key=lambda x: x.data["word_id"], reverse=True)
        # By default reverse is False, but this is just for emphasizing right is not reversed as opposed to left
        right = sorted(right, key=lambda x: x.data["word_id"], reverse=False) 
        return left, right

    def calcScore(self, depLM, clearCache = False):
        assert depLM is not None
        if clearCache:
            self.lmScore = None
        if self.lmScore is not None:
            return
        self.lmScore = 0.0
        for child in self.children:
            if child.lmScore is not None: # if child is terminal node, lmScore is not set hence we skip the node
                self.lmScore += child.lmScore

        left, right = self.partitionChildren()
        if len(left) > 0:
            self.lmScore += depLM.probLeft.stupidBackoffProb(["___none", depLM.countkey(left[0].parent)+"___head", depLM.countkey(left[0])])
        for index in xrange(1, len(left)):
            self.lmScore += depLM.probLeft.stupidBackoffProb([depLM.countkey(left[index-1]), depLM.countkey(left[index].parent)+"___head", depLM.countkey(left[index])])

        if len(right) > 0:
            self.lmScore += depLM.probRight.stupidBackoffProb(["___none", depLM.countkey(right[0].parent)+"___head", depLM.countkey(right[0])])
        for index in xrange(1, len(right)):
            self.lmScore += depLM.probRight.stupidBackoffProb([depLM.countkey(right[index-1]), depLM.countkey(right[index].parent)+"___head", depLM.countkey(right[index])])

    def getDecodingPath(self, depth=0):
        path = ""
        if not self.isDummy:
            path = "%s%s(%d:%s)" % (" "*2*depth, self.data['surface'], self.data['id'], self.data['pos'])
        for child in self.children:
            if len(path)==0:
                path = child.getDecodingPath(depth+(not self.isDummy))
            else: 
                path = path+"\n"+child.getDecodingPath(depth+(not self.isDummy))
        return path
    
    def _getOrderedNodeList(self):
        left, right = self.partitionChildren()
        left.reverse() # since left is reversed in partitionChildren
        leftNodes = []
        rightNodes = []
        for node in left:
            leftNodes += node._getOrderedNodeList()
        for node in right:
            rightNodes += node._getOrderedNodeList()

        sortedList = leftNodes + [self] + rightNodes
        assert all(sortedList[i].data["word_id"] < sortedList[i+1].data["word_id"] for i in xrange(len(sortedList)-1))
        return leftNodes + [self] + rightNodes

    def setNodeRef(self):
        nodes = self._getOrderedNodeList()
        for node in nodes:
            node.data.update({"pre_children_ref": [], "post_children_ref": []})
        
        for node in nodes:
            id = node.data["word_id"]
            if node.parent is None: # if parent does not exist
                continue

            dependency_id = node.parent.data["word_id"]

            if id < dependency_id:
                nodes[dependency_id].data["pre_children_ref"].append(nodes[id])
            else:
                nodes[dependency_id].data["post_children_ref"].append(nodes[id])
       
    def getStringifiedTree(self, horizontal = False):
        buffer = []
        self.setNodeRef()
        self._getVisualizedDependencyTree(self.data, "", buffer, horizontal)
        return "\n".join(buffer)

    def _getVisualizedDependencyTree(self, word_ref, mark, b_ref, horizontal = False):
        local_buffer = u""
        children = []
        # print pre-children
        for c in word_ref["pre_children_ref"]:
            children.append(c)

        if len(children) > 0:
            self._getVisualizedDependencyTree(children.pop(0).data, mark+"L", b_ref, horizontal)
            for c in children:
                self._getVisualizedDependencyTree(c.data, mark+"l", b_ref, horizontal)

        # print self
        markList = []
        if mark != "":
            markList = list(mark) # string to list of characters

        for m in xrange(len(markList)):
            if m == len(markList) - 1:
                if markList[m] == "L":
                    local_buffer += u'┌'
                elif markList[m] == "R":
                    if horizontal:
                        local_buffer += u'┐'
                    else:
                        local_buffer += u'└'
                else:
                    if horizontal:
                        local_buffer += u'┬'
                    else:
                        local_buffer += u'├'

            else:
                if markList[m] == "l" or markList[m] == "r" or \
                    (markList[m] == "L" and (markList[m+1] == "r" or markList[m+1] == "R")) or \
                    (markList[m] == "R" and (markList[m+1] == "l" or markList[m+1] == "L")):
                        if horizontal:
                            local_buffer += u'─'
                        else:
                            local_buffer += u'│'
                else:
                    local_buffer += u'　'

        local_buffer += unicode(word_ref["surface"], "utf-8")
        b_ref.append(local_buffer)

        # print post-children
        children = []
        for c in word_ref["post_children_ref"]:
            children.append(c)

        if len(children) > 0:
            last_child = children.pop()
            for c in children:
                self._getVisualizedDependencyTree(c.data, mark+"r", b_ref, horizontal)

            self._getVisualizedDependencyTree(last_child.data, mark+"R", b_ref, horizontal)

