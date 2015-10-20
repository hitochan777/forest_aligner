class AlignmentLink:
    def __init__(self, link, depth=0):
        self.depth = depth
        self.link = link

    def __getitem__(self, index):
        return self.link[index]

    def __str__(self):
        return "%s, %d" % (str(self.link), self.depth)
