from collections import defaultdict
import svector

class PartialGridAlignment(object):
    def __hash__(self):
      return id(self)
  
    def __cmp__(self, x):
      """
      Compare two PartialGridAlignment objects.
      """
      if self.score < x.score:
          return -1
      elif self.score == x.score:
          return 0
      else:
          return 1
  
    def __str__(self):
      return str(self.score)+" "+str(self.links)
  
    def __init__(self, flen = 0, elen = 0):
      """
      Initialize member objects
      """
      self.links = [ ]
      self.score = 0
      self.fscore = 0
      self.hyperEdgeScore = 0.0
      self.scoreVector = svector.Vector()
      self.scoreVector_nonlocal = svector.Vector()
      self.position = None
      self.boundingBox = None
  
    def clear(self):
      self.links = []
      self.score = 0
      self.fscore = 0
      self.hyperEdgeScore = 0.0
      self.scoreVector = svector.Vector()
      self.position = None
      self.boundingBox = None

    def addDepthToLink(self, delta=1):
        for link in self.links:
            link.depth += delta
