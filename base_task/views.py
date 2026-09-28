from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import ProjectForm, TaskForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q


def user_register(request):
    page = 'register'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, 'Ju sapo u regjistruat me sukses!')
            return redirect('home')
        else:
            messages.error(request, 'Ju lutem plotësoni saktë kushtet.')
    else:
        form = UserCreationForm()
    
    return render(request, 'user_register.html', {'page':page, 'form':form})

def user_login(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            messages.success(request, 'Ju sapo u kyqet me sukses!')
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Ju lutem kontrolloni username ose password!')

    return render(request, 'user_register.html', {'page':page})

def user_logout(request):
    logout(request)
    messages.success(request, 'Ju sapo u qkyet nga sistemi!')
    return redirect('home')

@login_required(login_url='login')
def dashboard(request):
    projects = Project.objects.filter(owner=request.user)
    return render(request, 'dashboard.html', {'projects':projects})

@login_required(login_url='login')
def create_project(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        return redirect('home')

    return render(request, 'create_project.html', {'form':form})

@login_required(login_url='login')
def update_project(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        form.save()
        return redirect('home')

    return render(request, 'create_project.html', {'form':form, 'project':project})

@login_required(login_url='login')
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == 'POST':
        project.delete()
        return redirect('home')

    return render(request, 'delete_project.html', {'project':project})
    
@login_required(login_url='login')
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    
    tasks_list = project.tasks.all()

    search_query = request.GET.get('search', '')
    if search_query:
        tasks_list = tasks_list.filter(title__icontains=search_query)

    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    if status_filter:
        tasks_list = tasks_list.filter(status=status_filter)
    if priority_filter:
        tasks_list = tasks_list.filter(priority=priority_filter)

    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['due_date', '-due_date', 'priority', '-priority', '-created_at']:
        tasks_list = tasks_list.order_by(sort_by)

    paginator = Paginator(tasks_list, 5)
    page_number = request.GET.get('page')
    tasks = paginator.get_page(page_number)   

    context = {
        'project': project,
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by,
    }

    return render(request, 'project_detail.html', context)

@login_required(login_url='login')
def create_task(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    form = TaskForm(request.POST or None)

    if form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.save()
        messages.success(request, 'Ju sapo krijuar nje post te ri!')
        return redirect('project_detail', pk=project.id)

    return render(request, 'create_task.html', {'form':form, 'project':project})

@login_required(login_url='login')
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    form = TaskForm(request.POST or None, instance=task)

    if form.is_valid():
        form.save()
        messages.success(request, 'Ju sapo perditesuar nje post te ri!')
        return redirect('project_detail', pk=task.project.id)

    return render(request, 'create_task.html', {'form':form, 'task':task, 'project':task.project})

@login_required(login_url='login')
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    project_id = task.project.id

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Ju sapo fshit nje post te ri!')
        return redirect('project_detail', pk=project_id)

    return render(request, 'delete_task.html', {'task':task, 'project_id':project_id})

    