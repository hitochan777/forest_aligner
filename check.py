from DependencyForestHelper import *

g = list(readDependencyForestFile("data/aspec-je.ja.forest"))
f = parser(g[0])
for e in f.hyperEdges:
  print e.head, e.tail, e.score
