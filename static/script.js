// Hamburger menu toggle
function toggleMenu() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('menu-overlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('visible');
}

let selectedType = 'angebot';
let currentDocId = null;

// Page navigation
function showPage(page) {
    document.getElementById('page-create').style.display = 'none';
    document.getElementById('page-documents').style.display = 'none';
    document.getElementById('page-company').style.display = 'none';
    document.getElementById(`page-${page}`).style.display = 'flex';
    document.getElementById(`page-${page}`).style.flexDirection = 'column';

    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    if (page === 'documents') loadDocumentsPage();
    if (page === 'company') loadCompany();
}

// Select document type
function selectType(type, btn) {
    selectedType = type;
    document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

// Live cost preview
function updatePreview() {
    const hours = parseFloat(document.getElementById('hours').value) || 0;
    const hourlyRate = parseFloat(document.getElementById('hourly_rate').value) || 0;
    const materialCost = parseFloat(document.getElementById('material_cost').value) || 0;

    const labor = hours * hourlyRate;
    const net = labor + materialCost;
    const vat = net * 0.19;
    const gross = net + vat;

    document.getElementById('preview-labor').textContent = `€ ${labor.toFixed(2)}`;
    document.getElementById('preview-material').textContent = `€ ${materialCost.toFixed(2)}`;
    document.getElementById('preview-net').textContent = `€ ${net.toFixed(2)}`;
    document.getElementById('preview-vat').textContent = `€ ${vat.toFixed(2)}`;
    document.getElementById('preview-gross').textContent = `€ ${gross.toFixed(2)}`;
}

document.getElementById('hours').addEventListener('input', updatePreview);
document.getElementById('hourly_rate').addEventListener('input', updatePreview);
document.getElementById('material_cost').addEventListener('input', updatePreview);

// Voice input
let recognition = null;
let isRecording = false;

function toggleVoice() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Spracheingabe wird von diesem Browser nicht unterstützt. Bitte Chrome verwenden.');
        return;
    }

    if (isRecording) {
        recognition.stop();
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'de-DE';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        isRecording = true;
        document.getElementById('voice-btn').classList.add('recording');
        document.getElementById('voice-btn').textContent = '⏹ Aufnahme stoppen';
        document.getElementById('voice-status').textContent = 'Höre zu...';
    };

   recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('voice-status').textContent = '⏳ KI analysiert...';

        try {
            const response = await fetch('/parse-voice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ transcript })
            });

            const result = await response.json();

            if (result.success) {
                const d = result.data;
                if (d.customer_name) document.getElementById('customer_name').value = d.customer_name;
                if (d.customer_address) document.getElementById('customer_address').value = d.customer_address;
                if (d.job_description) document.getElementById('job_description').value = d.job_description;
                if (d.materials) document.getElementById('materials').value = d.materials;
                if (d.hours) document.getElementById('hours').value = d.hours;
                if (d.hourly_rate) document.getElementById('hourly_rate').value = d.hourly_rate;
                if (d.material_cost) document.getElementById('material_cost').value = d.material_cost;
                updatePreview();
                document.getElementById('voice-status').textContent = '✅ Alle Felder ausgefüllt!';
            }
        } catch (error) {
            document.getElementById('job_description').value = transcript;
            document.getElementById('voice-status').textContent = '✅ Sprache erkannt!';
        }
    };
    recognition.onerror = () => {
        document.getElementById('voice-status').textContent = '❌ Fehler. Bitte erneut versuchen.';
    };

    recognition.onend = () => {
        isRecording = false;
        document.getElementById('voice-btn').classList.remove('recording');
        document.getElementById('voice-btn').textContent = '🎤 Spracheingabe';
    };

    recognition.start();
}

// Generate document
async function generateDocument() {
    const customerName = document.getElementById('customer_name').value.trim();
    const customerAddress = document.getElementById('customer_address').value.trim();
    const jobDescription = document.getElementById('job_description').value.trim();
    const hours = document.getElementById('hours').value;
    const hourlyRate = document.getElementById('hourly_rate').value;
    const materialCost = document.getElementById('material_cost').value;
    const materials = document.getElementById('materials').value.trim();

    if (!customerName || !customerAddress || !jobDescription) {
        alert('Bitte fülle alle Pflichtfelder aus (*)');
        return;
    }

    const btn = document.getElementById('generate-btn');
    btn.disabled = true;
    btn.textContent = '⏳ KI generiert Dokument...';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: selectedType,
                customer_name: customerName,
                customer_address: customerAddress,
                job_description: jobDescription,
                materials: materials,
                hours: hours,
                hourly_rate: hourlyRate,
                material_cost: materialCost
            })
        });

        const data = await response.json();

        if (data.success) {
            currentDocId = data.doc_id;

            document.getElementById('result-text').textContent = data.ai_content;
            document.getElementById('result-number').textContent = data.invoice_number;
            document.getElementById('download-btn').href = `/download/${data.doc_id}`;

            // Show convert button only for Angebote
            const convertBtn = document.getElementById('convert-btn');
            if (selectedType === 'angebot') {
                convertBtn.style.display = 'inline-block';
            } else {
                convertBtn.style.display = 'none';
            }

            document.getElementById('result').style.display = 'flex';
            document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
            loadDocuments();
        }

    } catch (error) {
        alert('Fehler beim Generieren. Bitte versuche es erneut.');
    }

    btn.disabled = false;
    btn.textContent = '⚡ Dokument generieren';
}

// Convert Angebot to Rechnung
async function convertToInvoice() {
    if (!currentDocId) return;

    const btn = document.getElementById('convert-btn');
    btn.disabled = true;
    btn.textContent = '⏳ Konvertiere...';

    try {
        const response = await fetch(`/convert/${currentDocId}`, { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            document.getElementById('result-number').textContent = data.invoice_number;
            document.getElementById('download-btn').href = `/download/${data.doc_id}`;
            document.getElementById('result-text').textContent =
                '✅ Erfolgreich zu Rechnung konvertiert! PDF wurde aktualisiert.';
            btn.style.display = 'none';
            loadDocuments();
        }
    } catch (error) {
        alert('Fehler beim Konvertieren.');
    }

    btn.disabled = false;
    btn.textContent = '🧾 Zu Rechnung konvertieren';
}

// Reset form
function resetForm() {
    document.getElementById('customer_name').value = '';
    document.getElementById('customer_address').value = '';
    document.getElementById('job_description').value = '';
    document.getElementById('materials').value = '';
    document.getElementById('hours').value = '2';
    document.getElementById('hourly_rate').value = '65';
    document.getElementById('material_cost').value = '0';
    document.getElementById('result').style.display = 'none';
    currentDocId = null;
    updatePreview();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Load sidebar documents
async function loadDocuments() {
    try {
        const response = await fetch('/documents');
        const docs = await response.json();
        const list = document.getElementById('doc-list');
        list.innerHTML = '';

        if (docs.length === 0) {
            list.innerHTML = '<p style="font-size:0.78rem;color:#333;">Noch keine Dokumente</p>';
            return;
        }

        docs.slice(0, 5).forEach(doc => {
            const item = document.createElement('div');
            item.classList.add('doc-item');
            item.innerHTML = `
                <div class="doc-item-type">${doc.type === 'rechnung' ? '🧾 Rechnung' : '📋 Angebot'}</div>
                <div class="doc-item-name">${doc.customer_name}</div>
                <div class="doc-item-amount">€ ${parseFloat(doc.total_gross).toFixed(2)}</div>
            `;
            item.onclick = () => window.location.href = `/download/${doc.id}`;
            list.appendChild(item);
        });
    } catch (error) {
        console.error('Fehler:', error);
    }
}

// Load full documents page
async function loadDocumentsPage() {
    try {
        const response = await fetch('/documents');
        const docs = await response.json();
        const grid = document.getElementById('documents-list');
        grid.innerHTML = '';

        if (docs.length === 0) {
            grid.innerHTML = '<p style="color:#444;">Noch keine Dokumente vorhanden.</p>';
            return;
        }

        docs.forEach(doc => {
            const date = new Date(doc.created_at).toLocaleDateString('de-DE');
            const card = document.createElement('div');
            card.classList.add('document-card');
            card.innerHTML = `
                <div class="document-card-left">
                    <div class="document-card-type">
                        ${doc.type === 'rechnung' ? '🧾 Rechnung' : '📋 Angebot'}
                    </div>
                    <div class="document-card-name">${doc.customer_name}</div>
                    <div class="document-card-number">${doc.invoice_number || ''}</div>
                </div>
                <div class="document-card-right">
                    <div class="document-card-date">${date}</div>
                    <div class="document-card-amount">€ ${parseFloat(doc.total_gross).toFixed(2)}</div>
                    <div class="card-actions">
                        <a href="/download/${doc.id}" class="card-download">⬇️ PDF</a>
                        ${doc.type === 'angebot' ? `<button class="card-convert" 
                            onclick="convertFromCard(${doc.id})">→ Rechnung</button>` : ''}
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Fehler:', error);
    }
}

// Convert from documents page
async function convertFromCard(docId) {
    try {
        const response = await fetch(`/convert/${docId}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            alert(`✅ Erfolgreich konvertiert! Rechnungsnummer: ${data.invoice_number}`);
            loadDocumentsPage();
            loadDocuments();
        }
    } catch (error) {
        alert('Fehler beim Konvertieren.');
    }
}

// Save company profile
async function saveCompany() {
    const data = {
        name: document.getElementById('company_name').value,
        address: document.getElementById('company_address').value,
        phone: document.getElementById('company_phone').value,
        email: document.getElementById('company_email').value,
        tax_number: document.getElementById('company_tax_number').value,
        iban: document.getElementById('company_iban').value,
        bic: document.getElementById('company_bic').value
    };

    try {
        const response = await fetch('/company', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            alert('✅ Firmenprofil gespeichert!');
        }
    } catch (error) {
        alert('Fehler beim Speichern.');
    }
}

// Load company profile
async function loadCompany() {
    try {
        const response = await fetch('/company');
        const data = await response.json();
        if (data.name) {
            document.getElementById('company_name').value = data.name || '';
            document.getElementById('company_address').value = data.address || '';
            document.getElementById('company_phone').value = data.phone || '';
            document.getElementById('company_email').value = data.email || '';
            document.getElementById('company_tax_number').value = data.tax_number || '';
            document.getElementById('company_iban').value = data.iban || '';
            document.getElementById('company_bic').value = data.bic || '';
        }
    } catch (error) {
        console.error('Fehler:', error);
    }
}

// Init
loadDocuments();
updatePreview();