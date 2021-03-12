from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
# from .forms import CreateTaskForm
from .models import Task
from django.contrib.auth.decorators import login_required

# drf imports
from rest_framework import viewsets
from .serializers import TaskSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from django.shortcuts import get_object_or_404


def index(request):
    return render(request, 'index.html')


def tasks_list(request):
    tasks = Task.objects.all()
    return render(request, 'task/tasks_list.html', {'tasks': tasks})


@login_required
def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        start_date = request.POST.get('start_date')
        task = Task(title=title, text=text, user=request.user, start_date=start_date) 
        task.save()
        return HttpResponseRedirect(reverse('tasks:tasks_list'))
    else:
        return render(request, template_name='task/create_task.html')


@login_required
def update_task(request, pk):
    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        start_date = request.POST.get('start_date')
        # task = Task(title=title, text=text, user=request.user, start_date=start_date) 
        # task.save()
        task = Task.objects.get(pk=pk)
        task.title = title
        task.text = text
        task.start_date = start_date
        task.save()
        # Task.objects.filter(pk=pk).update(title=title, text=text, user=request.user, start_date=start_date)
        
        return HttpResponseRedirect(reverse('tasks:tasks_list'))
    else:
        task = Task.objects.get(pk=pk)
        task_dict = {
            'title': task.title,
            'text': task.text,
        }
        return render(request, template_name='task/create_task.html', context=task_dict)



@login_required
def delete_task(request, pk):
    task = Task.objects.get(pk=pk)
    task.delete()
    return HttpResponseRedirect(reverse('tasks:tasks_list'))





class TaskViewSet(viewsets.ViewSet):

    def list(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks,many=True)
        return Response(serializer.data)
        
    def create(self, request):
        serializer = TaskSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = Task.objects.all()
        task = get_object_or_404(queryset, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = Task.objects.all()
        task = get_object_or_404(queryset, pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = Task.objects.all()
        task = get_object_or_404(queryset, pk=pk)
        task.delete()



