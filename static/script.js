// script.js — UI logic for Mini-Nmap

const form = document.getElementById('scan-form');
const targetInput = document.getElementById('target');
const startInput = document.getElementById('start_port');
const endInput = document.getElementById('end_port');
const scanBtn = document.getElementById('scan-btn');
const exportBtn = document.getElementById('export-btn');
const showClosed = document.getElementById('show-closed');
const output = document.getElementById('output');
const statusBadge = document.getElementById('status-badge');
const scanBar = document.getElementById('scan-bar');
const statTotal = document.getElementById('stat-total');
const statOpen = document.getElementById('stat-open');
const statClosed = document.getElementById('stat-closed');

let lastScan = null;        // last full scan response (for export)
let abortController = null; // allows cancelling in-flight fetch

function pad(n) { return String(n).padStart(3, '0'); }

function setStats(total, open, closed) {
  statTotal.textContent = pad(total);
  statOpen.textContent = pad(open);
  statClosed.textContent = pad(closed);
}

function renderResults(target, results, durationSec) {
  output.innerHTML = '';

  const header = document.createElement('div');
  header.innerHTML =
    `<div>$ ./mini-nmap --target ${target} --range ${startInput.value}-${endInput.value}</div>` +
    `<div class="cyan">Starting Mini-Nmap 1.0 at ${new Date().toLocaleString()}</div>` +
    `<div class="muted">Initiating SYN-style sweep on ${target}...</div>` +
    `<div class="divider"></div>`;
  output.appendChild(header);

  const visible = results.filter(r => showClosed.checked || r.status === 'OPEN');
  if (visible.length === 0) {
    const m = document.createElement('div');
    m.className = 'muted';
    m.textContent = '// no matching results';
    output.appendChild(m);
  } else {
    for (const r of visible) {
      const row = document.createElement('div');
      row.className = 'line';
      const status = r.status === 'OPEN'
        ? '<span class="open">● open</span>'
        : '<span class="closed">○ closed</span>';
      const banner = r.banner ? ` <span class="banner">| ${escapeHtml(r.banner)}</span>` : '';
      const service = r.service ? escapeHtml(r.service) : '—';
      row.innerHTML =
        `<span class="port">${r.port}/tcp</span>${status}` +
        `<span class="info">${service}${banner}</span>`;
      output.appendChild(row);
    }
  }

  const open = results.filter(r => r.status === 'OPEN').length;
  const footer = document.createElement('div');
  footer.innerHTML =
    `<div class="divider"></div>` +
    `<div class="cyan">Mini-Nmap done: ${results.length} ports scanned, ${open} open</div>` +
    `<div>Scan duration: ${durationSec.toFixed(2)}s</div>` +
    `<div>$ <span class="caret"></span></div>`;
  output.appendChild(footer);

  setStats(results.length, open, results.length - open);
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

function setScanning(on) {
  if (on) {
    scanBtn.textContent = '■ Abort';
    scanBtn.classList.add('abort');
    statusBadge.classList.remove('hidden');
    scanBar.classList.remove('hidden');
    targetInput.disabled = startInput.disabled = endInput.disabled = true;
  } else {
    scanBtn.textContent = '▶ Start Scan';
    scanBtn.classList.remove('abort');
    statusBadge.classList.add('hidden');
    scanBar.classList.add('hidden');
    targetInput.disabled = startInput.disabled = endInput.disabled = false;
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Abort if already scanning
  if (abortController) {
    abortController.abort();
    abortController = null;
    setScanning(false);
    return;
  }

  const target = targetInput.value.trim();
  const start_port = parseInt(startInput.value, 10);
  const end_port = parseInt(endInput.value, 10);

  output.innerHTML = '<div class="muted">▸ Scanning... please wait. Larger ranges take longer.</div>';
  setScanning(true);
  abortController = new AbortController();

  try {
    const res = await fetch('/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target, start_port, end_port }),
      signal: abortController.signal,
    });
    const data = await res.json();

    if (!res.ok) {
      output.innerHTML = `<div class="red">[ERROR] ${escapeHtml(data.error || 'Scan failed')}</div>`;
      return;
    }

    lastScan = data;
    exportBtn.disabled = false;
    renderResults(data.target, data.results, data.duration_seconds);
  } catch (err) {
    if (err.name === 'AbortError') {
      output.innerHTML = '<div class="amber">[ABORTED] Scan cancelled by user.</div>';
    } else {
      output.innerHTML = `<div class="red">[ERROR] ${escapeHtml(err.message)}</div>`;
    }
  } finally {
    abortController = null;
    setScanning(false);
  }
});

showClosed.addEventListener('change', () => {
  if (lastScan) renderResults(lastScan.target, lastScan.results, lastScan.duration_seconds);
});

exportBtn.addEventListener('click', () => {
  if (!lastScan) return;
  const blob = new Blob([JSON.stringify(lastScan, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `mini-nmap_${lastScan.target}_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
});
