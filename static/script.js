let selectedType = 'angebot';

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

// Attach live preview listeners
document.getElementById('hours').addEventListener('input', updatePreview);
document.getElementById('hourly_rate').addEventListener('input', updatePreview);
document.getElementById('material_cost').addEventListener('input', updatePreview);

// Generate document
async function generateDocument() {
    const customerName = document.getElementById('customer_name').value.trim();
    const customerAddress = document.getElementById('customer_address').value.trim();
    const jobDescription = document.getElementById('job_description').value.trim();
    const hours = document.getElementById('hours').value;
    const hourlyRate = document.getElementById('hourly_rate').value;
    const materialCost = document.getElementById('material_cost').value;
    const materials = document.getElementById('materials').value.trim();

    // Validation
    if (!customerName || !customerAddress || !jobDescription) {
        alert('Bitte fülle alle Pflichtfelder aus (*)');
        return;
    }

    // Show loading state
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
            // Show result
            document.getElementById('result-text').textContent = data.ai_content;
            document.getElementById('download-btn').href = `/download/${data.doc_id}`;
            document.getElementById('result').style.display = 'flex';

            // Scroll to result
            document.getElementById('result').scrollIntoView({ behavior: 'smooth' });

            // Reload document list
            loadDocuments();
        }

    } catch (error) {
        alert('Fehler beim Generieren. Bitte versuche es erneut.');
    }

    // Reset button
    btn.disabled = false;
    btn.textContent = '⚡ Dokument generieren';
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
    updatePreview();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Load documents into sidebar
async function loadDocuments() {
    try {
        const response = await fetch('/documents');
        const docs = await response.json();

        const list = document.getElementById('doc-list');
        list.innerHTML = '';

        if (docs.length === 0) {
            list.innerHTML = '<p style="font-size:0.8rem;color:#444;">Noch keine Dokumente</p>';
            return;
        }

        docs.forEach(doc => {
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
        console.error('Fehler beim Laden der Dokumente:', error);
    }
}

// Load documents on page load
loadDocuments();
updatePreview();