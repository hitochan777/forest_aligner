#########################################################
# Features.py
# riesa@isi.edu (Jason Riesa)
# Feature Function Templates
#########################################################

from collections import defaultdict
import sys
from pyglog import *
from AlignmentLink import AlignmentLink
from LinkTag import LinkTag

class LocalFeatures:
    def __init__(self, pef, pfe):
        self.null_token = "*NULL*"
        self.pef = pef
        self.pfe = pfe
        self.punc = {',':True,'.':True,'!':True,'?':True,"'":True,'"':True,
                     ')':True,'(':True,':':True,';':True,'-':True,'@':True}
        # Chinese punctuation
        self.punc[u'\u3002']=True # Chinese period
        self.punc[u'\u201c']=True # Chinese quote
        self.punc[u'\u201d']=True # Chinese quote
        self.punc[u'\uff0c']=True # Chinese comma
        self.punc[u'\u3001']=True # Chinese comma
        self.punc[u'\uff0d']=True # Chinese dash
        self.punc[u'\uff1f']=True # Chinese question mark
        self.months = {'january':True, 'february':True,'march':True,'april':True,
                       'may':True,'june':True,'july':True,'august':True,
                       'september':True,'october':True,'november':True,
                       'december':True,
                       'jan':True,'feb':True,'mar':True,'apr':True,'jun':True,
                       'jul':True,'aug':True,'sep':True,'nov':True,'dec':True,
                       'jan.':True,'feb.':True,'mar.':True,'apr.':True,
                       'jun.':True,'jul.':True,'aug.':True,'sep.':True,
                       'nov.':True,'dec.':True}

    def ff_thirdParty(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Fire feature if links appear in third-party alignments.
        """
        values = { }
        if len(links) == 0:
            return values

        name = self.ff_thirdParty.func_name
        a1 = True
        a2 = True
        inverse = True

        for link in links:
            if link.link not in info['a1']:
                a1 = False
            if link.link not in info['a2']:
                a2 = False
            if link.link not in info['inverse']:
                inverse = False

        # Encode results as features
        if inverse:
            values[name+'_inv'] = 1
            values[name+'_inv_%s' % (currentNode.getPOS())] = 1
            values[name+'_inv_(%s)' % (currentNode.data["surface"])] = 1
            values[name+'_inv_%s(%s)' % (currentNode.getPOS(), currentNode.data["surface"])] = 1
        if a1:
            values[name+'_a1'] = 1
            values[name+'_a1_%s' % (currentNode.getPOS())] = 1
            values[name+'_a1_(%s)' % (currentNode.data["surface"])] = 1
            values[name+'_a1_%s(%s)' % (currentNode.getPOS(), currentNode.data["surface"])] = 1
        if a2:
            values[name+'_a2'] = 1
            values[name+'_a2_%s' %(currentNode.getPOS())] = 1
            values[name+'_a2_(%s)' % (currentNode.data["surface"])] = 1
            values[name+'_a2_%s(%s)' % (currentNode.getPOS(), currentNode.data["surface"])] = 1

        return values

    def ff_probFgivenE(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Return p(f|e)
        """
        if currentNode is not None:
            pos = currentNode.getPOS()
        name = self.ff_probFgivenE.func_name + '___' + pos + '_nb'

        # Calculate feature function value
        sum = 0.0
        numLinks = len(links)
        if numLinks > 0:
            for link in links:
                fWord = info['f'][link[0]]
                eWord = info['e'][link[1]]
                sum += self.pfe.get(eWord, {}).get(fWord, 0.0)
        else:
            sum = self.pfe.get(eWord, {}).get(fWord, 0.0)
        if numLinks > 1:
            sum /= float(numLinks)

        return {name: sum}

    def ff_probFgivenETag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Return p(e|f)
        """
        values = defaultdict(float)
        if currentNode is not None:
            pos = currentNode.getPOS()

        name = self.ff_probFgivenETag.func_name + '___' + pos
        # Calculate feature function value
        sum = 0.0
        numLinks = len(links)
        for link in links:
            fWord = info['f'][link[0]]
            eWord = info['e'][link[1]]
            values[name+'___' + link.linkTag.name + '_nb'] += self.pfe.get(eWord, {}).get(fWord, 0.0)/numLinks

        return values

    def ff_probEgivenFTag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        """
        values = defaultdict(float)
        if currentNode is not None:
            pos = currentNode.getPOS()

        name = self.ff_probEgivenFTag.func_name + '___' + pos
        # Calculate feature function value
        sum = 0.0
        numLinks = len(links)
        for link in links:
            fWord = info['f'][link[0]]
            eWord = info['e'][link[1]]
            values[name+'___' + link.linkTag.name + '_nb'] += self.pef.get(fWord, {}).get(eWord, 0.0)/numLinks

        return values

    def ff_probEgivenF(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Return average p(e|f)
        """
        if currentNode is not None:
            pos = currentNode.getPOS()
        name = self.ff_probEgivenF.func_name + '___' + pos + '_nb'

        # Calculate feature function value
        sum = 0.0
        numLinks = len(links)
        if numLinks > 0:
            for link in links:
                fWord = info['f'][link[0]]
                eWord = info['e'][link[1]]
                sum += self.pef.get(fWord, {}).get(eWord, 0.0)
        else:
            sum = self.pef.get(fWord, {}).get(eWord, 0.0)
        if numLinks > 1:
            sum /= float(numLinks)

        return {name: sum}

    def ff_identity(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Return 1 if fWord == eWord; 0 otherwise.
        """
        name = self.ff_identity.func_name
        if len(links) == 1:
            link = links[0]
            CHECK_GT(len(info['f']), 0, "Length of f sentence is 0.")
            CHECK_GT(len(info['e']), 0, "Length of e sentence is 0.")

            if info['f'][link[0]] == info['e'][link[1]]:
                return {name: 1.0}
        return {name: 0.0}

    def ff_identityTag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Return 1 if fWord == eWord; 0 otherwise.
        """
        name = self.ff_identityTag.func_name

        if len(links) == 1:
            link = links[0]
            CHECK_GT(len(info['f']), 0, "Length of f sentence is 0.")
            CHECK_GT(len(info['e']), 0, "Length of e sentence is 0.")
            name = name + '___' + link.linkTag.name
            if info['f'][link[0]] == info['e'][link[1]]:
                return {name: 1.0}

        return {name: 0.0}

    def ff_distToDiag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Average (Normalized) Distance from the point (fIndex,eIndex) to the grid diagonal
        """
        if currentNode is not None:
            pos = currentNode.getPOS()
        name = self.ff_distToDiag.func_name + '___' + pos + '_nb'

        val = 0.0

        if len(links) > 0:
            for link in links:
                fIndex = link[0]
                eIndex = link[1]
                if diagValues.has_key((fIndex, eIndex)):
                    val += abs(diagValues[(fIndex, eIndex)])
                else:
                    val += abs(self.pointLineGridDistance(info['f'], info['e'], fIndex, eIndex))
                    # Save value for later use.
                    diagValues[(fIndex, eIndex)] = val
            val /= len(links)
        return {name: val}

    def ff_distToDiagTag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Average (Normalized) Distance from the point (fIndex,eIndex) to the grid diagonal
        """
        if currentNode is not None:
            pos = currentNode.getPOS()

        values = defaultdict(float)
        name = self.ff_distToDiagTag.func_name + '___' + pos

        for linkTag in LinkTag:
            values[name + '___' + linkTag.name + '_nb'] = 0.0

        if len(links) > 0:
            for link in links:
                fIndex = link[0]
                eIndex = link[1]
                if not diagValues.has_key((fIndex, eIndex)):
                    # Save value for later use.
                    diagValues[(fIndex, eIndex)] = abs(self.pointLineGridDistance(info['f'], info['e'], fIndex, eIndex))

                val = diagValues[(fIndex, eIndex)]
                values[name + '___' + link.linkTag.name + '_nb'] += val/len(links)

        return values 

    ################################################################################
    # ff_tgtTag_srcTag
    ################################################################################
    def ff_tgtTag_srcTag(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Compute targetTag, srcTag indicator features.
        We also lexicalize by the eWord.
        Uncomment value3 below to include lexicalized features by fword.
        """
        name = self.ff_tgtTag_srcTag.func_name

        if info['ftree'] is None:
            return {}
        if len(info['ftree'].terminals) == 0:
            return {}

        tgtTag = currentNode.getPOS()
        srcTags = ""

        values = {}
        probDictList = [defaultdict(float)]*2

        if len(links) == 0:
            srcTag = "*NULL*"
            values["%s___%s:%s" % (name, tgtTag, srcTag)] = 1
            values["%s___%s(%s):%s"% (name, tgtTag, eWord, srcTag)] = 1
            # Uncomment to add feature lexicalized by fword
            # values["%s___%s:%s(%s)"% (name, tgtTag, srcTag, fWord)] = 1
        else:
            for i ,link in enumerate(links):
                findex = link[0]
                probDictList[(i+1)%2] = defaultdict(float)
                nodes =  info['ftree'].getNodesByIndex(findex)
                pos_count = defaultdict(float)
                for node in nodes:
                    pos_count[node.getPOS()] += 1
                total = sum(pos_count.values())
                # normalize count
                for srcTag in pos_count:
                    pos_count[srcTag] /= float(total)
                if len(probDictList[i%2])==0:
                    probDictList[(i+1)%2] = pos_count
                else:
                    for srcTags, prob in probDictList[i%2].iteritems(): # In python3 iteritems is replaced with items
                        for srcTag in pos_count:
                            probDictList[(i+1)%2]["%s,%s" % (srcTags, srcTag)] = prob*pos_count[srcTag]
            total = 0.0
            for srcTags, prob in probDictList[len(links)%2].iteritems():
                total += prob
                values["%s___%s:%s" % (name, tgtTag, srcTags)] = prob
                values["%s___%s(%s):%s"% (name, tgtTag, eWord, srcTags)] = prob
                # Uncomment to add feature lexicalized by fword
                # values["%s___%s:%s(%s)"% (name, tgtTag, srcTags, fWord)] = prob
            assert total <= 1.0 + 1e-06 and total >= 1.0 - 1e-06, "The probability does not sum to 1!!"
            # for key in values:
                # print key, values[key]
        return values

    def ff_tgtTag_srcTagTag(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Compute targetTag, srcTag indicator features.
        We also lexicalize by the eWord.
        """
        name = self.ff_tgtTag_srcTagTag.func_name

        if info['ftree'] is None:
            return {}
        if len(info['ftree'].terminals) == 0:
            return {}
        if len(links) == 0:
            return {}

        tgtTag = currentNode.getPOS()
        srcTags = ""

        values = {}
        pos_count = defaultdict(float)

        for i ,link in enumerate(links):
            findex = link[0]
            nodes = info['ftree'].getNodesByIndex(findex)
            for node in nodes:
                pos_count[(node.getPOS(), link.linkTag.name)] += 1.0/len(nodes)

        for key in pos_count:
            pos_count[key] /= len(links)

        for (srcTag, linkTag), prob in pos_count.iteritems():
            values["%s___%s:%s___%s" % (name, tgtTag, srcTag, linkTag)] = prob
            values["%s___%s(%s):%s___%s"% (name, tgtTag, eWord, srcTag, linkTag)] = prob

        return values
 
    def ff_englishCommaLinkedToNonComma(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires if eWord ',' is linked to a non-comma.
        """
        name = self.ff_englishCommaLinkedToNonComma.func_name

        if eWord == ',':
            fwords = [info['f'][link[0]] for link in links]
            for fword in fwords:
                if eWord == ',' and fword != ',':
                    return {name: 1.0}
        return {name: 0.0}

    def ff_englishCommaLinkedToNonCommaTag(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires if eWord ',' is linked to a non-comma.
        """
        name = self.ff_englishCommaLinkedToNonCommaTag.func_name
        count = defaultdict(float)
        values = defaultdict(float)

        for linkTag in LinkTag:
            values["%s___%s" % (name, linkTag.name)] = 0.0 
        if eWord == ',':
            for link in links:
                fword = info['f'][link[0]]
                if fword != ',':
                    count[link.linkTag.name] += 1.0/len(links)
            
            for linkTag, cnt in count.iteritems():
                values["%s___%s" % (name, linkTag)] = cnt

        return values

    def ff_finalPeriodAlignedToNonPeriod(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires if last token in e-sentence is a period and is
        aligned to a non-period.
        """
        name = self.ff_finalPeriodAlignedToNonPeriod.func_name
        if eIndex != len(info['e'])-1:
            flag=False
            for link in links:
                if link[0] == len(info['f'])-1:
                    flag=True
                    break
            if not flag:
                return {name: 0.}

        if eWord == ".":
            for link in links:
                if info['f'][link[0]] != ".":
                    return {name: 1.}
        return {name: 0.}

    def ff_finalPeriodAlignedToNonPeriodTag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires if last token in e-sentence is a period and is
        aligned to a non-period.
        """
        name = self.ff_finalPeriodAlignedToNonPeriodTag.func_name
        values = defaultdict(float)
        for linkTag in LinkTag:
            values["%s___%s" % (name, linkTag.name)] = 0.0

        if eWord == "." and eIndex != len(info['e']) - 1:
            for link in links:
                if info['f'][link[0]] != ".":
                    values["%s___%s" % (name, link.linkTag.name)] += 1.0/len(links)

        return values

    def ff_isLinkedToNullWord(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires if eWord is aligned to nothing.
        """
        if currentNode is not None:
            pos = currentNode.getPOS()
        name = self.ff_isLinkedToNullWord.func_name + '___' + pos

        if len(links) == 0:
            return {name: 1.}
        else:
            return {name: 0.}

    def ff_isPuncAndHasMoreThanOneLink(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires if eWord is punctuation and is aligned to more than
        one f token.
        """
        name = self.ff_isPuncAndHasMoreThanOneLink.func_name

        if self.isPunctuation(eWord) and len(links) > 1:
            return {name: 1.}
        else:
            return {name: 0.}

    def ff_isPuncAndHasMoreThanOneLinkTag(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires if eWord is punctuation and is aligned to more than
        one f token.
        """
        name = self.ff_isPuncAndHasMoreThanOneLinkTag.func_name

        values = defaultdict(float)

        for linkTag in LinkTag:
            values["%s___%s" % (name, linkTag.name)] = 0.0

        if self.isPunctuation(eWord) and len(links) > 1:
            for link in links:
                values["%s___%s" % (name, link.linkTag.name)] += 1.0 / len(links)

        return values

    def ff_jumpDistance(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        When eWord is aligned to two or more fWords, return size of vertical gap
        between the two links in the alignment matrix. Condition on POS.
        For example, it's probably OK for an English IN to align to align to two
        Chinese tokens spaced relatively far apart; it's probably not OK for the
        same thing to happen with an English JJ.
        We return features for distances of: 0, 1, 2, 3, >=4.
        """
        # We assume that all links passed to this function will have the same eIndex
        # Only the fIndex will vary.

        if currentNode is not None:
            pos = currentNode.getPOS()
        name = self.ff_jumpDistance.func_name + '___' + pos + '_nb'

        maxdiff = 0
        if len(links) <= 1:
            return {name: 0}

        for i, link1 in enumerate(links):
            for link2 in links[i+1:i+2]:
                diff = abs(link2[0]-link1[0])
                if diff > maxdiff:
                    maxdiff = diff

        features = defaultdict(int)
        for i in range(min(maxdiff+1, 5)):
            features[name+'_'+str(i)] = 1
        return features

    def ff_jumpDistanceTag(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        When eWord is aligned to two or more fWords, return size of vertical gap
        between the two links in the alignment matrix. Condition on POS.
        For example, it's probably OK for an English IN to align to align to two
        Chinese tokens spaced relatively far apart; it's probably not OK for the
        same thing to happen with an English JJ.
        We return features for distances of: 0, 1, 2, 3, >=4.
        """
        # We assume that all links passed to this function will have the same eIndex
        # Only the fIndex will vary.

        if currentNode is not None:
            pos = currentNode.getPOS()

        name = self.ff_jumpDistanceTag.func_name + '___' + pos
        values = defaultdict(float)

        maxdiff = 0
        if len(links) <= 1:
            return {name: 0}

        delta = 1.0 / len(links)
        for i, link1 in enumerate(links):
            for link2 in links[i+1:i+2]:
                diff = abs(link2[0]-link1[0])
                diff = min(diff, 5)
                values["%s___%d(%s:%s)___nb" % (name, diff, link1.linkTag.name, link2.linkTag.name)] += delta 

        return values


    def ff_lexprob_zero(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Fire feature when we hypothesize a link that implies a translation not
        found in our GIZA++ T-tables. This function turns out to be an interesting
        barometer for how well we can trust GIZA++ alignments. We tend to learn
        strong negative weights here for links involving eWords with POS tags
        indicative of content words (e.g. NNP, NN, JJ, NNS, VBG), and weights
        closer to zero for links involving eWords with POS tags indicative of
        function words, e.g. (TO, WP$, CC, ").
        """
        if currentNode is not None:
            pos = currentNode.getPOS()
        name = self.ff_lexprob_zero.func_name + '___' + pos + '_nb'

        # Calculate feature function value
        val = 0.0
        numLinks = len(links)
        if numLinks > 0:
            for link in links:
                fWord = info['f'][link[0]]
                eWord = info['e'][link[1]]
                val = (self.pef.get(fWord, {}).get(eWord, 0.0) +
                      self.pfe.get(eWord, {}).get(fWord, 0.0))
                if val == 0:
                    return {name: 1.0}

        return {name: 0.}

    def ff_lexprob_zeroTag(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Fire feature when we hypothesize a link that implies a translation not
        found in our GIZA++ T-tables. This function turns out to be an interesting
        barometer for how well we can trust GIZA++ alignments. We tend to learn
        strong negative weights here for links involving eWords with POS tags
        indicative of content words (e.g. NNP, NN, JJ, NNS, VBG), and weights
        closer to zero for links involving eWords with POS tags indicative of
        function words, e.g. (TO, WP$, CC, ").
        """
        if currentNode is not None:
            pos = currentNode.getPOS()

        name = self.ff_lexprob_zeroTag.func_name + '___' + pos

        features = defaultdict(float)

        # Calculate feature function value
        val = 0.0
        numLinks = len(links)
        if numLinks > 0:
            delta = 1.0/numLinks
            for link in links:
                fWord = info['f'][link[0]]
                eWord = info['e'][link[1]]
                val = (self.pef.get(fWord, {}).get(eWord, 0.0) +
                      self.pfe.get(eWord, {}).get(fWord, 0.0))
                if val == 0:
                    features["%s___%s___nb"  % (name, link.linkTag.name)] += delta

        return features

    def ff_nonPeriodLinkedToPeriod(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when non-period eWord is linked to a period.
        """
        name = self.ff_nonPeriodLinkedToPeriod.func_name

        if eWord != '.':
            fWords = [info['f'][link[0]] for link in links]
            for fword in fWords:
                if fword == '.':
                    return {name: 1.0}
        return {name: 0.0}

    def ff_nonPeriodLinkedToPeriodTag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when non-period eWord is linked to a period.
        """
        name = self.ff_nonPeriodLinkedToPeriodTag.func_name
        features = defaultdict(float)
        if len(links) == 0:
            return features

        delta = 1.0/len(links)
        if eWord != '.':
            for link in links:
                fword = info['f'][link[0]]
                if fword == '.':
                    features["%s___%s" % (name, link.linkTag.name)] += delta

        return features


    def ff_nonfinalPeriodLinkedToComma(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when non-final eWord '.' is linked to a comma.
        """
        name = self.ff_nonfinalPeriodLinkedToComma.func_name

        if eWord == '.' and eIndex is not len(info['e'])-1 and len(links) == 1 and fWord == ',':
            return {name: 1.0}
        else:
            return {name: 0.0}

    def ff_nonfinalPeriodLinkedToCommaTag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when non-final eWord '.' is linked to a comma.
        """
        name = self.ff_nonfinalPeriodLinkedToCommaTag.func_name

        if eWord == '.' and eIndex is not len(info['e'])-1 and len(links) == 1 and fWord == ',':
            return {name+'___'+links[0].linkTag.name: 1.0}
        
        return {}


    def ff_nonfinalPeriodLinkedToFinalPeriod(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when non-final eWord '.' is aligned to
        final fWord '.'
        """
        name = self.ff_nonfinalPeriodLinkedToFinalPeriod.func_name

        if eWord == '.' and eIndex is not len(info['e'])-1 and len(links) == 1 and fWord == '.' and fIndex == len(info['f'])-1:
            return {name: 1.0}
        else:
            return {name: 0.0}

    def ff_nonfinalPeriodLinkedToFinalPeriodTag(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when non-final eWord '.' is aligned to
        final fWord '.'
        """
        name = self.ff_nonfinalPeriodLinkedToFinalPeriodTag.func_name

        if eWord == '.' and eIndex is not len(info['e'])-1 and len(links) == 1 and fWord == '.' and fIndex == len(info['f'])-1:
            return {name+'___'+links[0].linkTag.name: 1.0}
        else:
            return {name: 0.0}



    def ff_quote1to1(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when double-quote is linked to double-quote.
        """
        name = self.ff_quote1to1.func_name

        if len(links) == 1 and eWord == '"' and fWord == '"':
            return {name: 1.}
        else:
            return {name: 0.}

    def ff_quote1to1Tag(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when double-quote is linked to double-quote.
        """
        name = self.ff_quote1to1Tag.func_name

        if len(links) == 1 and eWord == '"' and fWord == '"':
            return {name + '___' + links[0].linkTag.name: 1.0}

        return {}

    def ff_sameWordLinksTag(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when single eWord is linked to more than one fWord
        of the same type.
        """
        name = self.ff_sameWordLinksTag.func_name
        count = defaultdict(float)
        feature = defaultdict(float)

        if len(links) > 1:
            linkedToWords = defaultdict(int)
            for link in links:
                if count[link.linkTag.name] < 5:
                    count[link.linkTag.name] += 1               

            for link in links:
                fIndex = link[0]
                eIndex = link[1]
                fWord = info['f'][fIndex]
                eWord = info['e'][eIndex]
                linkedToWords[fWord] += 1
                if linkedToWords[fWord] > 1:
                    for linkTag in LinkTag:
                        feature["%s___%s" % (name, linkTag.name)] = count[linkTag.name]

        return {}

    def ff_sameWordLinks(self, info,  fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        feature fires when single eWord is linked to more than one fWord
        of the same type.
        """
        name = self.ff_sameWordLinks.func_name

        if len(links) > 1:
            linkedToWords = defaultdict(int)
            for link in links:
                fIndex = link[0]
                eIndex = link[1]
                fWord = info['f'][fIndex]
                eWord = info['e'][eIndex]
                linkedToWords[fWord] += 1
                if linkedToWords[fWord] > 1:
                    return {name: 1.}

        return {name: 0.}


    def ff_unalignedNonfinalPeriod(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        """
        Binary feature fires when non-final eWord '.' is unaligned.
        """
        name = self.ff_unalignedNonfinalPeriod.func_name

        if eWord == '.' and eIndex is not len(info['e'])-1 and len(links) == 0:
            return {name: 1.0}
        else:
            return {name: 0.0}

    def ff_continuousAlignment(self, info, fWord, eWord, fIndex, eIndex, links, diagValues, currentNode = None):
        name = self.ff_continuousAlignment.func_name
        links = sorted(links)
        nodes1 = None
        nodes2 = None
        total = 0.0
        for i in xrange(len(links)-1):
            count = 0.0 # the number of times two nodes are connected(meaning one node is a parent of the other node)
            findex1 = links[i][0]
            findex2 = links[i+1][0]
            if not nodes2 == None:
                nodes1 = nodes2
            else:
                nodes1  = info['ftree'].getNodesByIndex(findex1)
            nodes2  = info['ftree'].getNodesByIndex(findex2)
            for node1 in nodes1:
                for node2 in nodes2:
                    if node1.isConnectedTo(node2):
                        count += 1
            total += count / (len(nodes1)*len(nodes2))

        return {name: total}


    def pointLineGridDistance(self, f, e, fIndex, eIndex):
        """
        Compute distance to the diagonal of the alignment matrix.
        """
        elen = float(len(e))
        flen = float(len(f))

        ySize = flen
        xSize = elen
        x = eIndex
        y = fIndex

        slope = ySize/xSize
        perfectY = slope*x

        distance = perfectY - y
        # Return distance
        normalizer = max(perfectY, ySize - perfectY)
        normalizedDistance = distance/normalizer
        val = normalizedDistance

        return val

    def isPunctuation(self, string):
        """
        Return True if string is one of , . ! ? ' " ( ) : ; - @ etc
        """
        return self.punc.has_key(string)

class NonlocalFeatures:
    def __init__(self, pef, pfe, lm = None):
        self.null_token = "*NULL*"
        self.pef = pef
        self.pfe = pfe
        self.lm = lm
        self.punc = {',':True,'.':True,'!':True,'?':True,"'":True,'"':True,
                     ')':True,'(':True,':':True,';':True,'-':True,'@':True}
        # Chinese punctuation
        #self.punc[u'\u3002']=True # Chinese period
        #self.punc[u'\u201c']=True # Chinese quote
        #self.punc[u'\u201d']=True # Chinese quote
        #self.punc[u'\uff0c']=True # Chinese comma
        #self.punc[u'\u3001']=True # Chinese comma
        #self.punc[u'\uff0d']=True # Chinese dash
        #self.punc[u'\uff1f']=True # Chinese question mark

    def ff_nonlocal_dummy(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        Just a dummy feature. For debugging purposes only. Always returns a zero value.
        """
        name = self.ff_nonlocal_dummy.func_name
        return {name: 0}

    def ff_nonlocal_crossb(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        Constellation features. An extension of the constellation features
        of Liang et al. '06. These features fire for certain configuration of link
        clusters as we combine two treenode spans.
        """
        name = self.ff_nonlocal_crossb.func_name
        values = {}
        try:
            edge1 = childEdges[0]
            edge2 = childEdges[1]
            edge1_maxF = edge1.boundingBox[1][0]
            edge2_maxF = edge2.boundingBox[1][0]
            edge2_minF = edge2.boundingBox[0][0]
            edge1_minF = edge1.boundingBox[0][0]

            # Case 0: Equal bounding boxes
            # [    ] [    ]
            # [    ] [    ]
            if edge1_maxF == edge2_maxF and edge1_minF == edge2_minF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'0___'+value] = 1
            # Case 1 (monotonic)
            # [    ]
            # [    ]
            #        [    ]
            #        [    ]
            elif edge1_maxF < edge2_minF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'1___'+value] = 1
            # Case 2 (reordered)
            #        [    ]
            #        [    ]
            # [    ]
            # [    ]
            elif edge1_minF > edge2_maxF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'2___'+value] = 1
            # Case 3
            # [    ]
            # [    ] [    ]
            #        [    ]
            elif edge1_maxF >= edge2_minF and edge1_maxF < edge2_maxF and edge1_minF < edge2_minF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'3___'+value] = 1
            # Case 4
            #        [    ]
            # [    ] [    ]
            # [    ] [    ]
            # [    ]

            elif edge1_minF >= edge2_minF and edge1_minF < edge2_maxF and edge1_maxF > edge2_maxF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'4___'+value] = 1
            # Case 5 (1 shares top of 2)
            # [    ] [    ]
            #        [    ]
            elif edge1_minF == edge2_minF and edge1_maxF < edge2_maxF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'5___'+value] = 1
            # Case 6 (1 shares bot of 2)
            #        [    ]
            # [    ] [    ]
            elif edge1_maxF == edge2_maxF and edge1_minF > edge2_minF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'6___'+value] = 1
            # Case 7 (2 shares top of 1; same as 5 but diff bracketing)
            # [    ] [    ]
            # [    ]
            elif edge2_minF == edge1_minF and edge2_maxF < edge1_maxF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'7___'+value] = 1
            # Case 8 (2 shares bot of 1; same as 6 but diff bracketing)
            # [    ]
            # [    ] [    ]
            elif edge2_maxF == edge1_maxF and edge2_minF > edge1_minF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'8___'+value] = 1
            # Case 9 (1 wholly contained in 2)
            #        [    ]
            # [    ] [    ]
            #        [    ]
            elif edge1_minF > edge2_minF and edge1_maxF < edge2_maxF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'9___'+value] = 1
            # Case 10 (2 wholly contained in 1)
            # [    ]
            # [    ] [    ]
            # [    ]
            elif edge2_minF > edge1_minF and edge2_maxF < edge1_maxF:
                value = "%s(%s,%s)" %(treeNode.getPOS(),treeNode.children[0].getPOS(),treeNode.children[1].getPOS())
                values[name+'10___'+value] = 1
            # else: dump links here to find out what cases we missed, if any
        except:
            return {}
        return values

    def ff_nonlocal_horizGridDistance(self, info,  treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        A distance metric quantifying horizontal distance between two links (f, i); (f, j)
        d((f,i),(f,j)) = j - i
        Necessary for sentence pairs with no etrees.
        """
        name = self.ff_nonlocal_horizGridDistance.func_name + '_nb'

        dist = 0.0
        if len(linkedToWords) == 0:
            return {name: 0.}
        spanLength = float(srcSpan[1] - srcSpan[0])

        for fIndex in linkedToWords:
            if len(linkedToWords[fIndex]) < 2:
                continue
            else:   # fIndex is aligned to at least two different eIndices
                    # compute distance in pairs: if list = [1,2,3], compute dist(1,2), dist(2,3)
                for i, (eIndex1, _ ) in enumerate(linkedToWords[fIndex]):
                    for _, (eIndex2, _ ) in enumerate(linkedToWords[fIndex][i+1:i+2]):
                        dist += max(0.0,abs(eIndex2 - eIndex1)-1)/spanLength
        dist /= len(linkedToWords)
        return {name: dist}



    def ff_nonlocal_isPuncAndHasMoreThanOneLink(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        Binary feature fires when fWord is punctuation token and is aligned
        to more than one e token. In a good alignment, we expect this to happen
        rarely or never.
        """
        name = self.ff_nonlocal_isPuncAndHasMoreThanOneLink.func_name

        val = 0.0
        for fIndex in linkedToWords:
            fWord = info['f'][fIndex]
            if self.isPunctuation(fWord) and len(linkedToWords[fIndex]) > 1:
                val += 1.0
        return {name: val}


    def ff_nonlocal_tgtTag_srcTag(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        Fire Source-target coordination features.
        From (Riesa et al., 2011) Section 3.2.1.
        """
        name = self.ff_nonlocal_tgtTag_srcTag.func_name

        if info['ftree'] is None:
            return {}
        if len(info['ftree'].terminals) == 0:
            return {}

        tgtTag = treeNode.getPOS()
        srcTag = ""
        # Account for the null alignment case
        if len(links) == 0:
            value = "%s:%s" % (tgtTag, self.null_token)
            return {name+'___'+value: 1}

        minF = edge.boundingBox[0][0]
        maxF = edge.boundingBox[1][0]
        eWord = treeNode.data['surface']
        eStartSpan, eEndSpan = treeNode.get_span()
        eSpanLen = float(eEndSpan - eStartSpan)

        fspan = (minF, maxF)
        sourceNode = info['ftree'].getDeepestNodeConveringSpan(fspan)
        fWord = sourceNode.data['surface']
        fStartSpan, fEndSpan = sourceNode.get_span()
        fSpanLen = float(fEndSpan - fStartSpan)
        srcTag = sourceNode.getPOS()
        value1 = '%s:%s' % (tgtTag, srcTag)
        normalized_span_diff = abs(eSpanLen/len(info['e']) - fSpanLen/len(info['f']))
        features =  {name+'___'+value1: 1, name+'__'+'normalizedSpanLenDiff': normalized_span_diff, name+'__'+'pfe' : self.pef.get(fWord, {}).get(eWord, 0.0) }
        if minF < maxF:
            pos_count = defaultdict(int)
            for node1 in info['ftree'].data['nodeTable'][minF]:
                for node2 in info['ftree'].data['nodeTable'][maxF]:
                    pos_count[(node1.getPOS(), node2.getPOS())] += 1
            for key in pos_count.keys():
                pos_count[key] /= float(len(info['ftree'].data['nodeTable'][minF])*len(info['ftree'].data['nodeTable'][maxF]))
                leftFTag = key[0]
                rightFTag = key[1]
                features[name+'___'+'%s:%s(%s,%s)' % (tgtTag, srcTag, leftFTag, rightFTag)] = pos_count[key]
        return features

    def ff_nonlocal_sameWordLinks(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        Fire feature when fWord linked to more than one eWord of the same type.
        """
        name = self.ff_nonlocal_sameWordLinks.func_name

        penalty = 0.0
        if len(links) > 1:
            for fIndex in linkedToWords:
                if len(linkedToWords[fIndex]) < 2:
                    continue
                eWords = defaultdict(int)
                for (eIndex, _) in linkedToWords[fIndex]:
                    eWord = info['e'][eIndex]
                    eWords[eWord] += 1
                penalty += sum([count-1 for count in eWords.values()])
                # Normalize
                penalty /= (tgtSpan[1] - tgtSpan[0] + 1)
        return {name: penalty}

    def ff_nonlocal_stringDistance(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        dist = defaultdict(float)

        linkedToWords_copy = dict(linkedToWords)
        if tgtSpan is None:
            return {}
        tgtSpanDist = tgtSpan[1] - tgtSpan[0]
        if tgtSpanDist == 0:
            return {}

        # normalizer = 0.0
        for fIndex in linkedToWords_copy:
            if len(linkedToWords_copy[fIndex]) < 2:
                continue
            else:
                # fIndex is aligned to at least two different eIndices
                # compute distance in pairs: if list = [1,2,3], compute dist(1,2), dist(2,3)
                # if list has length n, we will have n-1 distance computations
                nodes =  info['ftree'].getNodesByIndex(fIndex)
                pos_count = defaultdict(float)
                for node in nodes:
                    pos_count[node.getPOS()] += 1.0/len(nodes)

                linkedToWords_copy[fIndex].sort()
                listlength = len(linkedToWords_copy[fIndex])
                # normalizer += listlength - 1
                for i in xrange(listlength-1):
                    # eIndex1 and eIndex2 will always be the smallest, and second-smallest indices, respectively.
                    eIndex1, _ = linkedToWords_copy[fIndex][0]
                    eIndex2, _ = linkedToWords_copy[fIndex][1]
                    linkedToWords_copy[fIndex] = linkedToWords_copy[fIndex][1:]
                    assert eIndex2 > eIndex1
                    for pos, count in pos_count.iteritems():
                        dist[pos] += (eIndex2 - eIndex1 - 1)*count
        features = {}
        for pos in dist:
            try:
                dist[pos] /= tgtSpanDist
            except:
                dist[pos] = 0.0
            features[self.ff_nonlocal_stringDistance.func_name+'___'+pos+'_nb'] = dist[pos]
        return features

    def ff_nonlocal_treeDistance(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        A distance metric quantifying "tree distance" between two links (f, i); (f, j)
        """
        name = self.ff_nonlocal_treeDistance.func_name + '_nb'
        dist = 0.0
        linkedToWords_copy = dict(linkedToWords)
        if tgtSpan is None:
            return {name: 0.}
        tgtSpanDist = tgtSpan[1] - tgtSpan[0]
        if tgtSpanDist == 0:
            return {name: 0.}

        normalizer = 0.0
        for fIndex in linkedToWords_copy:
            if len(linkedToWords_copy[fIndex]) < 2:
                continue
            else:   # fIndex is aligned to at least two different eIndices
                        # compute distance in pairs: if list = [1,2,3], compute dist(1,2), dist(2,3)
                        # if list has length n, we will have n-1 distance computations

                linkedToWords_copy[fIndex].sort()
                listlength = len(linkedToWords_copy[fIndex])
                normalizer += listlength - 1
                for i in xrange(listlength-1):
                    # eIndex1 and eIndex2 will always be the smallest, and second-smallest indices, respectively.
                    eIndex1, depth1 = linkedToWords_copy[fIndex][0]
                    eIndex2, depth2 = linkedToWords_copy[fIndex][1]
                    linkedToWords_copy[fIndex] = linkedToWords_copy[fIndex][1:]
                    dist += depth1 + depth2
        try:
            # dist /= tgtSpanDist
            dist /= normalizer
        except:
            dist = 0.0
        return {name: dist}

    def isPunctuation(self, string):
        """
        Return True if string is one of  , . ! ? ' " ( ) : ; - @ etc.
        """
        return self.punc.has_key(string)

    def ff_nonlocal_hyperEdgeScore(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        Return hyperedge score
        """
        name = self.ff_nonlocal_hyperEdgeScore.func_name
        return {name: edge.hyperEdgeScore}

    def ff_nonlocal_dependencyTreeLM(self, info, treeNode, edge, links, srcSpan, tgtSpan, linkedToWords, childEdges, diagValues, treeDistValues):
        """
        Return dependency tree language model score for a partial alignment
        """
        name = self.ff_nonlocal_dependencyTreeLM.func_name

        if self.lm is None:
            return {}
        edge.decodingPath.calcScore(self.lm)
        return {name: edge.decodingPath.lmScore}
