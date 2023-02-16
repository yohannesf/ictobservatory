from django.shortcuts import render, redirect

from django.contrib import messages


def manageprofile(request):

    user = request.user
    context = {'user': user}

    if request.method == 'POST':
        first_name = request.POST['firstname']

        last_name = request.POST['lastname']
        phone = request.POST['phone']
        #email = request.POST['email']

        # Check Unique Email

        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        #user.email = email
        user.save()

    return render(request, 'portaldata/profile.html', context=context)
