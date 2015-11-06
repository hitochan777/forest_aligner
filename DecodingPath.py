import sys

class DecodingPath:
    def __init__(self):
        self.children = []
        self.parent = None 
        self.node = None
    
    def addChild(self, child):
        self.children.append(child)

    def getDecodingPath(self, depth=0):
        path = "%s%s(%d:%s)" % (" "*2*depth, self.node.data['surface'], self.node.data['id'], self.node.data['pos'])
        for child in self.children:
            path = path+"\n"+child.getDecodingPath(depth+1)
        return path
