from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from . models import *
from . forms import NotesForm, HomeworkForm, DashboardForm, TodoForm, ConversionForm, ConversionLengthForm, ConversionMassForm
from django.views import generic
from youtubesearchpython import VideosSearch
from django.contrib.auth.decorators import login_required
import requests
import wikipedia as wiki


# Create your views here.

def home(request):   
    return render(request, 'navbar/home.html')
    

#                                    ------------------------NOTES-------------------------
# View function for Notes
@login_required
def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
        messages.success(request, f'Notes added from {request.user.username} successfully.')
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)


# View functioin for delete Note..
@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    messages.success(request, 'Note has been deleted.')
    return redirect('notes')


# View function for Note details..
class NotesDetailView(generic.DetailView):
    model = Notes
    
    
#                               ------------------HOMEWORKS-------------------
# View function for homework.
@login_required
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = form.cleaned_data['is_finished']
            except KeyError:
                finished = False

            homeworks = Homework(
                user=request.user,
                subject=form.cleaned_data['subject'],
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                due=form.cleaned_data['due'],
                is_finished=finished
            )
            homeworks.save()
            messages.success(request, f'Homework added from {request.user}')
        else:
            messages.error(request, 'Invalid form data')
    else:
        form = HomeworkForm()

    homeworks = Homework.objects.filter(user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False

    context = {
        'homeworks': homeworks,
        'form': form,
        'homework_done': homework_done
    }
    return render(request, 'dashboard/homework.html', context)

# View function for updating homework.
@login_required
def update_homework(request, pk=None):
    try:
        homeworks = Homework.objects.get(id=pk)
    except Homework.DoesNotExist:
        messages.error(request, 'Homework not found')
        return redirect(reverse('homework'))

    if homeworks.is_finished:
        homeworks.is_finished = False
    else:
        homeworks.is_finished = True
    homeworks.save()
    return redirect('homework')

# View function for deleting homework.
@login_required
def delete_homework(request, pk=None):   
    homework = Homework.objects.get(id=pk).delete()   
    return redirect('homework')
    

#                            -----------------YOUTUBE--------------------
# View function for youtube.
def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text, limit=10)
        result_list = []
        
        for i in video.result()['result']:
            result_dict = {
                'input':     text,
                'title':     i['title'],
                'duration':  i['duration'],
                'thumbnail': i['thumbnails'][0]['url'],
                'channel':   i['channel']['name'],
                'link':      i['link'],
                'views':     i['viewCount']['short'],
                'published': i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            
            context = {'form': form,
                       'results': result_list,
                       }
        return render(request, 'dashboard/youtube.html', context)
    else:
        form = DashboardForm()
    context = {'form': form,}   
    return render(request, 'dashboard/youtube.html', context)


#                                 -------------------TODO---------------------
# View function for todo..
@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                title = form.cleaned_data['title']
                if not title:
                    messages.error(request, 'Title cannot be empty')
                    return redirect('todo')
                try:
                    finished = request.POST['is_finished']
                    if finished == 'on':
                        finished = True
                    else:
                        finished = False
                except:
                    finished = False
                todos = Todo(
                    user=request.user,
                    title=title,
                    is_finished=finished
                )
                todos.save()
                messages.success(request, f'Todo Added from {request.user}!')
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Invalid form data')
    else:
        form = TodoForm()
    todos = Todo.objects.filter(user=request.user)
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'todos': todos,
        'form': form,
        'todos_done': todos_done,
    }
    return render(request, 'dashboard/todo.html', context)

# View function for update todo..
@login_required
def update_todo(request, pk=None):
    try:
        todos = Todo.objects.get(id=pk)
        if todos.is_finished == True:
            todos.is_finished = False
        else:
            todos.is_finished = True
        todos.save()
        messages.success(request, 'Todo updated successfully')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('todo')


# View function for delete todo..
@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()     
    return redirect('todo')


#                                 -------------------BOOKS---------------------
# View function for books.
def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        
        if 'items' in answer:
            for i in range(len(answer['items'])):
                result_dict = {
                    'title':       answer['items'][i]['volumeInfo'].get('title'),
                    'subtitle':    answer['items'][i]['volumeInfo'].get('subtitle'),
                    'description': answer['items'][i]['volumeInfo'].get('description'),
                    'count':       answer['items'][i]['volumeInfo'].get('pageCount'),
                    'categories':  answer['items'][i]['volumeInfo'].get('categories'),
                    'rating':      answer['items'][i]['volumeInfo'].get('averageRating'),
                    'thumbnail':   answer['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail'),
                    'preview':     answer['items'][i]['volumeInfo'].get('previewLink')
                }
                result_list.append(result_dict)
        else:
            result_list = []  # or some other default value
        
        context = {'form': form, 'results': result_list,}
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
    context = {'form': form,}   
    return render(request, 'dashboard/books.html', context)


#                              -------------------DICTIONARY---------------------
# View function for dictionary.
def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics =  answer[0]['phonetics'][0]['text']
            audio =      answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example =    answer[0]['meanings'][0]['definitions'][0].get('example', '')
            synonyms =   answer[0]['meanings'][0]['definitions'][0]['synonyms']           
            context ={
                'form':       form,
                'input':      text,
                'phonetics':  phonetics,
                'audio':      audio,
                'definition': definition,
                'example':    example,
                'synonyms':   synonyms
            }
        except:
            context = {'form': form, 
                       'input': '' }
        return render(request, 'dashboard/dictionary.html', context)
    else:
       form = DashboardForm()
    context = {'form': form}
    return render(request, 'dashboard/dictionary.html', context)

 
#                              -------------------WIKIPEDIA---------------------    
# View function for wikipedia.
def wikipedia(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        try:
            search = wiki.page(text)
            context = {
                'form': form,
                'title': search.title,
                'link': search.url,
                'details': search.summary
            }
        except wiki.exceptions.DisambiguationError as e:
            
            context = {
                'form': form,
                'error': 'Multiple pages found. Please search another topic!',                
                }
        except wiki.exceptions.PageError:
            context = {
                'form': form,
                'error': 'Page not found.'
            }
        return render(request, 'dashboard/wikipedia.html', context)
    else:
        form = DashboardForm()
        context = {'form': form}
    return render(request, 'dashboard/wikipedia.html', context)


#                            ---------------------CONVERSION-----------------------
# View function for conversion.
def conversion(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        if form.is_valid():
            measurement = request.POST.get('measurement')
            if measurement:
                if measurement == 'length':
                    measurement_form = ConversionLengthForm()
                    context = {
                        'form': form,
                        'm_form': measurement_form,
                        'input': True
                    }
                    if 'input' in request.POST:
                        first = request.POST.get('measure1')
                        second = request.POST.get('measure2')
                        input = request.POST.get('input')
                        answer = ''
                        if input and float(input) >= 0:
                            if first == 'yard' and second == 'foot':
                                answer = f'{input} yard = {float(input)*3} foot'
                            elif first == 'foot' and second == 'yard':
                                answer = f'{input} foot = {float(input)/3} yard'
                        context = {
                            'form': form,
                            'm_form': measurement_form,
                            'input': True,
                            'answer': answer
                        }
                elif measurement == 'mass':
                    measurement_form = ConversionMassForm()
                    context = {
                        'form': form,
                        'm_form': measurement_form,
                        'input': True
                    }
                    if 'input' in request.POST:
                        first = request.POST.get('measure1')
                        second = request.POST.get('measure2')
                        input = request.POST.get('input')
                        answer = ''
                        if input and float(input) >= 0:
                            if first == 'pound' and second == 'kilogram':
                                answer = f'{input} pound = {float(input)*0.4535} kilogram'
                            elif first == 'kilogram' and second == 'pound':
                                answer = f'{input} kilogram = {float(input)/2.20462} pound'
                        context = {
                            'form': form,
                            'm_form': measurement_form,
                            'input': True,
                            'answer': answer
                        }
                return render(request, 'dashboard/conversion.html', context)
    else:
        form = ConversionForm()
    context = {'form': form, 'input': False}
    return render(request, 'dashboard/conversion.html', context)


# View function for profile..
@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done
    }
    return render(request, 'navbar/profile.html', context)

 






















