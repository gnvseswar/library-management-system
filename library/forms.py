from django import forms
from django.contrib.auth.models import User
from . import models
from datetime import date, timedelta

class IssueBookForm(forms.Form):
    isbn2 = forms.ModelChoiceField(queryset=models.Book.objects.all(), empty_label="Book Name [ISBN]", to_field_name="isbn", label="Book (Name and ISBN)")
    name2 = forms.ModelChoiceField(queryset=models.Student.objects.all(), empty_label="Name [Branch] [Class] [Roll No]", to_field_name="user", label="Student Details")
    issue_date = forms.DateField(
        label="Issue Date",
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    isbn2.widget.attrs.update({'class': 'form-control'})
    name2.widget.attrs.update({'class':'form-control'})

class ReturnBookForm(forms.Form):
    return_date = forms.DateField(
        label="Return Date",
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

class BookFeedbackForm(forms.ModelForm):
    class Meta:
        model = models.BookFeedback
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }
