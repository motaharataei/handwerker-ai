from flask import Flask, render_template, request, jsonify, send_file
from groq import Groq
from dotenv import load_dotenv
from database import init_db, save_document, get_all_documents, get_document
from pdf_generator import generate_pdf
import os
import json

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize database on startup
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    doc_type = data.get("type")
    customer_name = data.get("customer_name")
    customer_address = data.get("customer_address")
    job_description = data.get("job_description")
    materials = data.get("materials")
    hours = float(data.get("hours", 1))
    hourly_rate = float(data.get("hourly_rate", 50))

    # Calculate costs
    labor_cost = hours * hourly_rate
    material_cost = float(data.get("material_cost", 0))
    total_net = labor_cost + material_cost
    vat = total_net * 0.19
    total_gross = total_net + vat

    # Ask AI to write professional job description
    doc_type_german = "Rechnung" if doc_type == "rechnung" else "Angebot"

    prompt = f"""
Du bist ein professioneller Assistent für deutsche Handwerksbetriebe.
Schreibe eine professionelle Leistungsbeschreibung auf Deutsch für eine {doc_type_german}.

Kundenname: {customer_name}
Jobbeschreibung: {job_description}
Verwendete Materialien: {materials if materials else 'keine angegeben'}
Arbeitsstunden: {hours} Stunden

Schreibe NUR die Leistungsbeschreibung, kurz und professionell, maximal 5 Sätze.
Kein Anrede, keine Grußformel, nur die Beschreibung der ausgeführten Arbeiten.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    ai_content = response.choices[0].message.content.strip()

    # Save to database
    doc_data = {
        'type': doc_type,
        'customer_name': customer_name,
        'customer_address': customer_address,
        'job_description': job_description,
        'materials': materials,
        'hours': hours,
        'hourly_rate': hourly_rate,
        'total_net': total_net,
        'vat': vat,
        'total_gross': total_gross,
        'ai_content': ai_content
    }

    doc_id = save_document(doc_data)

    # Generate PDF
    generate_pdf(doc_id, doc_data)

    return jsonify({
        'success': True,
        'doc_id': doc_id,
        'ai_content': ai_content,
        'total_net': round(total_net, 2),
        'vat': round(vat, 2),
        'total_gross': round(total_gross, 2)
    })

@app.route("/download/<int:doc_id>")
def download(doc_id):
    filename = f'static/pdfs/document_{doc_id}.pdf'
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True,
                        download_name=f'dokument_{doc_id}.pdf')
    return jsonify({'error': 'Dokument nicht gefunden'}), 404

@app.route("/documents")
def documents():
    rows = get_all_documents()
    docs = []
    for row in rows:
        docs.append({
            'id': row[0],
            'type': row[1],
            'customer_name': row[2],
            'total_gross': row[10],
            'created_at': row[12]
        })
    return jsonify(docs)

if __name__ == "__main__":
    app.run(debug=True)