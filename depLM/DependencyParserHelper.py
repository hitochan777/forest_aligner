import re
import sys

from DependencyTreeNode import DependencyTreeNode

def readDependencyFile(filename):
    dep=""
    with open(filename,"r") as f:
        for line in f:
            if line.startswith("\n"):
                if dep!="":
                    yield dep
                    dep=""
                continue
            dep += line
        if dep!="":
            yield dep

def stringToDependencyTreeWeakRef(string):
    """
    Read dependency parser output style tree string and return the tree that the string encodes. 
    """
    # Reset current class members
    eIndex = -1
    rootId = -1  
    infos = [word_infos.split() for word_infos in string.strip().split("\n")]
    # print(infos)
    strlen = len(infos)
    nodeList = [DependencyTreeNode() for i in range(0,strlen)]
    for info in infos: 
        id = int(info[0]) - 1
        surface = info[1] 
        dict_form = info[2]
        pos = info[3]
        pos2 = info[4]
        dependency_id = int(info[6]) - 1
        depLabel = info[7]
        nodeList[id].data = {"id": id, "dep_id": dependency_id, "surface": surface, "dict_form": dict_form, "pos": pos, "pos2": pos2, "depLabel": depLabel}
        if dependency_id >= 0:
            nodeList[id].parent = nodeList[dependency_id]
            nodeList[dependency_id].addChild(nodeList[id])
        else:
            if rootId != -1:
                sys.stderr.write('Root appeared more than once!! Skipping... ')
                return None
            rootId = id
            nodeList[id].parent = None
    if rootId == -1:
        sys.stderr.write("Root did't appear!! Skippping...") 
        return None
    return nodeList[rootId]
    
if __name__ == "__main__":
    fname=sys.argv[1]
    y = readDependencyFile(fname)
    for d in y:
        tree = stringToDependencyTreeWeakRef(d)
        # print(tree)
        for node in tree.bottomup():
            print(node.data["surface"],node.i, node.j)
            # print(node.setTerminals())
        # print(d.split("\n"))
