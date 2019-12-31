from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def homepage(request, testmode):
	return render(request, 'index.html', locals())
	# return HttpResponse('Hello world!:{}'.format(testmode))


def about(request, author_no = 0):
	html = "<h2>Here is Author:{}'s about page!</h2><hr>".format(author_no)
	return HttpResponse(html)	


def listing(request, yr, mon, day):
    html = "<h2>List Date is {}/{}/{}</h2><hr>".format(yr, mon, day)
    return HttpResponse(html)


def post(request, yr, mon, day, post_num):
    html = "<h2>{}/{}/{}:Post Number:{}</h2><hr>".format(yr, mon, day, post_num)
    return HttpResponse(html)


def postNum2(request, yr):
    html = "<h2>{}:Post Number:Hello</h2><hr>".format(yr)
    return HttpResponse(html)
