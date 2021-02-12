import requests
from PIL import Image
from django.shortcuts import render, get_object_or_404

from database import views as db
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

# Create your views here.
from detail_views.forms import CalibrationForm


def model_detail_page(request, pk=None):
    model = get_object_or_404(db.EquipmentModelViewSet.queryset, pk=pk)
    context = {
        "model": model,
        "instruments": db.InstrumentViewSet.queryset.all().filter(model=model),
    }

    return render(request, 'model_details.html', context)


def instrument_detail_page(request, serial=None):
    instrument = get_object_or_404(db.InstrumentViewSet.queryset.all(), serial_number=serial)
    user = request.user

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = CalibrationForm(request.POST)
        if not form.is_valid():
            print("form isn't valid")

            # redirect to a new URL:
            #TODO form submission response
        else:
            print("form is valid")
            response = requests.post('http://'+request.get_host()+'/calibration-events/', data=form.data.dict())


    # If this is a GET (or any other method) create the default form.
    else:
        form = CalibrationForm()

    context = {
        "instrument": instrument,
        "model": instrument.model,
        "instruments": db.InstrumentViewSet.queryset.all(),
        "form": form,
        "user": user,
    }
    return render(request, 'instrument_details.html', context)


def pdf_gen(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Instrument Calibration Certificate")
    img = Image.open("detail_views/resources/image.png")
    img = img.rotate(90)
    p.drawInlineImage(img, 200, 500)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='calibration_certificate.pdf')
