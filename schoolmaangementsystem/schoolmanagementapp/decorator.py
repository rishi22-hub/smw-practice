from django.http import HttpResponse
from django.shortcuts import render,redirect

def principal_allowed(function):    
    def wrapper_func(request,*args,**kwargs):
        if request.user.role == "principal":
            return function(request,*args,**kwargs)
        
        else:
            return HttpResponse("You are Not authorized to view the page!!!")
    return wrapper_func
    
def teacher_allowed(function):    
    def wrapper_func(request,*args,**kwargs):
        if request.user.role == "principal" or request.user.role=='teacher':
            return function(request,*args,**kwargs)
        
        else:
            return HttpResponse("You are Not authorized to view the page!!!")
    return wrapper_func



def student_allowed(function):    
    def wrapper_func(request,*args,**kwargs):
        if request.user.role == "principal" or request.user.role=='teacher' or request.user.role=='student':
            return function(request,*args,**kwargs)
        
        else:
            return HttpResponse("You are Not authorized to view the page!!!")
    return wrapper_func