from .decorator import principal_allowed,teacher_allowed,student_allowed
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login,logout
from .forms import *
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes,force_str
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from .models import Principal,Student,Teacher,UserCredentials
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from functools import reduce
from operator import or_
from django.http import HttpResponse

def home_redirect(request):
    print(request.user)
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        path=str(request.user.role)+"_dashboard"
        print(path)
        return redirect(path)
    else:
        return redirect('login')
    

def user_login(request):
    print(request.method)
    if request.method == 'POST':
        form = LoginForm(request.POST or None)
        print(form.errors)
        if form.is_valid():
            print("form valid",form.cleaned_data['email'],form.cleaned_data['password'])
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            print(user)
            if user:
                login(request, user)
                if request.user.role == 'principal':
                    return redirect('principal_dashboard')
                elif request.user.role == 'teacher':
                    return redirect('teacher_dashboard')
                elif request.user.role == 'student':
                    return redirect('student_dashboard')
                else:
                    return HttpResponse("Not any valid role assigned to you contact admin")
            else:
                messages.error(request,"User is not authenticated!!")
    else:
        form = LoginForm()
    return render(request, 'user_login.html', {'form': form})


@login_required(login_url="../login/")
def user_logout(request):
    logout(request)
    return redirect('login')

def forgot_pass(request):
    form=ForgotPasswordForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = request.POST.get('email')
            user = UserCredentials.objects.filter(email=email).first()
            print(user)
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(reverse('password_reset', args=[uid, token]))
                print(reset_url)
                message = render_to_string('send_email.html', {'reset_url': reset_url})
                print("sending email")
                messages.success(request,"Email sent succesfully")
                send_mail(
                    'Password Reset Request',
                    "nothing just reset password",
                    'ppppppppp1234pp@gmail.com',
                    [email],
                    fail_silently=False,
                    html_message=message
                )
            
            return redirect('forgot_password')

    return render(request,'forgot_password.html',{'form':form})


def password_reset(request,uidb64=None,token=None):
    form=ResetPasswordForm(request.POST or None)
    user=None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserCredentials.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserCredentials.DoesNotExist):
        user = None
    print(user)
    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            print(new_password)
            print(confirm_password)
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request,"password Reset successfully!!")
                return redirect('login')

    return render(request, 'reset_password.html',{'form':form})



@login_required(login_url='../login/')
def change_pass(request,id):
    form=ChangePasswordForm(request.POST or None)
    if request.method=='POST':
        password=request.POST.get('new_password')
        user=UserCredentials.objects.get(id=id)
        if form.is_valid():
            user.set_password(password)
            path=str(request.user.role)+"_dashboard"
            print(path)
            return redirect(path)
    
    
    return render(request,"change_password.html",{'form':form})



@login_required(login_url='../login/')
@principal_allowed
def principal_dashboard(request):
    context={}
    return render(request,'dashboard_principal.html',context=context)

@login_required(login_url='../login/')
@teacher_allowed
def teacher_dashboard(request):
    return render(request,'dashboard_teacher.html')

@login_required(login_url='../login/')
@student_allowed
def student_dashboard(request):
    return render(request,'dashboard_student.html')

@login_required(login_url='../login/')
@principal_allowed
def student_list(request):
    return render(request,'student_list.html')

@login_required(login_url='../login/')
@principal_allowed
def student_list_json(request):
    print(request.method)
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]')
    order_column_index = int(request.GET.get('order[0][column]',default=-1))
    order_direction = request.GET.get('order[0][dir]')
    if search_value is None:
        search_value=""
    search_value = search_value.strip()
    search_value =search_value.lower()
    column_names=['first_name','last_name','email','date_joined']
    q_obj=reduce(or_ , (Q(**{i + '__icontains': search_value}) for i in column_names))
    data=Student.objects.filter(q_obj)
    print(data)
    total_records = data.count()
    filtered_records = data.count()
    records = []
    if order_column_index != -1:
        sort_field=column_names[order_column_index]     
        if order_direction == 'asc':
            data = data.order_by(sort_field)
        else:
            data = data.order_by(f'-{sort_field}')
    for item in data[start:start+length]:
        records.append({
              "first_name" :item.first_name,
            "last_name":item.last_name,
             "email" : item.email,
            "date_joined":item.date_joined,
            "id":item.id
       })
    response = {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": records,
    }
    return JsonResponse(response)
   
    







@principal_allowed
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_teachers')  
    else:
        form = TeacherForm()
    return render(request, 'add_teacher.html', {'form': form})


@teacher_allowed
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_students')  
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})


@principal_allowed
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_subjects')
    else:
        form = SubjectForm()
    return render(request, 'add_subject.html', {'form': form})



@principal_allowed
def add_classroom(request):
    form=ClassRoomForm()
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_classrooms') 
   
    return render(request, 'add_classroom.html', {'form': form})




@teacher_allowed
def subject_list(request):
    return render(request,'subject_list.html')


@principal_allowed
def subject_list_json(request):
    print(request.method)
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]')
    order_column_index = int(request.GET.get('order[0][column]',default=-1))
    order_direction = request.GET.get('order[0][dir]')
    if search_value is None:
        search_value=""
    search_value = search_value.strip()
    search_value =search_value.lower()
    column_names=['name','description']
    q_obj=reduce(or_ , (Q(**{i + '__icontains': search_value}) for i in column_names))
    data=Subject.objects.filter(q_obj)
    total_records = data.count()
    filtered_records = data.count()
    records = []
    if order_column_index != -1:
        sort_field=column_names[order_column_index]     
        if order_direction == 'asc':
            data = data.order_by(sort_field)
        else:
            data = data.order_by(f'-{sort_field}')
    for item in data[start:start+length]:
        records.append({
            "name" :item.name,
            "description":item.description,             
            "id":item.id
       })
    response = {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": records,
    }
    return JsonResponse(response)





@teacher_allowed
def teacher_list(request):
    return render(request,'teacher_list.html')

@principal_allowed
def teacher_list_json(request):
    print(request.method)
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]')
    order_column_index = int(request.GET.get('order[0][column]',default=-1))
    order_direction = request.GET.get('order[0][dir]')
    if search_value is None:
        search_value=""
    search_value = search_value.strip()
    search_value =search_value.lower()
    column_names=['first_name','last_name',"date_joined",'email']
    q_obj=reduce(or_ , (Q(**{i + '__icontains': search_value}) for i in column_names))
    data=Teacher.objects.filter(q_obj)
    total_records = data.count()
    filtered_records = data.count()
    records = []
    if order_column_index != -1:
        sort_field=column_names[order_column_index]     
        if order_direction == 'asc':
            data = data.order_by(sort_field)
        else:
            data = data.order_by(f'-{sort_field}')
    for item in data[start:start+length]:
        subject_names = [subject.name for subject in item.subjects.all()]
        joined_subject_names = ', '.join(subject_names)
        records.append({
            "first_name" :item.first_name,
             "last_name" :item.last_name,
             "date_joined" :item.date_joined,
            "email":item.email,
            "subjects":joined_subject_names,            
            "id":item.id
       })
    response = {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": records,
    }
    return JsonResponse(response)

@teacher_allowed
def delete_student(request,id):
    print("inside_delete")
    student= Student.objects.get(id=id)
    student.delete()
    return redirect("list_students")

@principal_allowed
def delete_teacher(request,id):
    print("inside_delete")
    teacher= Teacher.objects.get(id=id)
    teacher.delete()
    return redirect("list_teachers")

@principal_allowed
def delete_subject(request,id):
    print("inside_delete")
    subject= Subject.objects.get(id=id)
    subject.delete()
    return redirect("list_subjects")

@teacher_allowed
def edit_student(request,id):
    student=Student.objects.get(id=id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('list_students')
    else:
        form = StudentForm(instance=student)
    return render(request, 'add_student.html', {'form': form})



@principal_allowed
def edit_teacher(request,id):
    teacher=Teacher.objects.get(id=id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request,"teachers data edited successfully!!")
            return redirect('list_teachers')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'add_teacher.html', {'form': form})


@teacher_allowed
def edit_subject(request,id):
    subject=Subject.objects.get(id=id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('list_subjects')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'add_subject.html', {'form': form})


@principal_allowed
def classroom_list(request):
    return render(request,'classroom_list.html')

@principal_allowed
def classroom_list_json(request):
    print(request.method)
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]')
    order_column_index = int(request.GET.get('order[0][column]',default=-1))
    order_direction = request.GET.get('order[0][dir]')
    if search_value is None:
        search_value=""
    search_value = search_value.strip()
    search_value =search_value.lower()
    column_names=['name','grade']
    q_obj=reduce(or_ , (Q(**{i + '__icontains': search_value}) for i in column_names))
    data=ClassRoom.objects.filter(q_obj)
    total_records = data.count()
    filtered_records = data.count()
    records = []
    if order_column_index != -1:
        sort_field=column_names[order_column_index]     
        if order_direction == 'asc':
            data = data.order_by(sort_field)
        else:
            data = data.order_by(f'-{sort_field}')
    for item in data[start:start+length]:
        # teacher_names = [teacher.first_name+teacher.last_name for teacher in item.teacher.all()]
        # joined_teacher_names = ', '.join(teacher_names)
        teacher=item.teacher.first_name+item.teacher.last_name
        print(teacher)
        print(item.teacher.first_name)
        records.append({
            "name" :item.name,
            "grade":item.grade,
            "teacher":teacher,  
            "id":item.id           
            
       })
    response = {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": records,
    }
    return JsonResponse(response)