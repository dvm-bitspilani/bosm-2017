# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle

# doc = SimpleDocTemplate("table.pdf", pagesize=letter)

# data = [
#     ['Item', 'Cost', 'Quantity'],
#     ['Widget', 3.99, 26],
#     ['Whatsit', 2.25, 26],
#     ['Hooplah', 10.00, 26],
# ]

# parts = []
# table = Table(data, [3 * inch, 1.5 * inch, inch])
# table_with_style = Table(data, [3 * inch, 1.5 * inch, inch])

# table_with_style.setStyle(TableStyle([
#     ('FONT', (0, 0), (-1, -1), 'Helvetica'),
#     ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
#     ('FONTSIZE', (0, 0), (-1, -1), 8),
#     ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#     ('BOX', (0, 0), (-1, 0), 0.25, colors.green),
#     ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
# ]))

# parts.append(table)
# parts.append(Spacer(1, 0.5 * inch))
# parts.append(table_with_style)
# doc.build(parts)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, cm,landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch

a = Image.open("svg.svg")  
a.drawHeight = 2*inch
a.drawWidth = 2*inch
data=[['1',a],['3','4']]
c = canvas.Canvas("Reportlabtest.pdf", pagesize=landscape(A4))
table = Table(data, colWidths=200, rowHeights=50)
table.setStyle(TableStyle([
                           ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                           ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                           ('BACKGROUND',(0,0),(-1,2),colors.lightgrey)
                           ]))
table.wrapOn(c, 200, 400)
table.drawOn(c,20,50)
c.save()
