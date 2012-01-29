from random import choice, randint

def random_string(charlist=None, start=2, end=6):
    if not charlist:
        charlist = [u'bcdfgklmnprstxz', u'aejioqvuwy']
    return ''.join(map(choice, (charlist * randint(start, end))))

