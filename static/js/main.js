/* ==========================================================================
   SecureBox — UI Interactions (Vanilla JS)
   ========================================================================== */

// --- Toast Notification System ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        error: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        info: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" type="button" onclick="dismissToast(this.parentElement)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        dismissToast(toast);
    }, 4000);
}

function dismissToast(toastElement) {
    if (toastElement && !toastElement.classList.contains('removing')) {
        toastElement.classList.add('removing');
        setTimeout(() => toastElement.remove(), 200);
    }
}

// --- Copy to Clipboard ---
function copyToClipboard(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.value || el.textContent;
    if (!text) {
        showToast('Nothing to copy.', 'error');
        return;
    }
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback
        try {
            el.select();
            document.execCommand('copy');
            showToast('Copied to clipboard!', 'success');
        } catch (err) {
            showToast('Failed to copy.', 'error');
        }
    });
}

// --- Download Text as File ---
function downloadText(elementId, filename) {
    const el = document.getElementById(elementId);
    if (!el || !el.value) {
        showToast('Nothing to download.', 'error');
        return;
    }
    const blob = new Blob([el.value], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'output.txt';
    a.click();
    URL.revokeObjectURL(url);
    showToast('File download started!', 'success');
}

// --- Mobile Sidebar Toggle ---
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
    }
}

// --- Password Visibility Toggle ---
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const eyeIcon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
    const eyeOffIcon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
    
    if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = eyeOffIcon;
    } else {
        input.type = 'password';
        btn.innerHTML = eyeIcon;
    }
}

// --- Clear Form ---
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.querySelectorAll('textarea, input[type=text], input[type=password]').forEach(el => {
            if (el.name !== 'algorithm') el.value = '';
        });
        showToast('Form cleared.', 'info');
    }
}

// --- Algorithm Tab Switching (for Text encryption page) ---
function switchAlgorithm(algo) {
    // Switch active style classes on tabs
    document.querySelectorAll('.tab').forEach(tab => {
        const input = tab.querySelector('input[type=radio][name="algorithm"]');
        if (input && input.value === algo) {
            tab.classList.add('active');
        } else if (input) {
            tab.classList.remove('active');
        }
    });

    const symmetricFields = document.getElementById('symmetricKeyFields');
    const rsaFields = document.getElementById('rsaKeyFields');
    if (!symmetricFields || !rsaFields) return;

    if (algo === 'rsa') {
        symmetricFields.style.display = 'none';
        rsaFields.style.display = 'block';
        
        // Remove required attribute from secret key if present
        const keyInput = document.getElementById('keyInput');
        if (keyInput) keyInput.removeAttribute('required');
    } else {
        symmetricFields.style.display = 'block';
        rsaFields.style.display = 'none';
        
        // Add required attribute back
        const keyInput = document.getElementById('keyInput');
        if (keyInput) keyInput.setAttribute('required', 'required');
    }
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', function() {
    // 1. Initial State for Algorithm Tabs
    const checkedAlgo = document.querySelector('input[name="algorithm"]:checked');
    if (checkedAlgo) {
        switchAlgorithm(checkedAlgo.value);
    }
    
    // Listen for algorithm changes to switch tabs/fields dynamically
    document.querySelectorAll('input[name="algorithm"]').forEach(radio => {
        radio.addEventListener('change', function() {
            switchAlgorithm(this.value);
        });
    });

    // Listen for tab clicks directly to handle hidden radio buttons reliably
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function(e) {
            const radio = this.querySelector('input[type="radio"]');
            if (radio && !radio.checked) {
                radio.checked = true;
                // Dispatch change event manually
                radio.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    });

    // 2. Drag & Drop Upload Zone Setup
    document.querySelectorAll('.upload-zone').forEach(zone => {
        const input = zone.querySelector('input[type="file"]');
        if (!input) return;
        
        zone.addEventListener('click', () => input.click());
        
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });
        
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                input.dispatchEvent(new Event('change'));
            }
        });
        
        input.addEventListener('change', function() {
            const textEl = zone.querySelector('.upload-zone-text');
            if (this.files.length) {
                if (textEl) textEl.textContent = this.files[0].name;
                zone.classList.add('has-file');
            } else {
                if (textEl) textEl.textContent = 'Click or drag file here';
                zone.classList.remove('has-file');
            }
        });
    });

    // 3. Staggered Entrance Animations
    document.querySelectorAll('.animate-slide-up').forEach((el, i) => {
        el.style.animationDelay = `${i * 0.06}s`;
    });
});
