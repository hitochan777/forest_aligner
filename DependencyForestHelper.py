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
                dep=line
                continue
            # if line.startswith("\n"):
            #     continue
            dep += line
        if dep!="":
            yield dep

def parser(string):
    buf = StringIO.StringIO(string)
    nodeList = []
    nodeChildrenSetList = []
    nodeTable = []
    curWordId = -1
    sent_len = 0
    for line in buf:
        if line.startswith("#"):
            p = re.compile('#\s*ID=(\d+)') 
            sentence_ID= int(p.match(line).group(1))
            continue
        if not line.strip():
            break
        node = ForestNode()
        word_infos = line.split()
        node.i, node.j = map(int, word_infos[1].split(",")) # add span
        dict_form = word_infos[4].split("/")[0]
        if "/" in word_infos[4]:
            pronunciation = word_infos[4].split("/")[1]
        else:
            pronunciation = None
        if ":" in word_infos[5]:
            pos2 = word_infos[5].split(":")[1]
        else:
            pos2 = None
        pos = word_infos[5].split(":")[0]
        word_id = int(word_infos[2])
        if curWordId != word_id:
            nodeTable.append([])
            curWordId = word_id
        node.data = {
                "id": int(word_infos[0]), # node ID which is unique
                "word_id": word_id, 
                "surface": word_infos[3],
                "pronunciation": pronunciation,
                "dict_form": dict_form,
                "pos": pos,
                "pos2": pos2,
                "isContent": word_infos[6]=="1",
                "pos2": pos2
        }
        nodeList.append(node)
        nodeTable[-1].append(node)
        nodeChildrenSetList.append(set())
        sent_len = max(sent_len, node.data["word_id"])

    sent_len += 1

    assert len(nodeTable)==sent_len, "The length of node table(%d) is not the same as the sentence length(%d). Make sure that forest input data is consistent with segmented sentence data." % (len(nodeTable), sent_len)

    for line in buf: # process hyperedge
        if not line.strip():
            break
        edge_infos = line.split()
        head = int(edge_infos[0])
        tail = map(int, edge_infos[1].split(","))
        score = float(edge_infos[2])
        nodeList[head].addHyperEdge(nodeList[head], map(lambda id: nodeList[id], tail), score)
        for element in tail:
            nodeChildrenSetList[head].add(element)

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
        "id": -1,
        "word_id": -1,
        "surface": "__TOP__",
        "dict_form": "__TOP__",
        "pos": "TOP",
        "isContent": False,
        "pos2": "TOP",
        "sentence_ID": sentence_ID,
        "nodeTable": nodeTable,
        "root": root
    }

    for node in nodeList:
        node.root = root
        node.unprocessedChildNum = node.childnum = len(nodeChildrenSetList[node.data["id"]])
        if node.i == 0 and node.j == sent_len:
            node.addParent(root, 0) 
            root.addHyperEdge(root,[node], 0.0) # Since root is dummy, it is natural to think scores of incoming hyperedge is zero
    root.unprocessedChildNum = root.childnum = len(root.hyperEdges) # Since the arity of every incoming hyperedge to root is 0, the number of childrent is equal to the number of the hyperedges. 
    return root
