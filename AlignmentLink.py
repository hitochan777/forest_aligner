import enum

class AlignmentLink:
    LINK_TAG = enum.Enum("LinkTag","possible sure")

    def __init__(self, link, linkTag = LINK_TAG.sure, depth=0):
        self.depth = depth
        self.link = link
        self.linkTag = linkTag

    def __getitem__(self, index):
        return self.link[index]

    def __str__(self):
        return "%s, %d" % (str(self.link), self.depth)
