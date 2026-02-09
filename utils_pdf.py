import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os


def generate_pdf_with_chart(csv_path):
    df = pd.read_csv(csv_path)

    plt.figure(figsize=(6, 3))
    df[df.columns[1]].plot(kind="bar")
    plt.title("Grafik Data") plt.tight_layout()

    chart_path = tempfile.mktemp(suffix=".png")
    plt.savefig(chart_path)
    plt.close()

    pdf_path = tempfile.mktemp(suffix=".pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Laporan Data", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [list(df.columns)] + df.values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#79A3FF")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Grafik:", styles['Heading3']))
    elements.append(Spacer(1, 10))

    chart_image = Image(chart_path, width=400, height=200)
    elements.append(chart_image)

    doc.build(elements)

    os.remove(chart_path)

    return pdf_path
