#Some helpful functions

def getVal(val, default = '', obj = None):
    if obj and obj.has_key(val):
        return obj[val]
    return default
