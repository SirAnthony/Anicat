#Some helpful functions

def last_record_pk(model):
    try:
        return model.objects.values_list('pk').latest('pk')[0]
    except:
        return 0
