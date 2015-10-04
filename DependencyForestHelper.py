import re
import sys
import StringIO
import weakref
# http://stackoverflow.com/questions/9908013/weak-references-in-python

from ForestNode import ForestNode

def readDependencyForestFile(filename):
    dep=""
    with open(filename,"r") as f:
        for line in f:
            if line.startswith("#"):
                if dep!="":
                    yield dep
                    dep=""
                continue
            # if line.startswith("\n"):
            #     continue
            dep += line
        if dep!="":
            yield dep

def parser(string):
    # keys = ["id","span","word_id", "surface", "base", "pos", "is_content", "pos2","type", "other"]
    buf = StringIO.StringIO(string)
    nodeList = []
    sent_len = 0
    for line in buf:
        if not line.strip():
            break
        node = ForestNode()
        word_infos = line.split()
        node.i, node.j = map(lambda x: int(x), word_infos[1].split(",")) # add span
        node.data = {
                "id": int(word_infos[0]), # node ID which is unique
                "word_id": int(word_infos[2]), 
                "surface": word_infos[3],
                "dict_form": word_infos[4],
                "pos": word_infos[5],
                "isContent": word_infos[6]=="1",
                "pos2": word_infos[7]
        }
        nodeList.append(node)
        sent_len = max(sent_len, node.data["word_id"])

    for line in buf: # process hyperedge
        if not line.strip():
            break
        edge_infos = line.split()
        head = int(edge_infos[0])
        tail = map(int, edge_infos[1].split(","))
        score = float(edge_infos[2])
        nodeList[head].addHyperEdge(nodeList[head], map(lambda id: nodeList[id], tail), score)
        nodeList[head].childnum += len(tail)

    for line in buf: # process child and parent relations
        if not line.strip():
            break
        edge_infos = line.split()
        parent_id = int(edge_infos[0])
        child_id = int(edge_infos[1])
        score = float(edge_infos[2])
        nodeList[child_id].addParent(nodeList[parent_id], score)

    root = ForestNode() # Dummy root node which collects all root nodes(A forest has multiple roots) in the forest.
    root.i, root.j = 0, sent_len
    root.data = {
        "id": None,
        "word_id": None,
        "surface": None,
        "dict_form": None,
        "pos": "TOP",
        "isContent": False,
        "pos2": "TOP"
    }

    for node in nodeList:
        node.unprocessedChildNum = node.childnum
        if node.i == 0 and node.j + 1 == sent_len:
            node.addParent(root, 0) 
            root.addHyperEdge(root,[node], 0.0) # Since root is dummy, it is natural to think scores of incoming hyperedge is zero
            # print len(root.hyperEdges)
    return root

if __name__ == "__main__":
    fname=sys.argv[1]
    y = readDependencyFile(fname)
    for d in y:
        tree = parse(d)
        # print(tree)
        for node in tree.bottomup():
            print(node.data["surface"],node.i, node.j)
            # print(node.setTerminals())
        # print(d.split("\n"))
