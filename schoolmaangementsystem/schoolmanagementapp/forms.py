from django import forms
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Student,Subject,Teacher,ClassRoom,Principal,UserCredentials

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your Email'}),
        label='Email',
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your Password'}),
        label='Password',
        required=True
        )
    def clean_email(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        try:
            validate_email(email)
            return email
        except:
            raise forms.ValidationError("enter valid email id")
        


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        label='Email',
        required=True
    )
    def clean_email(self):
        email = self.cleaned_data.get('email')
        print(email)
        if not UserCredentials.objects.filter(email=email).exists():
            print("not wdkjjsd")
            raise ValidationError("User with this email doesn't exist.")
        return email
    


class ChangePasswordForm(forms.Form):
    old_password=forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Old Password'}),
        label='Password',
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        label='Password',
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        label='Password',
        required=True
    )

    def clean(self):
        old_pass = self.cleaned_data.get('old_password')
        new_pass=self.cleaned_data.get('new_password')
        cnfirm_pass=self.cleaned_data.get('confirm_password')
        user_credentials = UserCredentials.objects.get(user=self.user)

        if not self.user.check_password(old_pass):
            raise forms.ValidationError("Your old password was entered incorrectly. Please enter it again.")

        if len(new_pass)<8:
            raise forms.ValidationError("Password is too Small.")
        if new_pass != cnfirm_pass:
            raise forms.ValidationError("Both Password doesn't match")


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label='Password',
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        label='Password',
        required=True
    )




class SubjectForm(forms.ModelForm):
    class Meta:
        model=Subject
        fields="__all__"
        widgets = {
            'name': forms.TextInput(attrs={'class': 'subject-name-class', 'placeholder': 'Enter subject name'}),
            'description': forms.Textarea(attrs={'class': 'subject-description-class', 'rows': 4, 'placeholder': 'Enter description'}),
        }


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model=ClassRoom
        fields="__all__"
        widgets = {
            'name': forms.TextInput(attrs={'class': 'classroom-name-class', 'placeholder': 'Enter classroom name'}),
            'grade': forms.NumberInput(attrs={'class': 'classroom-grade-class', 'placeholder': 'Enter grade'}),
            'teacher': forms.Select(attrs={'class': 'classroom-teacher-class'}),
        }
    

class TeacherForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'teacher-subjects'})
    )
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'email', 'subjects']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'teacher-first-name', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'teacher-last-name', 'placeholder': 'Enter last name'}),
            'email': forms.EmailInput(attrs={'class': 'teacher-email', 'placeholder': 'Enter email address'}),           
            'subjects': forms.SelectMultiple(attrs={'class': 'teacher-subjects'}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'class_room']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'student-first-name', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'student-last-name', 'placeholder': 'Enter last name'}),
            'email': forms.EmailInput(attrs={'class': 'student-email', 'placeholder': 'Enter email address'}),
            'class_room': forms.Select(attrs={'class': 'student-class-room'}),
        }
