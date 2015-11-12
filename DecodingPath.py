import sys

class DecodingPath:
    def __init__(self):
        self.children = []
        self.node = None
        self.isDummy = False
    
    def addChild(self, child):
        self.children.append(child)

    def getDecodingPath(self, depth=0):
        path = ""
        if not self.isDummy:
            path = "%s%s(%d:%s)" % (" "*2*depth, self.node.data['surface'], self.node.data['id'], self.node.data['pos'])
        for child in self.children:
            if len(path)==0:
                path = child.getDecodingPath(depth+(not self.isDummy))
            else: 
                path = path+"\n"+child.getDecodingPath(depth+(not self.isDummy))
        return path
