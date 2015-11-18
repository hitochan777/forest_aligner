from collections import defaultdict
from AlignmentLink import AlignmentLink
from DecodingPath import DecodingPath
import svector
import sys

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
        return str(self.score)+" "+str(map(lambda x: x.link,self.links))
  
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
      self.boundingBoxOrigins = None
      self.decodingPath = DecodingPath()
  
    def clear(self):
      self.links = []
      self.score = 0
      self.fscore = 0
      self.hyperEdgeScore = 0.0
      self.scoreVector = svector.Vector()
      self.position = None
      self.boundingBox = None

    def getDepthAddedLink(self, delta=1):
        newAlignmentLinks = []
        for link in self.links:
            newAlignment = AlignmentLink(link.link, link.depth + delta)
            newAlignmentLinks.append(newAlignment)
        return newAlignmentLinks

