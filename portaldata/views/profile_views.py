from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def manageprofile(request):
    '''Show User's Profile on the Profile page'''

    user = request.user
    context = {'user': user}

    if request.method == 'POST':
        first_name = request.POST['firstname']

        last_name = request.POST['lastname']
        phone = request.POST['phone']

        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone

        user.save()

    return render(request, 'portaldata/profile.html', context=context)
