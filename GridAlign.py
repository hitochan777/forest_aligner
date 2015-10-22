#!/usr/bin/env python

#########################################################
# GridAlign.py
# riesa@isi.edu (Jason Riesa)
# Based on work described in:
# @inproceedings{RiesaIrvineMarcu:11,
#   Title = {Feature-Rich Language-Independent Syntax-Based Alignment for Statistical Machine Translation},
#   Author = {Jason Riesa and Ann Irvine and Daniel Marcu},
#   Booktitle = {Proceedings of the 2011 Conference on Empirical Methods in Natural Language Processing},
#   Pages = {497--507},
#   Publisher = {Association for Computational Linguistics},
#   Year = {2011}}
#
# @inproceedings{RiesaMarcu:10,
#   Title = {Hierarchical Search for Word Alignment},
#   Author = {Jason Riesa and Daniel Marcu},
#   Booktitle = {Proceedings of the 48th Annual Meeting of the Association for Computational Linguistics (ACL)},
#   Pages = {157--166},
#   Publisher = {Association for Computational Linguistics},
#   Year = {2010}}
#########################################################

import cPickle
import sys
from itertools import izip
from operator import attrgetter
from heapq import heappush, heapify, heappop, heappushpop
from collections import defaultdict
import collections

from DependencyForestHelper import *
from Alignment import readAlignmentString
from PartialGridAlignment import PartialGridAlignment
import Fmeasure
import svector
import ScoreFunctions
from AlignmentLink import AlignmentLink

class Model(object):
    """
    Main class for the Hierarchical Alignment model
    """
    def __init__(self, f = None, e = None, etree = None, ftree = None,
                 id = "no-id-given", weights = None, a1 = None, a2 = None,
                 inverse = None, DECODING=False,
                 LOCAL_FEATURES = None, NONLOCAL_FEATURES = None, FLAGS=None):
  
      ################################################
      # Constants and Flags
      ################################################
      if FLAGS is None:
        sys.stderr.write("Program flags not given to alignment model.\n")
        sys.exit(1)
  
      self.FLAGS = FLAGS
  
      self.LOCAL_FEATURES = LOCAL_FEATURES
      self.NONLOCAL_FEATURES = NONLOCAL_FEATURES
      self.LANG = FLAGS.langpair
      if FLAGS.init_k is not None:
        self.BEAM_SIZE = FLAGS.init_k
      else:
        self.BEAM_SIZE = FLAGS.k
      self.NT_BEAM = FLAGS.k
      self.COMPUTE_HOPE = False
      self.COMPUTE_1BEST = False
      self.COMPUTE_FEAR = False
      self.COMPUTE_ORACLE = False
      self.hypScoreFunc = ScoreFunctions.default
      self.oracleScoreFunc = ScoreFunctions.default
      self.DO_RESCORE = FLAGS.rescore
      self.DECODING = False
      if DECODING:
        self.COMPUTE_1BEST = True
        self.DECODING = True
      else:
        if FLAGS.oracle == "gold":
          self.COMPUTE_ORACLE = True
        elif FLAGS.oracle == "hope":
          self.COMPUTE_HOPE = True
          self.oracleScoreFunc = ScoreFunctions.hope 
  
        elif FLAGS.oracle is not None:
          # During decoding we don't need to compute oracle
          sys.stderr.write("Unknown value: oracle=%s\n" %(FLAGS.oracle))
          sys.exit(1)
  
        if FLAGS.hyp == "1best":
          self.COMPUTE_1BEST = True
        elif FLAGS.hyp == "fear":
          self.COMPUTE_FEAR = True
          self.oracleScoreFunc = ScoreFunctions.fear
        else:
          sys.stderr.write("Unknown value: hyp=%s\n" %(FLAGS.hyp))
          sys.exit(1)
  
      # Extra info to pass to feature functions
      self.info = { }
  
      self.f = f
      self.fstring = " ".join(f)
      self.e = e
      self.lenE = len(e)
      self.lenF = len(f)
      self.nto1 = FLAGS.nto1
  
      # GIZA++ alignments
      self.a1 = { }		# intersection
      self.a2 = { }		# grow-diag-final
      self.inverse = { }      # ivi-inverse
      if FLAGS.inverse is not None:
        self.inverse = readAlignmentString(inverse)
      if FLAGS.a1 is not None:
        self.a1 = readAlignmentString(a1)
      if FLAGS.a2 is not None:
        self.a2 = readAlignmentString(a2)
  
      self.hyp = None
      self.oracle = None
      self.gold = None
  
      self.id = id
      self.pef = { }
      self.pfe = { }
  
      self.etree = parser(etree) 
      # self.etree.terminals = self.etree.setTerminals()
      if ftree is not None:
          self.ftree = parser(ftree) 
          self.ftree.terminals = self.ftree.setTerminals()
      else:
        self.ftree = None
  
      # Keep track of all of our feature templates
      self.featureTemplates = [ ]
      self.featureTemplates_nonlocal= [ ]
  
      ########################################
      # Add weight vector to model
      ########################################
      # Initialize local weights
      if weights is None or len(weights) == 0:
        self.weights = svector.Vector()
      else:
        self.weights = weights
  
      ########################################
      # Add Feature templates to model
      ########################################
      self.featureTemplateSetup_local(LOCAL_FEATURES)
      self.featureTemplateSetup_nonlocal(NONLOCAL_FEATURES)
  
      # Data structures for feature function memoization
      self.diagValues = { }
      self.treeDistValues = { }
  
      # Populate info
      self.info['a1']=self.a1
      self.info['a2']=self.a2
      self.info['inverse']=self.inverse
      self.info['f'] = self.f
      self.info['e'] = self.e
      self.info['etree'] = self.etree
      self.info['ftree'] = self.ftree
  
    ########################################
    # Initialize feature function list
    ########################################
    def featureTemplateSetup_local(self, localFeatures):
      """
      Incorporate the following "local" features into our model.
      """
      self.featureTemplates.append(localFeatures.ff_identity)
      self.featureTemplates.append(localFeatures.ff_jumpDistance)
      self.featureTemplates.append(localFeatures.ff_finalPeriodAlignedToNonPeriod)
      self.featureTemplates.append(localFeatures.ff_lexprob_zero)
      self.featureTemplates.append(localFeatures.ff_probEgivenF)
      self.featureTemplates.append(localFeatures.ff_probFgivenE)
      self.featureTemplates.append(localFeatures.ff_distToDiag)
      self.featureTemplates.append(localFeatures.ff_isLinkedToNullWord)
      self.featureTemplates.append(localFeatures.ff_isPuncAndHasMoreThanOneLink)
      self.featureTemplates.append(localFeatures.ff_quote1to1)
      self.featureTemplates.append(localFeatures.ff_unalignedNonfinalPeriod)
      self.featureTemplates.append(localFeatures.ff_nonfinalPeriodLinkedToComma)
      self.featureTemplates.append(localFeatures.ff_nonPeriodLinkedToPeriod)
      self.featureTemplates.append(localFeatures.ff_nonfinalPeriodLinkedToFinalPeriod)
      # self.featureTemplates.append(localFeatures.ff_tgtTag_srcTag)
      self.featureTemplates.append(localFeatures.ff_thirdParty)
  
    ##################################################
    # Inititalize feature function list
    ##################################################
    def featureTemplateSetup_nonlocal(self, nonlocalFeatures):
      """
      Incorporate the following combination-cost features into our model.
      """
      # self.featureTemplates_nonlocal.append(nonlocalFeatures.ff_nonlocal_dummy)
      self.featureTemplates_nonlocal.append(nonlocalFeatures.ff_nonlocal_isPuncAndHasMoreThanOneLink)
      self.featureTemplates_nonlocal.append(nonlocalFeatures.ff_nonlocal_sameWordLinks)
      self.featureTemplates_nonlocal.append(nonlocalFeatures.ff_nonlocal_hyperEdgeScore)
      # self.featureTemplates_nonlocal.append(nonlocalFeatures.ff_nonlocal_treeDistance)
      # self.featureTemplates_nonlocal.append(nonlocalFeatures.ff_nonlocal_tgtTag_srcTag)
      # self.featureTemplates_nonlocal.append(nonlocalFeatures.ff_nonlocal_crossb)
  
    def align(self):
        """
        Main wrapper for performing alignment.
        """
        ##############################################
        # Do the alignment, traversing tree bottom up.
        ##############################################
        self.bottom_up_visit()
        # *DONE* Now finalize everything; final bookkeeping.
  
        self.hyp = self.etree.partialAlignments["hyp"][0]
        if self.COMPUTE_HOPE:
            self.oracle = self.etree.partialAlignments["oracle"][0]
        elif self.COMPUTE_ORACLE:
            self.oracle = self.etree.partialAlignments["oracle"]
      
    def bottom_up_visit(self):
        """
        Visit each node in the tree, bottom up, and in level-order.
  
        ###########################################################
        # bottom_up_visit(self):
        # traverse etree bottom-up, in level order
        # (1) Add terminal nodes to the visit queue
        # (2) As each node is visited, add its parent to the visit
        #     queue if not already on the queue
        # (3) During each visit, perform the proper alignment function
        #     depending on the type of node: 'terminal' or 'non-terminal'
        ###########################################################
        """
        queue = [ ]
        if self.etree is None:
            empty = PartialGridAlignment()
            empty.score = None
            self.etree.partialAlignments["hyp"].append(empty)
            self.etree.partialAlignments["oracle"] = PartialGridAlignment()
            return

        # Add first-level nodes to the queue
        # for terminal in sorted(list(self.etree.getTerminals()),key=lambda x: x.data["word_id"]):
        for terminal in self.etree.getTerminals():
            queue.append(terminal)
        # Visit each node in the queue and put parent
        # in queue if not there already
        # Parent is there already if it is the last one in the queue
        while len(queue) > 0:
            currentNode = queue.pop(0)
          # Put parent in the queue if it is not there already
          # We are guaranteed to have visited all of a node's children before we visit that node
            for edgeToParent in currentNode.parent:
                edgeToParent["parent"].unprocessedChildNum -= 1
                if edgeToParent["parent"].unprocessedChildNum == 0:
                    queue.append(edgeToParent["parent"])
      
          # Visit node here.
            if currentNode.data["pos"] != "TOP":
                self.terminal_operation(currentNode)
            if len(currentNode.hyperEdges) > 0:
                self.nonterminal_operation_cube(currentNode)

    ################################################################################
    # nonterminal_operation_cube(self, currentNode):
    # Perform alignment for visit of nonterminal currentNode
    ################################################################################
    def nonterminal_operation_cube(self, currentNode): 
        # To speed up each epoch of training (but not necessarily convergence),
        # generate a single forest with model score as thz objective
        # Search through that forest for the oracle hypotheses,
        # e.g. hope (or fear)
  
        # Compute the span of currentNode
        # span is an ordered pair [i,j] where:
        # i = index of the first eword in span of currentNode
        # j = index of the  last eword in span of currentNode
        currentNode.span = (currentNode.span_start(), currentNode.span_end())

    	############################# Start of hypothesis calculation ####################################
        self.kbest(currentNode, "hyp")   
    	############################# End of hypothesis calculation ####################################
  
        ############################# Start of oracle calculation("oracle" or "hope") ######################################
        if self.COMPUTE_ORACLE:
          # Oracle BEFORE beam is applied.
          # Should just copy oracle up from terminal nodes.
          best = PartialGridAlignment()
          best.fscore = -1.0 # Any negative value suffices
          for hyperEdge in currentNode.hyperEdges:
              oracleChildEdges = [c.oracle for c in hyperEdge.tail]
              if currentNode.oracle:
                  oracleChildEdges.append(currentNode.oracle)
              oracleAlignment, boundingBox = self.createEdge(oracleChildEdges, currentNode, currentNode.span, hyperEdge)
              if oracleAlignment.fscore > best.fscore:
                  best = oracleAlignment
          currentNode.partialAlignments["oracle"] = currentNode.oracle = best
          # Oracle AFTER beam is applied.
          #oracleCandidates = list(currentNode.partialAlignments)
          #oracleCandidates.sort(key=attrgetter('fscore'),reverse=True)
          #oracleAlignment = oracleCandidates[0]
          # currentNode.oracle = oracleAlignment
        elif self.COMPUTE_HOPE:
            self.kbest(currentNode, "oracle")
             
    def createEdge(self, childEdges, currentNode, span, hyperEdge):
      """
      Create a new edge from the list of edges 'edge'.
      Creating an edge involves:
      (1) Initializing the PartialGridAlignment data structure
      (2) Adding links (f,e) to list newEdge.links
      (3) setting the score of the edge with scoreEdge(newEdge, ...)
      In addition, set the score of the new edge.
      """
      newEdge = PartialGridAlignment()
      newEdge.scoreVector_local = svector.Vector()
      newEdge.scoreVector = svector.Vector()
      newEdge.hyperEdgeScore = hyperEdge.score
  
      for index, e in enumerate(childEdges):
          newEdge.links += e.getDepthAddedLink()
          newEdge.scoreVector_local += e.scoreVector_local
          newEdge.scoreVector += e.scoreVector
  
          if e.boundingBox is None:
              e.boundingBox = self.boundingBox(e.links)
      score, boundingBox = self.scoreEdge(newEdge, currentNode, span, childEdges)
      return newEdge, boundingBox
  
    ############################################################################
    # scoreEdge(self, edge, currentNode, srcSpan, childEdges):
    ############################################################################
    def scoreEdge(self, edge, currentNode, srcSpan, childEdges):
      """
      Score an edge.
      (1) edge: new hyperedge in the alignment forest, tail of this hyperedge are the edges in childEdges
      (2) currentNode: the currentNode in the tree
      (3) srcSpan: span (i, j) of currentNode; i = index of first terminal node in span, j = index of last terminal node in span
      (4) childEdges: the two (or more in case of general trees) nodes we are combining with a new hyperedge
      """

      if self.COMPUTE_ORACLE:
          edge.fscore = self.ff_fscore(edge, srcSpan)
  
      boundingBox = None
      if self.DO_RESCORE:
          ##################################################################
          # Compute data needed for certain feature functions
          ##################################################################
          tgtSpan = None
          if len(edge.links) > 0:
              boundingBox = self.boundingBox(edge.links)
              tgtSpan = (boundingBox[0][0], boundingBox[1][0])
          edge.boundingBox = boundingBox
  
          # TODO: This is an awful O(l) patch of code
          linkedIndices = defaultdict(list)
          for link in edge.links:
              fIndex = link[0]
              eIndex = link[1]
              linkedIndices[fIndex].append((eIndex,link.depth))
  
          scoreVector = svector.Vector(edge.scoreVector)
  
          if currentNode.data is not None and currentNode.data is not '_XXX_':
              for _, func in enumerate(self.featureTemplates_nonlocal):
                  value_dict = func(self.info, currentNode, edge, edge.links, srcSpan, tgtSpan, linkedIndices, childEdges, self.diagValues, self.treeDistValues)
                  for name, value in value_dict.iteritems():
                      if value != 0:
                          scoreVector[name] = value
          edge.scoreVector = scoreVector
  
          ##################################################
          # Compute final score for this partial alignment
          ##################################################
          edge.score = edge.scoreVector.dot(self.weights)
      return edge.score, boundingBox
  
    def boundingBox(self, links):
        """
        Return a 2-tuple of ordered paris representing
        the bounding box for the links in list 'links'.
        (upper-left corner, lower-right corner)
        """
        # upper left corner is (min(fIndices), min(eIndices))
        # lower right corner is (max(fIndices, max(eIndices))
  
        minF = float('inf')
        maxF = float('-inf')
        minE = float('inf')
        maxE = float('-inf')
  
        for link in links:
            fIndex = link[0]
            eIndex = link[1]
            if fIndex > maxF:
                maxF = fIndex
            if fIndex < minF:
                minF = fIndex
            if eIndex > maxE:
                maxE = eIndex
            if eIndex < minE:
                minE = eIndex
        # This box is the top-left corner and the lower-right corner
        box = ((minF, minE), (maxF, maxE))
        return box

    def terminal_operation(self, currentNode = None):
        """
        Fire features at (pre)terminal nodes of the tree.
        """
        ##################################################
        # Setup
        ##################################################
  
        partialAlignments = []
        oracleAlignment = []
  
        heapify(partialAlignments)
  
        tgtWordList = self.f
        srcWordList = self.e
        tgtWord = None
        srcWord = currentNode.data["surface"]
        srcTag = currentNode.data["pos"]
        tgtIndex = None
        srcIndex = currentNode.data["word_id"]
  
        span = (srcIndex, srcIndex)
  
        ##################################################
        # null partial alignment ( assign no links )
        ##################################################
        tgtIndex = -1
        tgtWord = '*NULL*'
        scoreVector = svector.Vector()
        # Compute feature score
  
        for k, func in enumerate(self.featureTemplates):
            value_dict = func(self.info, tgtWord, srcWord, tgtIndex, srcIndex, [], self.diagValues, currentNode)
            for name, value in value_dict.iteritems():
                if value != 0:
                    scoreVector[name] += value
  
        nullPartialAlignment = PartialGridAlignment()
        nullPartialAlignment.score = score = scoreVector.dot(self.weights)
        nullPartialAlignment.scoreVector = scoreVector
        nullPartialAlignment.scoreVector_local = svector.Vector(scoreVector)
        nullPartialAlignment.score = self.hypScoreFunc(nullPartialAlignment)
        self.addPartialAlignment(partialAlignments, nullPartialAlignment, self.BEAM_SIZE)
        nullPartialAlignment.score = self.oracleScoreFunc(nullPartialAlignment)

        if not self.DECODING:
            nullPartialAlignment.fscore = self.ff_fscore(nullPartialAlignment, span)

        if self.COMPUTE_ORACLE:
            oracleAlignment = nullPartialAlignment
        elif self.COMPUTE_HOPE:
            self.addPartialAlignment(oracleAlignments, nullPartialAlignment, self.BEAM_SIZE)
  
        ##################################################
        # Single-link alignment
        ##################################################
        singleBestAlignment = []
        alignmentList = []
        for tgtIndex, tgtWord in enumerate(tgtWordList):
          currentLinks = [AlignmentLink((tgtIndex, srcIndex))]
          scoreVector = svector.Vector()
  
          for k, func in enumerate(self.featureTemplates):
            value_dict = func(self.info, tgtWord, srcWord, tgtIndex, srcIndex, currentLinks, self.diagValues, currentNode)
            for name, value in value_dict.iteritems():
              if value != 0:
                scoreVector[name] += value
  
          # Keep track of scores for all 1-link partial alignments
          score = scoreVector.dot(self.weights)
          singleBestAlignment.append((score, [tgtIndex]))
  
          singleLinkPartialAlignment = PartialGridAlignment()
          singleLinkPartialAlignment.score = score
          singleLinkPartialAlignment.scoreVector = scoreVector
          singleLinkPartialAlignment.scoreVector_local = svector.Vector(scoreVector)
          singleLinkPartialAlignment.links = currentLinks
  
          self.addPartialAlignment(partialAlignments, singleLinkPartialAlignment, self.BEAM_SIZE)
  
          if not self.DECODING:
              singleLinkPartialAlignment.fscore = self.ff_fscore(singleLinkPartialAlignment, span)
  
          if self.COMPUTE_ORACLE:
            if singleLinkPartialAlignment.fscore > oracleAlignment.fscore:
              oracleAlignment = singleLinkPartialAlignment
          elif self.COMPUTE_HOPE:
            singleLinkPartialAlignment.score = self.oracleScoreFunc(singleLinkPartialAlignment)
            self.addPartialAlignment(oracleAlignment, singleLinkPartialAlignment, self.BEAM_SIZE)
  
          if self.COMPUTE_FEAR:
            singleLinkPartialAlignment.score = self.hypScoreFunc(singleLinkPartialAlignment)
            self.addPartialAlignment(partialAlignments, singleLinkPartialAlignment, self.BEAM_SIZE)

        alignmentList = singleBestAlignment
        singleBestAlignment.sort(reverse=True)
        ##################################################
        # N link alignment(N>=2)
        ##################################################
        # Get ready for N-link alignments(N>=2)
        for i in xrange(2,self.nto1+1): 
            # Sort the fwords by score
            alignmentList.sort(reverse=True)
            newAlignmentList = []
            LIMIT_1 = max(10, self.lenF/2)
            LIMIT_N = max(10, self.lenF/i)
            for (_,na) in alignmentList[0:LIMIT_N]:# na means n link alignment
                for (_, sa) in singleBestAlignment[0:LIMIT_1]:#sa means single-link alignment
                    if(na[-1]>=sa[0]):#sa actually always have only one element
                        continue
                    # clear contents of twoLinkPartialAlignment
                    tgtIndex_a = na[-1]
                    tgtIndex_b = sa[0]
                    # Don't consider a pair (tgtIndex_a, tgtIndex_b) if distance between
                    # these indices > 1 (Arabic/English only).
                    # Need to debug feature that is supposed to deal with this naturally.
                    if self.LANG == "ar_en":
                        if (abs(tgtIndex_b - tgtIndex_a) > 1):
                            continue
  
                    currentLinks = list(map(lambda x: AlignmentLink((x,srcIndex)),na+sa))
                      
                    scoreVector = svector.Vector()
                    for k, func in enumerate(self.featureTemplates):
                        value_dict = func(self.info, tgtWord, srcWord,
                                          tgtIndex, srcIndex, currentLinks,
                                          self.diagValues, currentNode)
                        for name, value in value_dict.iteritems():
                            if value != 0:
                                scoreVector[name] += value
  
                    score = scoreVector.dot(self.weights)
                    newAlignmentList.append((score, na+sa))
  
                    NLinkPartialAlignment = PartialGridAlignment()
                    NLinkPartialAlignment.score = score
                    NLinkPartialAlignment.scoreVector = scoreVector
                    NLinkPartialAlignment.scoreVector_local = svector.Vector(scoreVector)
                    NLinkPartialAlignment.links = currentLinks
                    self.addPartialAlignment(partialAlignments, NLinkPartialAlignment, self.BEAM_SIZE)
                   
                    if not self.DECODING:
                        NLinkPartialAlignment.fscore = self.ff_fscore(NLinkPartialAlignment, span)
  
                    if self.COMPUTE_ORACLE:
                        if NLinkPartialAlignment.fscore > oracleAlignment.fscore:
                            oracleAlignment = NLinkPartialAlignment
                    elif self.COMPUTE_HOPE:
                        NLinkPartialAlignment.score = self.oracleScoreFunc(NLinkPartialAlignment)
                        self.addPartialAlignment(oracleAlignment, NLinkPartialAlignment, self.BEAM_SIZE)
  
                    if self.COMPUTE_FEAR:
                        NLinkPartialAlignment.score = self.hypScoreFunc(NLinkPartialAlignment)
                        self.addPartialAlignment(partialAlignments, NLinkPartialAlignment, self.BEAM_SIZE)
            alignmentList = newAlignmentList 
  
        ########################################################################
        # Finalize. Sort model-score list and then hope list.
        ########################################################################
        # Sort model score list.
        sortedBestFirstPartialAlignments = []
        while len(partialAlignments) > 0:
          sortedBestFirstPartialAlignments.insert(0,heappop(partialAlignments))
        # Sort hope score list.
        if self.COMPUTE_HOPE:
          sortedBestFirstPartialAlignments_oracle = []
          while len(oracleAlignment) > 0:
            sortedBestFirstPartialAlignments_oracle.insert(0,heappop(partialAlignments))
  
        currentNode.partialAlignments["hyp"] = sortedBestFirstPartialAlignments
        if self.COMPUTE_HOPE:
          currentNode.partialAlignments["oracle"] = sortedBestFirstPartialAlignments_oracle
        elif self.COMPUTE_ORACLE:
          # Oracle BEFORE beam is applied
          currentNode.partialAlignments["oracle"] = currentNode.oracle = oracleAlignment
  
          # Oracle AFTER beam is applied
          #oracleCandidates = list(partialAlignments)
          #oracleCandidates.sort(key=attrgetter('fscore'),reverse=True)
          #currentNode.oracle = oracleCandidates[0]
    ############################################################################
    # addPartialAlignment(self, list, partialAlignment):
    # Add partial alignment to the list of possible partial alignments
    # - Make sure we only keep P partial alignments at any one time
    # - If new partial alignment is > than min(list)
    # - - Replace min(list) with new partialAlignment
    ############################################################################
  
    def addPartialAlignment(self, list, partialAlignment, BEAM_SIZE):
        # Sort this heap with size limit self.BEAM_SIZE in worst-first order
        # A low score is worse than a higher score
        if len(list) < BEAM_SIZE:
            heappush(list, partialAlignment)
        elif partialAlignment > list[0]:
            heappushpop(list, partialAlignment)
  
    ############################################################################
    # ff_fscore(self):
    # Compute f-score of an edge with respect to the entire gold alignment
    # It shouldn't matter if we compute f-score of an edge wrt the entire
    # alignment or wrt the same piece of the gold alignment. The fscore for the
    # former will just have a lower recall figure.
    ############################################################################
  
    def ff_fscore(self, edge, span = None):
      if span is None:
        span = (0, len(self.e)-1)
  
      # get gold matrix span that we are interested in
      # Will be faster than using the matrix operation since getLinksByEIndex
      # returns a sparse list. We also memoize.
      numGoldLinks = self.gold.numLinksInSpan.get(span, None)
      if numGoldLinks is None:
        numGoldLinks = len(self.gold.getLinksByEIndex(span))
        self.gold.numLinksInSpan[span] = numGoldLinks
      else:
        numGoldLinks = self.gold.numLinksInSpan[span]
  
      # Count our links within this span.
      numModelLinks = len(edge.links)
  
      # (1) special case: both empty
      if numGoldLinks == 0 and numModelLinks == 0:
        return 1.0
      # (2) special case: gold empty, model not empty OR
      #     gold empty and model not empty
      elif numGoldLinks == 0 or numModelLinks == 0:
        return 0.0
  
      # The remainder here is executed when numGoldLinks > 0 and
      # numModelLinks > 0
  
      inGold = self.gold.links_dict.has_key
      numCorrect = 0

      for link in edge.links:
          numCorrect += inGold(link.link)
      numCorrect = float(numCorrect)
  
      precision = numCorrect / numModelLinks
      recall = numCorrect / numGoldLinks
  
      if precision == 0 or recall == 0:
        return 0.0
      f1 = (2*precision*recall) / (precision + recall)
      # Favor recall a la Fraser '07
      # f_recall = 1./((0.1/precision)+(0.9/recall))
      return f1

    def kbest(self, currentNode, type = "hyp"):
        # Initialize
        queue = []
        heapify(queue)
        oneColumnAlignments = currentNode.partialAlignments[type] # creates kind of dummy terminal for nonterminal node
        currentNode.partialAlignments[type] = []
        # Before we push, check to see if object's position is in duplicates
        # i.e., we have already visited that position and added the resultant object to the queue
        count = defaultdict(lambda: defaultdict(int))

        for hyperEdgeNumber, hyperEdge in enumerate(currentNode.hyperEdges):
            arity = len(hyperEdge.tail) 
        
            # Number of components in position vector is the number of children in the current node
            # Position vector uniquely identifies a position in the cube
            # and identifies a unique alignment structure
            position = [0]*(arity+1)
  
            # Create structure of first object in position [0,0,0,...,0]
            # This path identifies the structure that is the best structure
            # we know of before combination costs (rescoring).
            edges = [ ]
            for c in xrange(arity):
                # Object number for current child
                edgeNumber = position[c]
                currentChild = hyperEdge.tail[c]
                edge = currentChild.partialAlignments[type][edgeNumber]
                edges.append(edge)
            if len(oneColumnAlignments) > 0:
                edges.append(oneColumnAlignments[position[-1]])
            newEdge, boundingBox = self.createEdge(edges, currentNode, currentNode.span, hyperEdge)
            if type == "hyp":
                newEdge.score = self.hypScoreFunc(newEdge)
            else:
                newEdge.score = self.oracleScoreFunc(newEdge)
            # Where did this new edge come from?
            newEdge.position = list(position)
            # Which hyper edge is newEdge created from?
            newEdge.hyperEdgeNumber = hyperEdgeNumber
            # Add new edge to the queue/buffer
            heappush(queue, (newEdge.score*-1, newEdge))
  
        # Keep filling up my cell until self.BEAM_SIZE has been reached *or*
        # we have exhausted all possible items in the queue
        while(len(queue) > 0 and len(currentNode.partialAlignments[type]) < self.NT_BEAM):
            # Find current best
            (_, currentBestCombinedEdge) = heappop(queue)
            arity = len(currentNode.hyperEdges[currentBestCombinedEdge.hyperEdgeNumber].tail)
            # Add to my cell
            self.addPartialAlignment(currentNode.partialAlignments[type], currentBestCombinedEdge, self.NT_BEAM)
            # Don't create and score more edges when we are already full.
            if len(currentNode.partialAlignments[type]) >= self.NT_BEAM:
                break
            # - Find neighbors
            # - Rescore neighbors
            # - Add neighbors to the queue to be explored
            #   o For every child, there exists a neighbor
            #   o numNeighbors = numChildren
            for componentNumber in xrange(arity+1):
                # Compute neighbor position
                neighborPosition = list(currentBestCombinedEdge.position)
                neighborPosition[componentNumber] += 1
                # Is this neighbor out of range?
                if componentNumber >= arity:
                    if neighborPosition[componentNumber] >= len(oneColumnAlignments):
                        continue
                else:
                    if neighborPosition[componentNumber] >= len(currentNode.hyperEdges[currentBestCombinedEdge.hyperEdgeNumber].tail[componentNumber].partialAlignments[type]):
                        continue
                # Has this neighbor already been visited?
                #if duplicates.has_key(tuple(neighborPosition)):
                #    continue
                # Lazy eval trick due to Matthias Buechse:
                # Only evaluate after both a node's predecessors have been evaluated.
                # Special case: if any component of neighborPosition is 0, it is on the border.
                # In this case, it only has one predecessor (the one that led us to this position),
                # and can be immediately evaluated.
                # if 0 not in neighborPosition and count[tuple(neighborPosition)] < 1: # this only works when number of children is 2, I think
                if count[currentBestCombinedEdge.hyperEdgeNumber][tuple(neighborPosition)] < arity - neighborPosition.count(0): # arity + 1 - neighborPosition.count(0) - 1
                    count[currentBestCombinedEdge.hyperEdgeNumber][tuple(neighborPosition)] += 1
                    continue
  
                # Now build the neighbor edge
                neighbor = []
                for cellNumber in xrange(arity):
                    cell = currentNode.hyperEdges[currentBestCombinedEdge.hyperEdgeNumber].tail[cellNumber]
                    edgeNumber = neighborPosition[cellNumber]
                    edge = cell.partialAlignments[type][edgeNumber]
                    neighbor.append(edge)

                if len(oneColumnAlignments) > 0:
                    neighbor.append(oneColumnAlignments[neighborPosition[-1]])

                neighborEdge, boundingBox = self.createEdge(neighbor, currentNode, currentNode.span, hyperEdge)
                neighborEdge.position = neighborPosition
                neighborEdge.hyperEdgeNumber = currentBestCombinedEdge.hyperEdgeNumber
                if type == "hyp":
                    neighborEdge.score = self.hypScoreFunc(neighborEdge)
                else:
                    neighborEdge.score = self.oracleScoreFunc(neighborEdge)
                heappush(queue, (-1*neighborEdge.score, neighborEdge))

        ####################################################################
        # Finalize.
        ####################################################################
        # Sort model score list.
        sortedItems = []
        while(len(currentNode.partialAlignments[type]) > 0):
            sortedItems.insert(0, heappop(currentNode.partialAlignments[type]))
        currentNode.partialAlignments[type] = sortedItems
