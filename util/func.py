def person_num(i,b):
    if b:
        return len(b.split(','))
    else:
        return 0

def split(cls, i):
    if i:
        return i.split(',')
    else:
        return ''