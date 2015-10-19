class AlignmentLink:
    def __init__(self, link):
        self.depth = 0
        self.link = link

    def __getitem__(self, index):
        return self.link[index]
