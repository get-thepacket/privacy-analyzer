from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from .forms import policy


def index(request):

    if request.method == 'POST':

        # process form data
        form = policy(request.POST)
        if form.is_valid():
            policy_text = form.cleaned_data['policy_text']
            print(policy_text)

    return render(request,'index.html', {'form': policy()})
