# hitochan777@gmail.com (Otsuki Hitoshi)

def default(partialAlignment):
    return partialAlignment.score

def hope(partialAlignment):
    return partialAlignment.fscore + partialAlignment.score    

def fear(partialAlignment):
    return (1 - partialAlignment.fscore) + partialAlignment.score
        

