import sys

import depLM

class DependencyTreeNode(depLM.DependencyTreeNode):
    def __init__(self):
        self.children = []
        self.data = None
        self.parent = None
        self.isDummy = False
    
    def addChild(self, child):
        """
        child: instance of DecodingPath
        """
        self.children.append(child)

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
