from django import forms


class CalibrationForm(forms.Form):

    date = forms.DateField(label= "Date (YYYY-MM-DD)")
    comment = forms.CharField(label = "Comment", max_length=100)


class InstrumentsEditForm(forms.Form):
    comment = forms.CharField(label = "Comment", max_length=100)
    model = forms.CharField(label="Model")


class ModelEditForm(forms.Form):
    vendor = forms.CharField(label="Vendor")
    model_number = forms.CharField(label="Model #")
    description = forms.CharField(label="Description")
    comment = forms.CharField(label="Comment", max_length=100)
    calibration_frequency = forms.CharField(label="Calibration Frequency (Days/Calibration)")
