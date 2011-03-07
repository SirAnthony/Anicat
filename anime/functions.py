#Some helpful functions

def getVal(val, obj = None, default = ''):
    if obj and obj.has_key(val):
        return obj[val]
    return default

def getAttr(obj, val, default = ''):
    try:
        return getattr(obj, val)
    except AttributeError:
        return default
