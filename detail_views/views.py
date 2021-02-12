from PIL import Image
from django.shortcuts import render, get_object_or_404
from database import views as db
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

# Create your views here.
def detailspage(request, pk=None):
    # model = get_object_or_404(db.EquipmentModelViewSet.queryset, pk)
    # thing = request.GET.get('id')
    context = {
        "model": db.EquipmentModelViewSet.queryset.get(id = pk),
        "instruments": db.InstrumentViewSet.queryset,
        # "model": get_object_or_404(db.EquipmentModelViewSet.queryset, pk)
    }

    return render(request, 'model_details.html', context)
    # return render(request, 'instrumentdetails.html', context)

def pdf_gen(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Instrument Calibration Certificate")
    img = Image.open("detailviews/resources/image.png")
    img = img.rotate(90)
    p.drawInlineImage(img, 200, 500)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='calibration_certificate.pdf')