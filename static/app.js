// State Management
let state = {
  modules: {},
  activeModuleId: null,
  activeBrand: null,
  currentOutputText: '',
  currentOutputId: null,
  history: [],
  vaultSearch: '',
  vaultModuleFilter: 'all',
  vaultFavoritesOnly: false,
  modalWorkItem: null
};

// Initialize app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  await Promise.all([
    loadBrandProfile(),
    loadModules(),
    loadDashboardData()
  ]);
}

// ----------------------------------------------------
// API Calls & Data Loading
// ----------------------------------------------------

async function loadBrandProfile() {
  try {
    const res = await fetch('/api/brand');
    const brand = await res.json();
    state.activeBrand = brand;
    updateBrandUI();
  } catch (err) {
    console.error('Failed to load brand:', err);
  }
}

function updateBrandUI() {
  if (!state.activeBrand) return;
  const name = state.activeBrand.brand_name || 'My Brand';
  document.getElementById('sidebar-brand-name').textContent = name;
  document.getElementById('header-brand-pill').textContent = name;
}

async function loadModules() {
  try {
    const res = await fetch('/api/modules');
    state.modules = await res.json();
    renderSidebarModules();
    renderQuickLaunchGrid();
    populateVaultModuleFilter();
  } catch (err) {
    console.error('Failed to load modules:', err);
  }
}

async function loadDashboardData() {
  await Promise.all([
    loadStats(),
    loadRecentWork()
  ]);
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const stats = await res.json();
    
    document.getElementById('stat-total').textContent = stats.total_assets || 0;
    document.getElementById('stat-today').textContent = stats.today_count || 0;
    document.getElementById('stat-favs').textContent = stats.favorites_count || 0;
    document.getElementById('stat-top').textContent = stats.top_module || 'None yet';
    document.getElementById('badge-total-assets').textContent = stats.total_assets || 0;
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

async function loadRecentWork() {
  const container = document.getElementById('recent-work-list');
  try {
    const res = await fetch('/api/history?limit=10');
    const items = await res.json();
    state.history = items;
    renderRecentWorkList(items, container);
  } catch (err) {
    container.innerHTML = `<div class="p-6 text-center text-red-400 text-xs">Failed to load recent work.</div>`;
  }
}

// ----------------------------------------------------
// UI Rendering
// ----------------------------------------------------

function renderSidebarModules() {
  const container = document.getElementById('sidebar-categories');
  if (!container) return;

  // Group modules by category
  const categories = {};
  Object.values(state.modules).forEach(mod => {
    if (!categories[mod.category]) categories[mod.category] = [];
    categories[mod.category].push(mod);
  });

  let html = '';
  for (const [catName, mods] of Object.entries(categories)) {
    html += `
      <div>
        <p class="px-3 text-[10px] font-bold tracking-wider text-slate-400 uppercase mb-1.5">${catName}</p>
        <div class="space-y-0.5">
          ${mods.map(m => `
            <button onclick="selectModule('${m.id}')" id="nav-mod-${m.id}" class="nav-mod-btn w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 transition-all text-left group">
              <span class="flex items-center gap-2.5 truncate">
                <i class="${m.icon} text-slate-400 group-hover:text-indigo-400 transition-colors w-4 text-center"></i>
                <span class="truncate">${m.name}</span>
              </span>
              ${m.badge ? `<span class="text-[9px] px-1.5 py-0.2 rounded font-semibold bg-slate-800 text-slate-400 group-hover:bg-indigo-950 group-hover:text-indigo-300 transition-colors">${m.badge}</span>` : ''}
            </button>
          `).join('')}
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
}

function renderQuickLaunchGrid() {
  const container = document.getElementById('quick-launch-grid');
  if (!container) return;

  // Pick top 5 popular tools
  const priorityIds = ['content_calendar', 'social_content', 'ad_studio', 'blog_generation', 'seo_optimizer'];
  const items = priorityIds.map(id => state.modules[id]).filter(Boolean);

  container.innerHTML = items.map(m => `
    <div onclick="selectModule('${m.id}')" class="bg-[#111827] border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-800/40 p-4 rounded-xl cursor-pointer transition-all duration-200 group flex flex-col justify-between">
      <div class="space-y-2">
        <div class="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
          <i class="${m.icon} text-base"></i>
        </div>
        <h4 class="text-xs font-bold text-slate-200 group-hover:text-indigo-300 transition-colors">${m.name}</h4>
        <p class="text-[11px] text-slate-400 line-clamp-2">${m.description}</p>
      </div>
      <div class="pt-3 mt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 group-hover:text-indigo-400 font-medium">
        <span>Launch Agent</span>
        <i class="fa-solid fa-arrow-right text-[9px] group-hover:translate-x-0.5 transition-transform"></i>
      </div>
    </div>
  `).join('');
}

function renderRecentWorkList(items, container) {
  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="p-10 text-center text-slate-400 space-y-2">
        <div class="w-12 h-12 rounded-xl bg-slate-800/50 flex items-center justify-center text-slate-500 mx-auto text-xl">
          <i class="fa-solid fa-inbox"></i>
        </div>
        <p class="text-xs font-medium text-slate-300">Abhi tak koi kaam record nahi hua.</p>
        <p class="text-[11px] text-slate-400">Kisi bhi module ko run karein, result automatically yahan record hoga.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="p-4 hover:bg-slate-800/30 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 group">
      
      <div class="flex items-start gap-3 min-w-0 flex-1">
        <button onclick="toggleFavoriteWork(${item.id}, event)" class="mt-1 text-slate-400 hover:text-amber-400 transition-colors text-xs" title="Favorite">
          <i class="${item.is_favorite ? 'fa-solid text-amber-400' : 'fa-regular'} fa-star"></i>
        </button>

        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 flex-wrap mb-1">
            <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">${item.module_name}</span>
            <span class="text-[11px] text-slate-400">${item.created_at}</span>
          </div>
          <h4 class="text-xs font-semibold text-slate-200 truncate group-hover:text-indigo-300 transition-colors">${escapeHtml(item.title)}</h4>
          <p class="text-[11px] text-slate-400 line-clamp-1 mt-0.5 font-mono">${escapeHtml(item.output_content.replace(/[#*`|]/g, '').slice(0, 120))}...</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-1.5 flex-shrink-0">
        <button onclick="openDetailModal(${item.id})" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-indigo-600 hover:text-white text-xs font-medium text-slate-300 transition-all flex items-center gap-1 border border-slate-700/80">
          <i class="fa-solid fa-eye text-[11px]"></i>
          <span>View</span>
        </button>
        <button onclick="copyItemText(${item.id})" title="Copy Content" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center text-xs transition-all border border-slate-700/80">
          <i class="fa-regular fa-copy"></i>
        </button>
        <button onclick="exportItem(${item.id}, 'markdown')" title="Export .MD" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center text-xs transition-all border border-slate-700/80">
          <i class="fa-solid fa-download"></i>
        </button>
        <button onclick="deleteWorkItem(${item.id}, event)" title="Delete" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 flex items-center justify-center text-xs transition-all border border-slate-700/80">
          <i class="fa-regular fa-trash-can"></i>
        </button>
      </div>

    </div>
  `).join('');
}

// ----------------------------------------------------
// Navigation & Views
// ----------------------------------------------------

function switchView(viewName) {
  const views = ['dashboard', 'generator', 'vault'];
  views.forEach(v => {
    const el = document.getElementById(`view-${v}`);
    if (el) el.classList.add('hidden');
  });

  const target = document.getElementById(`view-${viewName}`);
  if (target) target.classList.remove('hidden');

  // Update topbar title
  const topTitle = document.getElementById('topbar-title');
  if (viewName === 'dashboard') {
    topTitle.textContent = 'Owner Dashboard // Live Overview';
    highlightNavItem('dashboard');
    loadDashboardData();
  } else if (viewName === 'vault') {
    topTitle.textContent = 'Work Vault // Completed Marketing Deliverables';
    highlightNavItem('vault');
    loadVaultData();
  }
}

function highlightNavItem(activeKey) {
  document.querySelectorAll('.nav-item').forEach(el => {
    el.className = 'nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-all';
  });
  document.querySelectorAll('.nav-mod-btn').forEach(el => {
    el.classList.remove('bg-indigo-600/20', 'text-indigo-300', 'border', 'border-indigo-500/30');
    el.classList.add('text-slate-400');
  });

  const activeBtn = document.getElementById(`nav-btn-${activeKey}`);
  if (activeBtn) {
    activeBtn.className = 'nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all bg-indigo-600/20 text-indigo-400 border border-indigo-500/30';
  }
}

function selectModule(moduleId) {
  const mod = state.modules[moduleId];
  if (!mod) return;

  state.activeModuleId = moduleId;
  switchView('generator');
  closeMobileSidebar();

  // Highlight in sidebar
  document.querySelectorAll('.nav-item').forEach(el => {
    el.className = 'nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-all';
  });
  document.querySelectorAll('.nav-mod-btn').forEach(el => {
    el.classList.remove('bg-indigo-600/20', 'text-indigo-300', 'border', 'border-indigo-500/30');
    el.classList.add('text-slate-400');
  });
  const btn = document.getElementById(`nav-mod-${moduleId}`);
  if (btn) {
    btn.classList.add('bg-indigo-600/20', 'text-indigo-300', 'border', 'border-indigo-500/30');
    btn.classList.remove('text-slate-400');
  }

  // Update Generator UI
  document.getElementById('topbar-title').textContent = `Agent Studio // ${mod.name}`;
  document.getElementById('gen-module-name').textContent = mod.name;
  document.getElementById('gen-module-desc').textContent = mod.description;
  document.getElementById('gen-module-badge').textContent = mod.badge || mod.category;
  document.getElementById('gen-module-icon').innerHTML = `<i class="${mod.icon}"></i>`;

  // Render Form Fields
  renderModuleFormFields(mod);

  // Reset Output Panel
  resetOutputPanel();
}

function renderModuleFormFields(mod) {
  const container = document.getElementById('dynamic-form-fields');
  if (!container) return;

  container.innerHTML = mod.fields.map(field => {
    const reqAttr = field.required ? 'required' : '';
    const reqStar = field.required ? '<span class="text-rose-400">*</span>' : '';

    if (field.type === 'select') {
      return `
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">${field.label} ${reqStar}</label>
          <select name="${field.name}" ${reqAttr} class="w-full bg-[#0F172A] border border-slate-700/80 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors">
            ${field.options.map(opt => `<option value="${opt}" ${opt === field.default ? 'selected' : ''}>${opt}</option>`).join('')}
          </select>
        </div>
      `;
    } else if (field.type === 'textarea') {
      return `
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">${field.label} ${reqStar}</label>
          <textarea name="${field.name}" rows="3" placeholder="${field.placeholder || ''}" ${reqAttr} class="w-full bg-[#0F172A] border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors">${field.default || ''}</textarea>
        </div>
      `;
    } else {
      return `
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">${field.label} ${reqStar}</label>
          <input type="text" name="${field.name}" value="${field.default || ''}" placeholder="${field.placeholder || ''}" ${reqAttr} class="w-full bg-[#0F172A] border border-slate-700/80 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors">
        </div>
      `;
    }
  }).join('');
}

function resetForm() {
  const form = document.getElementById('generator-form');
  if (form) form.reset();
}

function resetOutputPanel() {
  document.getElementById('output-placeholder').classList.remove('hidden');
  document.getElementById('output-loading').classList.add('hidden');
  document.getElementById('output-rendered').classList.add('hidden');
  document.getElementById('output-actions').classList.add('hidden');
  document.getElementById('output-status-indicator').className = 'w-2 h-2 rounded-full bg-slate-500';
  state.currentOutputText = '';
  state.currentOutputId = null;
}

// ----------------------------------------------------
// AI Generation Handler
// ----------------------------------------------------

async function handleGenerate(event) {
  event.preventDefault();
  if (!state.activeModuleId) return;

  const form = document.getElementById('generator-form');
  const formData = new FormData(form);
  const params = {};
  formData.forEach((val, key) => { params[key] = val; });

  // UI state: loading
  const btn = document.getElementById('btn-generate');
  const btnText = document.getElementById('btn-generate-text');
  btn.disabled = true;
  btnText.textContent = 'Generating with Gemini AI...';

  document.getElementById('output-placeholder').classList.add('hidden');
  document.getElementById('output-loading').classList.remove('hidden');
  document.getElementById('output-rendered').classList.add('hidden');
  document.getElementById('output-actions').classList.add('hidden');
  document.getElementById('output-status-indicator').className = 'w-2 h-2 rounded-full bg-amber-400 animate-pulse';

  // Rotating status message
  const statusTexts = [
    'Synthesizing brand voice & target ICP...',
    'Generating psychological hooks & angles...',
    'Structuring high-converting copy & layout...',
    'Polishing markdown formatting & tables...'
  ];
  let msgIdx = 0;
  const statusTimer = setInterval(() => {
    msgIdx = (msgIdx + 1) % statusTexts.length;
    const el = document.getElementById('loading-status-text');
    if (el) el.textContent = statusTexts[msgIdx];
  }, 2200);

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        module_id: state.activeModuleId,
        params: params
      })
    });

    clearInterval(statusTimer);
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || 'Generation failed');

    state.currentOutputText = data.output_content;
    state.currentOutputId = data.id;

    // Render output with responsive table container
    const outputContainer = document.getElementById('output-rendered');
    outputContainer.innerHTML = renderMarkdownWithResponsiveTables(data.output_content);

    document.getElementById('output-loading').classList.add('hidden');
    outputContainer.classList.remove('hidden');
    document.getElementById('output-actions').classList.remove('hidden');
    document.getElementById('output-status-indicator').className = 'w-2 h-2 rounded-full bg-emerald-500';

    showToast('Marketing deliverable generated and saved to history!', 'success');
    loadStats(); // Update stats in background
  } catch (err) {
    clearInterval(statusTimer);
    document.getElementById('output-loading').classList.add('hidden');
    const outputContainer = document.getElementById('output-rendered');
    outputContainer.innerHTML = `<div class="p-4 bg-red-950/40 border border-red-800 rounded-xl text-red-300 text-xs">${err.message}</div>`;
    outputContainer.classList.remove('hidden');
    document.getElementById('output-status-indicator').className = 'w-2 h-2 rounded-full bg-rose-500';
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Generate with Gemini AI';
  }
}

// ----------------------------------------------------
// Export, WhatsApp & Bulletproof Clipboard
// ----------------------------------------------------

async function copyToClipboard(text) {
  if (!text) return false;
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      console.warn('navigator.clipboard failed, trying fallback...', e);
    }
  }
  // Fallback for non-https or restricted mobile contexts
  try {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    const successful = document.execCommand('copy');
    textArea.remove();
    return successful;
  } catch (err) {
    console.error('Fallback copy failed:', err);
    return false;
  }
}

async function copyCurrentOutput() {
  if (!state.currentOutputText) return;
  const ok = await copyToClipboard(state.currentOutputText);
  const label = document.getElementById('copy-btn-label');
  if (ok) {
    label.textContent = 'Copied!';
    setTimeout(() => { label.textContent = 'Copy'; }, 2000);
    showToast('Copied to clipboard!', 'info');
  } else {
    showToast('Could not copy to clipboard', 'error');
  }
}

async function copyModalOutput() {
  if (!state.modalWorkItem) return;
  const ok = await copyToClipboard(state.modalWorkItem.output_content);
  const label = document.getElementById('dm-copy-btn');
  if (ok) {
    label.textContent = 'Copied!';
    setTimeout(() => { label.textContent = 'Copy'; }, 2000);
    showToast('Copied to clipboard!', 'info');
  } else {
    showToast('Could not copy to clipboard', 'error');
  }
}

async function copyItemText(id) {
  try {
    const res = await fetch(`/api/history/${id}`);
    const item = await res.json();
    const ok = await copyToClipboard(item.output_content);
    if (ok) showToast('Copied to clipboard!', 'info');
    else showToast('Could not copy text', 'error');
  } catch (err) {
    showToast('Failed to copy', 'error');
  }
}

function shareOutputWhatsApp() {
  if (!state.currentOutputText) return;
  const cleanText = state.currentOutputText.slice(0, 3500); // URL length safety
  const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(cleanText)}`;
  window.open(waUrl, '_blank');
}

function shareModalWhatsApp() {
  if (!state.modalWorkItem) return;
  const cleanText = `*${state.modalWorkItem.title}*\n\n${state.modalWorkItem.output_content}`.slice(0, 3500);
  const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(cleanText)}`;
  window.open(waUrl, '_blank');
}

function printCurrentOutput() {
  window.print();
}

function printModalOutput() {
  window.print();
}

function exportCurrentOutput(format) {
  if (!state.currentOutputId) return;
  window.open(`/api/export/${state.currentOutputId}?format=${format}`, '_blank');
}

function exportModalOutput(format) {
  if (!state.modalWorkItem) return;
  window.open(`/api/export/${state.modalWorkItem.id}?format=${format}`, '_blank');
}

function exportItem(id, format) {
  window.open(`/api/export/${id}?format=${format}`, '_blank');
}

// ----------------------------------------------------
// Work Vault & History
// ----------------------------------------------------

function populateVaultModuleFilter() {
  const sel = document.getElementById('vault-module-filter');
  if (!sel) return;
  sel.innerHTML = '<option value="all">All Modules</option>' + 
    Object.values(state.modules).map(m => `<option value="${m.id}">${m.name}</option>`).join('');
}

let searchDebounceTimer = null;
function debounceVaultSearch() {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    loadVaultData();
  }, 350);
}

function toggleVaultFavorites() {
  state.vaultFavoritesOnly = !state.vaultFavoritesOnly;
  const btn = document.getElementById('btn-vault-favs');
  if (state.vaultFavoritesOnly) {
    btn.classList.add('bg-amber-500/20', 'text-amber-300', 'border-amber-500/40');
  } else {
    btn.classList.remove('bg-amber-500/20', 'text-amber-300', 'border-amber-500/40');
  }
  loadVaultData();
}

async function loadVaultData() {
  const search = document.getElementById('vault-search-input')?.value || '';
  const filter = document.getElementById('vault-module-filter')?.value || 'all';
  const container = document.getElementById('vault-list');
  if (!container) return;

  container.innerHTML = `<div class="p-8 text-center text-slate-400 text-xs"><i class="fa-solid fa-spinner fa-spin mr-2"></i>Loading vault assets...</div>`;

  try {
    let url = `/api/history?limit=100`;
    if (filter !== 'all') url += `&module_id=${filter}`;
    if (search.trim()) url += `&search=${encodeURIComponent(search.trim())}`;
    if (state.vaultFavoritesOnly) url += `&favorites_only=true`;

    const res = await fetch(url);
    const items = await res.json();
    renderRecentWorkList(items, container);
  } catch (err) {
    container.innerHTML = `<div class="p-6 text-center text-red-400 text-xs">Failed to load vault.</div>`;
  }
}

async function toggleFavoriteWork(id, event) {
  if (event) event.stopPropagation();
  try {
    const res = await fetch(`/api/history/${id}/favorite`, { method: 'POST' });
    const data = await res.json();
    loadDashboardData();
    if (!document.getElementById('view-vault').classList.contains('hidden')) {
      loadVaultData();
    }
  } catch (err) {
    console.error('Failed to favorite:', err);
  }
}

async function deleteWorkItem(id, event) {
  if (event) event.stopPropagation();
  if (!confirm('Are you sure you want to delete this marketing asset?')) return;

  try {
    await fetch(`/api/history/${id}`, { method: 'DELETE' });
    showToast('Asset deleted', 'info');
    loadDashboardData();
    if (!document.getElementById('view-vault').classList.contains('hidden')) {
      loadVaultData();
    }
  } catch (err) {
    showToast('Failed to delete asset', 'error');
  }
}

// ----------------------------------------------------
// Detail Modal
// ----------------------------------------------------

async function openDetailModal(id) {
  try {
    const res = await fetch(`/api/history/${id}`);
    const item = await res.json();
    state.modalWorkItem = item;

    document.getElementById('dm-category-badge').textContent = item.module_name;
    document.getElementById('dm-title').textContent = item.title;
    document.getElementById('dm-content').innerHTML = renderMarkdownWithResponsiveTables(item.output_content);

    document.getElementById('detail-modal').classList.remove('hidden');
  } catch (err) {
    showToast('Could not load asset details', 'error');
  }
}

function renderMarkdownWithResponsiveTables(markdownText) {
  if (!markdownText) return '';
  let html = marked.parse(markdownText);
  // Wrap all table tags in responsive container
  html = html.replace(/<table(\s*[^>]*)>/gi, '<div class="table-responsive"><table$1>');
  html = html.replace(/<\/table>/gi, '</table></div>');
  return html;
}

function closeDetailModal() {
  document.getElementById('detail-modal').classList.add('hidden');
  state.modalWorkItem = null;
}

// ----------------------------------------------------
// Brand Modal & 1-Click Presets
// ----------------------------------------------------

const BRAND_PRESETS = {
  ecommerce: {
    brand_name: "LuxeVibe Apparel & Goods",
    industry: "E-Commerce / Fashion & Lifestyle Store",
    target_audience: "Gen Z & Millennials seeking trendy, high-quality, aesthetic apparel & accessories",
    tone: "Vibrant, trendy, energetic, and high-converting",
    usp: "Express 24h dispatch, premium breathable fabrics, and 100% money-back guarantee",
    website: "https://luxevibe.store"
  },
  realestate: {
    brand_name: "PrimeKey Real Estate & Builders",
    industry: "Real Estate & Property Development",
    target_audience: "Investors, high-income families, and overseas buyers looking for high-ROI property",
    tone: "Authoritative, trustworthy, prestigious, and data-backed",
    usp: "Vetted prime commercial/residential properties with guaranteed rental yields and safe titles",
    website: "https://primekeyestate.com"
  },
  agency: {
    brand_name: "ScaleSphere Digital & AI Agency",
    industry: "Digital Marketing, Web & AI Automation",
    target_audience: "Business owners, e-commerce brands, and founders wanting predictable revenue",
    tone: "Results-oriented, expert, direct, and cutting-edge",
    usp: "Autonomous AI workflows and high-ROAS paid ads that 3x qualified lead flow in 60 days",
    website: "https://scalesphere.io"
  },
  education: {
    brand_name: "SkillSprint Academy",
    industry: "IT Training, Tech Skills & Freelancing Institute",
    target_audience: "Students, college graduates, and job seekers wanting high-income digital skills",
    tone: "Empowering, motivating, clear, and beginner-friendly",
    usp: "Hands-on live client projects, mentorship from top industry earners, and internship placement",
    website: "https://skillsprint.edu"
  },
  restaurant: {
    brand_name: "SmashCraft Burgers & Bistro",
    industry: "Food, Cafe & Casual Dining",
    target_audience: "Foodies, youth, and families looking for gourmet burgers, shakes and cozy vibes",
    tone: "Mouth-watering, fun, welcoming, and community-focused",
    usp: "100% fresh gourmet smashed beef, artisan brioche buns, and secret signature dips",
    website: "https://smashcraft.menu"
  },
  fitness: {
    brand_name: "IronForge Fitness & Gym",
    industry: "Health, Fitness & Personal Training",
    target_audience: "Men and women wanting fat loss, muscle building, and peak energy",
    tone: "High-energy, disciplined, inspiring, and transformative",
    usp: "Customized nutrition protocols, certified strength coaches, and guaranteed 90-day transformation",
    website: "https://ironforge.fit"
  }
};

function applyBrandPreset(presetKey) {
  const p = BRAND_PRESETS[presetKey];
  if (!p) return;
  document.getElementById('bm-name').value = p.brand_name;
  document.getElementById('bm-industry').value = p.industry;
  document.getElementById('bm-audience').value = p.target_audience;
  document.getElementById('bm-tone').value = p.tone;
  document.getElementById('bm-usp').value = p.usp;
  document.getElementById('bm-website').value = p.website;
  showToast(`Loaded "${p.brand_name}" preset! Click 'Save Profile' to activate.`, 'info');
}

function openBrandModal() {
  if (state.activeBrand) {
    document.getElementById('bm-name').value = state.activeBrand.brand_name || '';
    document.getElementById('bm-industry').value = state.activeBrand.industry || '';
    document.getElementById('bm-audience').value = state.activeBrand.target_audience || '';
    document.getElementById('bm-tone').value = state.activeBrand.tone || '';
    document.getElementById('bm-usp').value = state.activeBrand.usp || '';
    document.getElementById('bm-website').value = state.activeBrand.website || '';
  }
  document.getElementById('brand-modal').classList.remove('hidden');
}

function closeBrandModal() {
  document.getElementById('brand-modal').classList.add('hidden');
}

async function handleSaveBrand(event) {
  event.preventDefault();
  const payload = {
    brand_name: document.getElementById('bm-name').value.trim(),
    industry: document.getElementById('bm-industry').value.trim(),
    target_audience: document.getElementById('bm-audience').value.trim(),
    tone: document.getElementById('bm-tone').value.trim(),
    usp: document.getElementById('bm-usp').value.trim(),
    website: document.getElementById('bm-website').value.trim()
  };

  try {
    const res = await fetch('/api/brand', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    state.activeBrand = data.brand;
    updateBrandUI();
    closeBrandModal();
    showToast('Client brand profile saved successfully!', 'success');
  } catch (err) {
    showToast('Failed to save brand profile', 'error');
  }
}

// ----------------------------------------------------
// Utilities
// ----------------------------------------------------

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const colors = {
    success: 'bg-emerald-950/90 text-emerald-200 border-emerald-700/80',
    error: 'bg-rose-950/90 text-rose-200 border-rose-700/80',
    info: 'bg-slate-900/90 text-slate-200 border-indigo-500/50'
  };

  const icons = {
    success: 'fa-solid fa-circle-check text-emerald-400',
    error: 'fa-solid fa-circle-exclamation text-rose-400',
    info: 'fa-solid fa-circle-info text-indigo-400'
  };

  toast.className = `flex items-center gap-2.5 px-4 py-3 rounded-xl border shadow-xl text-xs font-medium backdrop-blur-md fade-in pointer-events-auto transition-all ${colors[type] || colors.info}`;
  toast.innerHTML = `<i class="${icons[type] || icons.info}"></i> <span>${escapeHtml(message)}</span>`;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// Mobile Sidebar Helpers
function toggleMobileSidebar() {
  const sidebar = document.getElementById('app-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!sidebar) return;

  const isClosed = sidebar.classList.contains('-translate-x-full');
  if (isClosed) {
    sidebar.classList.remove('-translate-x-full');
    backdrop?.classList.remove('hidden');
  } else {
    sidebar.classList.add('-translate-x-full');
    backdrop?.classList.add('hidden');
  }
}

function closeMobileSidebar() {
  const sidebar = document.getElementById('app-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (sidebar && window.innerWidth < 768) {
    sidebar.classList.add('-translate-x-full');
    backdrop?.classList.add('hidden');
  }
}
