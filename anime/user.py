
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

def login(request):
    response = {}
    form = None
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already logged in.'
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            response.update({'response': True, 'text': {'name': user.username}})
    response['form'] = form or AuthenticationForm()
    return response
    
