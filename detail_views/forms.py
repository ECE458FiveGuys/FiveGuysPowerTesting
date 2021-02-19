from django import forms


class CalibrationForm(forms.Form):

    date = forms.DateField(label= "Date (YYYY-MM-DD)")
    comment = forms.CharField(label = "Comment", max_length=100)


class InstrumentsEditForm(forms.Form):
    comment = forms.CharField(label = "Comment", max_length=100,required=False)
    # model = forms.CharField(label="Model",required=False)


class ModelEditForm(forms.Form):
    vendor = forms.CharField(label="Vendor",required=False)
    model_number = forms.CharField(label="Model #",required=False)
    description = forms.CharField(label="Description",required=False)
    comment = forms.CharField(label="Comment", max_length=100,required=False)
    calibration_frequency = forms.CharField(label="Calibration Frequency (Days/Calibration)",required=False)
