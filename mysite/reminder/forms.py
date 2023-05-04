from django import forms
from django.core.exceptions import ValidationError
from django.utils.datetime_safe import datetime

from reminder.models import Task, Profile


class TitleField(forms.Field):
    pass


class TaskForm(forms.Form):
    title = TitleField()
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type':'time'}))


class TaskModelForm(forms.ModelForm):
    class Meta:
        model = Task
        # fields = ["title", "due_date"]
        # fields = "__all__"
        exclude = ["user"]

        widgets = {
            "due_date" : forms.DateInput(attrs={'type': 'date'}),
            "hour" : forms.TimeInput(attrs={'type':'time'})
        }

        help_texts = {
            "title" : "Title of the task (must be unique)."
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["done"] and cleaned_data["due_date"] > datetime.now().date():
            raise ValidationError("You cannot do the task before due date!", code="error1")
        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["email", "username", "first_name", "last_name", "website"]

    def clean_email(self):
        email = super().clean().get("email")
        if '.ac.ir' not in email and '.edu' not in email:
            raise ValidationError("You must enter an academic email address")
        return email



