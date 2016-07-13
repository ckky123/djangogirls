from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'cts0/index.html')

def add(request):
    a = request.GET['from']
    b = request.GET['to']
    c = a+b
    return HttpResponse(str(c))
    #return HttpResponse("aaaaaaa")
    
#def index(request):
#    return HttpResponse(u"欢迎光临 自强学堂!")