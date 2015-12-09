from collections import defaultdict
import math

class NgramLMNode:
    def __init__(self):
        self.prob = defaultdict(float)
        self.count = defaultdict(int)
        self.children = defaultdict(NgramLMNode)

    def clear(self):
        self.prob.clear()
        self.children.clear()

    def addNgramCount(self, word, context, count = 1):
        """
        word: w_{i}
        context: [w_{i-1}, w_{i-2},..., w_{i-n+1}]
        count: How many counts to add; default: 1
        """        
        self.count[word] += count
        if len(context) > 0:
            self.children[context[0]].addNgramCount(word, context[1:], count)

    def addNgramProb(self, word, context, prob):
        """
        word: w_{i}
        context: [w_{i-1}, w_{i-2},..., w_{i-n+1}]
        prob: probability to add 
        """        
        self.prob[word] += prob
        if len(context) > 0:
            self.children[context[0]].addNgramProb(word, context[1:], prob)


    def mlEstimate(self):
        numOfToken = sum(self.count.itervalues())
        for word in self.count.iterkeys():
            self.prob[word] = math.log10(self.count[word]) - math.log10(numOfToken)
        for word, child in self.children.iteritems():
            child.mlEstimate()
