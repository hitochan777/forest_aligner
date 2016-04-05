from LinkTag import LinkTag

class AlignmentLink:

    def __init__(self, link, linkTag = LinkTag.sure, depth=0):
        self.depth = depth
        self.link = link
        assert isinstance(linkTag, LinkTag)
        self.linkTag = linkTag

    def __getitem__(self, index):
        return self.link[index]

    def __str__(self):
        return "%s, %s, %d" % (str(self.link), self.linkTag.name, self.depth)

    def __repr__(self):
        return "%s, %s, %d" % (str(self.link), self.linkTag.name, self.depth)
