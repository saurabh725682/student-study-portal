from . forms import UserCreationForm, UserRegistrationForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import auth

# Create your views here.

#View function for register..
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserCreationForm()
    context = {'form': form}  
    return render(request, 'navbar/register.html', context)


# View function for login..
def login(request):  
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth.login(request, user)                
                return redirect('home')   
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid form data')    
        context = {'form': form}
        return render(request, 'navbar/login.html', context)
    else:
    # If the request method is not 'POST', return the form
        form = LoginForm() 
    context = {'form': form}
    return render(request, 'navbar/login.html', context)


# View function for logout..
def logout(request):
    auth.logout(request)  
    messages.success(request, "You are logged out!")
    return redirect('login')
    

 