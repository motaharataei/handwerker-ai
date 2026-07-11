from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from datetime import datetime
import os

def generate_pdf(doc_id, data):
    if not os.path.exists('static/pdfs'):
        os.makedirs('static/pdfs')

    filename = f'static/pdfs/document_{doc_id}.pdf'
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2.2*cm,
        leftMargin=2.2*cm,
        topMargin=2.2*cm,
        bottomMargin=2.2*cm
    )

    elements = []

    # ── STYLES ──────────────────────────────────────────
    doc_title_style = ParagraphStyle('doc_title',
        fontSize=28,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#111111'),
        leading=34,
        spaceAfter=0,
        spaceBefore=0)

    section_label_style = ParagraphStyle('section_label',
        fontSize=7.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#aaaaaa'),
        leading=12,
        spaceAfter=4,
        spaceBefore=0,
        letterSpacing=1)

    company_name_style = ParagraphStyle('company_name',
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#111111'),
        leading=16,
        spaceAfter=2)

    small_style = ParagraphStyle('small',
        fontSize=9,
        fontName='Helvetica',
        textColor=colors.HexColor('#555555'),
        leading=14,
        spaceAfter=1)

    normal_style = ParagraphStyle('normal',
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#222222'),
        leading=16,
        spaceAfter=2)

    bold_style = ParagraphStyle('bold',
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#111111'),
        leading=16,
        spaceAfter=2)

    meta_label_style = ParagraphStyle('meta_label',
        fontSize=7.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#aaaaaa'),
        leading=12,
        spaceAfter=2,
        letterSpacing=0.5)

    meta_value_style = ParagraphStyle('meta_value',
        fontSize=9.5,
        fontName='Helvetica',
        textColor=colors.HexColor('#222222'),
        leading=14,
        spaceAfter=0)

    meta_value_bold_style = ParagraphStyle('meta_value_bold',
        fontSize=9.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#111111'),
        leading=14,
        spaceAfter=0)

    table_header_style = ParagraphStyle('table_header',
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#444444'),
        leading=14)

    table_cell_style = ParagraphStyle('table_cell',
        fontSize=9.5,
        fontName='Helvetica',
        textColor=colors.HexColor('#222222'),
        leading=14)

    table_cell_bold_style = ParagraphStyle('table_cell_bold',
        fontSize=9.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#111111'),
        leading=14)

    # ── DOCUMENT INFO ───────────────────────────────────
    doc_type = "RECHNUNG" if data['type'] == 'rechnung' else "ANGEBOT"
    invoice_number = data.get('invoice_number', '')
    date_str = datetime.now().strftime('%d.%m.%Y')
    company_name = data.get('company_name', 'Ihr Unternehmen')
    company_address = data.get('company_address', '')
    company_phone = data.get('company_phone', '')
    company_email = data.get('company_email', '')
    company_tax = data.get('company_tax_number', '')
    company_iban = data.get('company_iban', '')
    company_bic = data.get('company_bic', '')

    # ── SECTION 1: COMPANY + DOCUMENT TITLE ─────────────
    # Company info on the left, document title on the right
    company_block = [
        Paragraph(company_name, company_name_style),
        Paragraph(company_address, small_style),
    ]
    if company_phone:
        company_block.append(Paragraph(f'Tel: {company_phone}', small_style))
    if company_email:
        company_block.append(Paragraph(f'E-Mail: {company_email}', small_style))

    company_cell = company_block
    title_cell = [Paragraph(doc_type, doc_title_style)]

    top_table = Table(
        [[company_cell, title_cell]],
        colWidths=[9.5*cm, 7.6*cm]
    )
    top_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('VALIGN', (1, 0), (1, 0), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(top_table)

    # Space between title and metadata — this is the key fix
    elements.append(Spacer(1, 0.7*cm))

    # ── SECTION 2: DOCUMENT METADATA ────────────────────
    # Number, date, tax number in a clean row
    meta_table = Table(
        [
            [Paragraph('NUMMER', meta_label_style),
             Paragraph('DATUM', meta_label_style),
             Paragraph('STEUERNUMMER', meta_label_style)],
            [Paragraph(invoice_number, meta_value_bold_style),
             Paragraph(date_str, meta_value_style),
             Paragraph(company_tax, meta_value_style)],
        ],
        colWidths=[6*cm, 4*cm, 7.1*cm]
    )
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.8*cm))

    # ── DIVIDER ─────────────────────────────────────────
    elements.append(HRFlowable(
        width='100%',
        thickness=0.5,
        color=colors.HexColor('#dddddd'),
        spaceAfter=0.8*cm
    ))

    # ── SECTION 3: CUSTOMER ─────────────────────────────
    elements.append(Paragraph('RECHNUNGSEMPFÄNGER', section_label_style))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(data['customer_name'], bold_style))
    elements.append(Paragraph(data['customer_address'], small_style))
    elements.append(Spacer(1, 0.9*cm))

    # ── SECTION 4: JOB DESCRIPTION ──────────────────────
    elements.append(Paragraph('LEISTUNGSBESCHREIBUNG', section_label_style))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(data['ai_content'], normal_style))
    elements.append(Spacer(1, 0.9*cm))

    # ── SECTION 5: COST TABLE ───────────────────────────
    hourly_rate = float(data['hourly_rate'])
    hours = float(data['hours'])
    labor_cost = hourly_rate * hours
    total_net = float(data['total_net'])
    vat_amount = float(data['vat'])
    total_gross = float(data['total_gross'])
    material_cost = total_net - labor_cost

    cost_data = [
        [Paragraph('POSITION', table_header_style),
         Paragraph('MENGE', table_header_style),
         Paragraph('EINZELPREIS', table_header_style),
         Paragraph('GESAMT', table_header_style)],
        [Paragraph('Arbeitszeit', table_cell_style),
         Paragraph(f'{hours} Std.', table_cell_style),
         Paragraph(f'€ {hourly_rate:.2f} / Std.', table_cell_style),
         Paragraph(f'€ {labor_cost:.2f}', table_cell_style)],
    ]

    if material_cost > 0:
        cost_data.append([
            Paragraph('Material', table_cell_style),
            Paragraph('1', table_cell_style),
            Paragraph(f'€ {material_cost:.2f}', table_cell_style),
            Paragraph(f'€ {material_cost:.2f}', table_cell_style),
        ])

    # Spacer row before totals
    cost_data.append(['', '', '', ''])

    cost_data.extend([
        ['', '', Paragraph('Netto', table_cell_style),
         Paragraph(f'€ {total_net:.2f}', table_cell_style)],
        ['', '', Paragraph('MwSt. 19 %', table_cell_style),
         Paragraph(f'€ {vat_amount:.2f}', table_cell_style)],
        ['', '', Paragraph('Gesamt Brutto', table_cell_bold_style),
         Paragraph(f'€ {total_gross:.2f}', table_cell_bold_style)],
    ])

    n_data_rows = len(cost_data)
    cost_table = Table(cost_data, colWidths=[7.2*cm, 2.8*cm, 4*cm, 3.1*cm])
    cost_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#cccccc')),
        # All cells
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        # Line above totals section
        ('LINEABOVE', (2, -3), (-1, -3), 0.5, colors.HexColor('#cccccc')),
        # Bold bottom border on last row
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#111111')),
        # Alternate row shading for data rows
        ('ROWBACKGROUNDS', (0, 1), (-1, -4),
         [colors.HexColor('#ffffff'), colors.HexColor('#fafafa')]),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 1*cm))

    # ── SECTION 6: PAYMENT INFO ──────────────────────────
    if data['type'] == 'rechnung':
        elements.append(Paragraph('ZAHLUNGSINFORMATIONEN', section_label_style))
        elements.append(Spacer(1, 0.2*cm))
        if company_iban:
            elements.append(Paragraph(f'IBAN: {company_iban}', normal_style))
        if company_bic:
            elements.append(Paragraph(f'BIC:  {company_bic}', normal_style))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(
            'Bitte überweisen Sie den Gesamtbetrag innerhalb von 14 Tagen '
            'nach Erhalt dieser Rechnung. Vielen Dank!',
            normal_style))
    else:
        elements.append(Paragraph(
            'Dieses Angebot ist 30 Tage ab Ausstellungsdatum gültig. '
            'Bei Fragen stehen wir Ihnen gerne zur Verfügung.',
            normal_style))

    elements.append(Spacer(1, 1.6*cm))

    # ── FOOTER ───────────────────────────────────────────
    elements.append(HRFlowable(
        width='100%',
        thickness=0.5,
        color=colors.HexColor('#eeeeee'),
        spaceAfter=0.3*cm
    ))
    elements.append(Paragraph(
        f'{company_name}  ·  {company_address}  ·  {company_email}',
        ParagraphStyle('footer',
            fontSize=7.5,
            fontName='Helvetica',
            textColor=colors.HexColor('#aaaaaa'),
            alignment=1)
    ))

    doc.build(elements)
    return filename