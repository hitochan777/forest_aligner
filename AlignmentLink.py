class AlignmentLink:
    def __init__(self, link, origin, depth=0):
        self.depth = depth
        self.link = link
        self.origin = origin

    def __getitem__(self, index):
        return self.link[index]

    def __str__(self):
        return "%s, %d" % (str(self.link), self.depth)
