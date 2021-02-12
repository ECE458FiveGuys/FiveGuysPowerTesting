from django import forms


class CalibrationForm(forms.Form):

    date = forms.DateField(label= "Date (MM/DD/YY)")
    comment = forms.CharField(label = "Comment", max_length=100)