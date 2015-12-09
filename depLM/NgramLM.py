from NgramLMNode import NgramLMNode
import math

class NgramLM:
    def __init__(self, n):
        self._root = NgramLMNode()
        self.order = n

    def _decomposeNgram(self, ngram):
        if len(ngram) == 0:
            raise ValueError("ngram length must not be zero!")
        context = []
        if len(ngram) > 1:
            context = ngram[0:-1]
            context.reverse()
        word = ngram[-1]
        return word, context

    def addNgramCount(self, ngram, count = 1):
        """
        ngram: list of string [w_{i-n+1},...,w_{i}]
        """
        assert len(ngram) == self.order, "Length of ngram is not the same as the one you specified during the initialization!"

        word, context = self._decomposeNgram(ngram)
        self._root.addNgramCount(word, context, count)

    def addNgramProb(self, ngram, prob = 0.0):
        assert len(ngram) == self.order, "Length of ngram is not the same as the one you specified during the initialization!"
        word, context = self._decomposeNgram(ngram)
        self._root.addNgramProb(word, context, prob)

    def saveNgramInfo(self, filename = None, fstream = None, countOnly = False):
        if not ((filename is None) ^ (fstream is None)):
            raise ValueError("One of filename and fstream should be set")

        if filename is not None:
            with open(filename, "w") as fstream:
                self._saveNgramInfo(fstream, self._root, [], countOnly)
        else:
                self._saveNgramInfo(fstream, self._root, [], countOnly)

    def _saveNgramInfo(self, fstream, node, context, countOnly):
        if len(node.children) == 0: # Reached highest order node?
            for word in node.prob.iterkeys():
                ngram = context + [word]
                if countOnly:
                    fstream.write("%s\t%d\n" % (" ".join(ngram), node.count[word]))
                else:
                    fstream.write("%s\t%d\t%f\n" % (" ".join(ngram), node.count[word], node.prob[word]))
        else:
            for word in node.children.iterkeys():
                context.insert(0, word)
                self._saveNgramInfo(fstream, node.children[word], context, countOnly)
                context.pop(0)

    def writeMessage(self, ngramEntries):
        """
        Write ngram infos to ngramEntries
        """
        self._writeMessage(ngramEntries,  self._root, [])
        
    def _writeMessage(self, ngramEntries, node, context):
        if len(node.children) == 0: # Reached highest order node?
            for word in node.prob.iterkeys():
                ngram = context + [word]
                ngramEntry = ngramEntries.add()
                ngramEntry.prob = node.prob[word]
                ngramEntry.count = node.count[word]
                for word in ngram:
                    ngramEntry.ngram.append(word)
        else:
            for word in node.children.iterkeys():
                context.insert(0, word)
                self._writeMessage(ngramEntries, node.children[word], context)
                context.pop(0)


    def mlEstimate(self):
        self._root.mlEstimate()

    def stupidBackoffProb(self, ngram, discount = 0.4):
        """
        Reference: http://www.aclweb.org/anthology/D07-1090.pdf
        """
        context = []
        prob = 0.0
        bow = 0.0
        discount = math.log10(discount)
        curNode = self._root
        clen = 0
        if len(ngram) > 1:
            context = ngram[0:-1]
            context.reverse()
        word = ngram[-1]
        while len(context) >= 0:
            if curNode.prob.has_key(word):
                prob = curNode.prob[word]
                bow = 0.0
            else:
                return -10 # any negative small number suffices
            if len(context) == 0:
                break
            if not curNode.children.has_key(context[0]):
                for i in xrange(len(context)):
                    bow += discount
                break
            curNode = curNode.children[context[0]]
            bow += discount
            context = context[1:]

        return prob + bow
