from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime
import os

def generate_pdf(doc_id, data):
    # Create pdfs folder if it doesn't exist
    if not os.path.exists('static/pdfs'):
        os.makedirs('static/pdfs')

    filename = f'static/pdfs/document_{doc_id}.pdf'
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle('title',
        fontSize=20, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a1a'), spaceAfter=6)

    label_style = ParagraphStyle('label',
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#888888'))

    normal_style = ParagraphStyle('normal',
        fontSize=10, fontName='Helvetica',
        textColor=colors.HexColor('#1a1a1a'), spaceAfter=4)

    bold_style = ParagraphStyle('bold',
        fontSize=10, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a1a'))

    # Document type title
    doc_type = "RECHNUNG" if data['type'] == 'rechnung' else "ANGEBOT"
    elements.append(Paragraph(doc_type, title_style))
    elements.append(Spacer(1, 0.5*cm))

    # Company and customer info side by side
    date_str = datetime.now().strftime('%d.%m.%Y')
    doc_number = f"{doc_type[:3]}-{doc_id:04d}"

    info_data = [
        [Paragraph('VON', label_style), Paragraph('AN', label_style),
         Paragraph('DATUM', label_style), Paragraph('NUMMER', label_style)],
        [Paragraph(data.get('company_name', 'Ihr Unternehmen'), normal_style),
         Paragraph(data['customer_name'], normal_style),
         Paragraph(date_str, normal_style),
         Paragraph(doc_number, normal_style)],
        [Paragraph('', normal_style),
         Paragraph(data['customer_address'].replace('\n', '<br/>'), normal_style),
         Paragraph('', normal_style),
         Paragraph('', normal_style)],
    ]

    info_table = Table(info_data, colWidths=[4.5*cm, 6*cm, 3*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.8*cm))

    # Divider line
    line_data = [[''] ]
    line_table = Table(line_data, colWidths=[17.5*cm])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#e0e0e0')),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.8*cm))

    # Job description
    elements.append(Paragraph('Leistungsbeschreibung', label_style))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(data['ai_content'], normal_style))
    elements.append(Spacer(1, 0.8*cm))

    # Cost table
    hourly_rate = float(data['hourly_rate'])
    hours = float(data['hours'])
    labor_cost = hourly_rate * hours
    total_net = float(data['total_net'])
    vat_amount = float(data['vat'])
    total_gross = float(data['total_gross'])

    cost_data = [
        [Paragraph('Position', bold_style),
         Paragraph('Menge', bold_style),
         Paragraph('Einzelpreis', bold_style),
         Paragraph('Gesamt', bold_style)],
        [Paragraph('Arbeitszeit', normal_style),
         Paragraph(f'{hours} Std.', normal_style),
         Paragraph(f'€ {hourly_rate:.2f}/Std.', normal_style),
         Paragraph(f'€ {labor_cost:.2f}', normal_style)],
    ]

    if data.get('materials'):
        cost_data.append([
            Paragraph('Material', normal_style),
            Paragraph('1', normal_style),
            Paragraph(f'€ {(total_net - labor_cost):.2f}', normal_style),
            Paragraph(f'€ {(total_net - labor_cost):.2f}', normal_style)
        ])

    # Totals
    cost_data.extend([
        ['', '', Paragraph('Netto', bold_style), Paragraph(f'€ {total_net:.2f}', normal_style)],
        ['', '', Paragraph('MwSt. 19%', bold_style), Paragraph(f'€ {vat_amount:.2f}', normal_style)],
        ['', '', Paragraph('Gesamt Brutto', bold_style), Paragraph(f'€ {total_gross:.2f}', bold_style)],
    ])

    cost_table = Table(cost_data, colWidths=[7*cm, 3*cm, 4*cm, 3.5*cm])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#e0e0e0')),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor('#e0e0e0')),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#1a1a1a')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 1*cm))

    # Payment note
    if data['type'] == 'rechnung':
        elements.append(Paragraph(
            'Bitte überweisen Sie den Betrag innerhalb von 14 Tagen nach Erhalt dieser Rechnung.',
            normal_style))
    else:
        elements.append(Paragraph(
            'Dieses Angebot ist 30 Tage gültig.',
            normal_style))

    elements.append(Spacer(1, 1.5*cm))
    elements.append(Paragraph('Vielen Dank für Ihren Auftrag!', bold_style))

    doc.build(elements)
    return filename