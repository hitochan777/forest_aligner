import sys

class DependencyTreeNode:
    def __init__(self):
        self.children = []
        self.data = None
        self.parent = None
        self.isDummy = False
        self.lmScore = None
    
    def addChild(self, child):
        """
        child: instance of DecodingPath
        """
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
