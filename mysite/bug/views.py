from django.shortcuts import render
from bug.models import Bug

# Create your views here.

def bug_manage(request):
    user = request.session.get('user','')
    bugs = Bug.objects.all()
    return render(request, 'bug_manage.html', locals())

