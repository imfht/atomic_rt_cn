// Global state
let currentPage = 1;
let currentSearch = '';
let currentTechnique = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    loadStats();
    loadTechniques(1);
    initModal();
});

// Navigation
function initNavigation() {
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding section
            const target = this.getAttribute('href').substring(1);
            showSection(target);
        });
    });
}

function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => {
        s.style.display = 'none';
    });
    
    // Show target section
    const targetSection = document.getElementById(`${section}-section`);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Load data if needed
    if (section === 'techniques' && document.querySelectorAll('.technique-card').length === 0) {
        loadTechniques(1);
    }
}

// Stats
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-techniques').textContent = data.total_techniques;
            document.getElementById('total-tests').textContent = data.total_tests;
            document.getElementById('analyzed-techniques').textContent = data.analyzed_techniques;
            document.getElementById('analysis-percentage').textContent = data.analysis_percentage + '%';
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

// Techniques
function loadTechniques(page, search = '') {
    const container = document.getElementById('techniques-list');
    container.innerHTML = '<p class="loading">加载中...</p>';
    
    let url = `/api/techniques?page=${page}&per_page=20`;
    if (search) {
        url += `&search=${encodeURIComponent(search)}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.techniques.length === 0) {
                container.innerHTML = '<p class="loading">暂无数据。请先同步数据。</p>';
                return;
            }
            
            container.innerHTML = '';
            data.techniques.forEach(technique => {
                const card = createTechniqueCard(technique);
                container.appendChild(card);
            });
            
            // Update pagination
            updatePagination(data);
            currentPage = page;
            currentSearch = search;
        })
        .catch(error => {
            console.error('Error loading techniques:', error);
            container.innerHTML = '<p class="loading">加载失败，请重试。</p>';
        });
}

function createTechniqueCard(technique) {
    const card = document.createElement('div');
    card.className = 'technique-card';
    card.onclick = () => showTechniqueDetail(technique.technique_id);
    
    const hasLLM = technique.llm_summary ? '<span class="llm-badge">已分析</span>' : '';
    
    card.innerHTML = `
        <div class="technique-header">
            <span class="technique-id">${technique.technique_id}</span>
            ${hasLLM}
        </div>
        <div class="technique-name">${technique.name || '未命名'}</div>
        <div class="technique-description">${technique.description || '暂无描述'}</div>
        <div class="technique-meta">
            <span>战术: ${technique.tactic || 'N/A'}</span>
            <span>平台: ${technique.platform || 'N/A'}</span>
        </div>
    `;
    
    return card;
}

function searchTechniques() {
    const searchInput = document.getElementById('search-input');
    const search = searchInput.value.trim();
    loadTechniques(1, search);
}

// Allow search on Enter key
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchTechniques();
            }
        });
    }
});

// Pagination
function updatePagination(data) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (data.pages <= 1) return;
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '上一页';
    prevBtn.disabled = data.page === 1;
    prevBtn.onclick = () => loadTechniques(data.page - 1, currentSearch);
    pagination.appendChild(prevBtn);
    
    // Page numbers
    for (let i = 1; i <= Math.min(data.pages, 10); i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === data.page ? 'active' : '';
        pageBtn.onclick = () => loadTechniques(i, currentSearch);
        pagination.appendChild(pageBtn);
    }
    
    if (data.pages > 10) {
        const ellipsis = document.createElement('span');
        ellipsis.textContent = '...';
        ellipsis.style.padding = '0.5rem';
        pagination.appendChild(ellipsis);
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '下一页';
    nextBtn.disabled = data.page === data.pages;
    nextBtn.onclick = () => loadTechniques(data.page + 1, currentSearch);
    pagination.appendChild(nextBtn);
}

// Technique Detail Modal
function initModal() {
    const modal = document.getElementById('technique-modal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }
}

function showTechniqueDetail(techniqueId) {
    const modal = document.getElementById('technique-modal');
    const detailContainer = document.getElementById('technique-detail');
    
    detailContainer.innerHTML = '<p class="loading">加载中...</p>';
    modal.style.display = 'block';
    
    fetch(`/api/techniques/${techniqueId}`)
        .then(response => response.json())
        .then(technique => {
            currentTechnique = technique;
            detailContainer.innerHTML = renderTechniqueDetail(technique);
        })
        .catch(error => {
            console.error('Error loading technique detail:', error);
            detailContainer.innerHTML = '<p class="loading">加载失败，请重试。</p>';
        });
}

function renderTechniqueDetail(technique) {
    let html = `
        <h2>${technique.technique_id}: ${technique.name || '未命名'}</h2>
        
        <div class="detail-section">
            <h3>基本信息</h3>
            <p><strong>战术:</strong> ${technique.tactic || 'N/A'}</p>
            <p><strong>平台:</strong> ${technique.platform || 'N/A'}</p>
            <p><strong>描述:</strong> ${technique.description || '暂无描述'}</p>
        </div>
    `;
    
    // LLM Analysis
    if (technique.llm_summary || technique.llm_analysis) {
        html += `
            <div class="detail-section">
                <h3>AI 分析</h3>
                ${technique.llm_summary ? `<p><strong>摘要:</strong> ${technique.llm_summary}</p>` : ''}
                ${technique.llm_analysis ? `<p><strong>详细分析:</strong></p><div>${technique.llm_analysis.replace(/\n/g, '<br>')}</div>` : ''}
                <p style="color: #888; font-size: 0.9rem;">分析时间: ${technique.llm_processed_at || 'N/A'}</p>
            </div>
        `;
    } else {
        html += `
            <div class="detail-section">
                <h3>AI 分析</h3>
                <p>该技术尚未进行 AI 分析</p>
                <button class="analyze-btn" onclick="analyzeTechnique('${technique.technique_id}')">
                    开始分析
                </button>
            </div>
        `;
    }
    
    // Atomic Tests
    if (technique.atomic_tests && technique.atomic_tests.length > 0) {
        html += `
            <div class="detail-section">
                <h3>原子测试 (${technique.atomic_tests.length})</h3>
        `;
        
        technique.atomic_tests.forEach((test, index) => {
            html += `
                <div class="atomic-test">
                    <h4>测试 ${test.test_number}: ${test.name || '未命名'}</h4>
                    <p>${test.description || '暂无描述'}</p>
                    <p><strong>支持平台:</strong> ${test.supported_platforms || 'N/A'}</p>
                    <p><strong>执行器:</strong> ${test.executor || 'N/A'}</p>
                    ${test.command ? `
                        <p><strong>命令:</strong></p>
                        <div class="code-block"><pre>${escapeHtml(test.command)}</pre></div>
                    ` : ''}
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function analyzeTechnique(techniqueId) {
    if (!window.event) {
        console.error('Event object not available');
        return;
    }
    
    const btn = window.event.target;
    btn.disabled = true;
    btn.textContent = '分析中...';
    
    fetch(`/api/techniques/${techniqueId}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('分析完成！');
            showTechniqueDetail(techniqueId);
            loadStats();
        } else {
            alert('分析失败: ' + (data.error || '未知错误'));
            btn.disabled = false;
            btn.textContent = '开始分析';
        }
    })
    .catch(error => {
        console.error('Error analyzing technique:', error);
        alert('分析失败，请重试。');
        btn.disabled = false;
        btn.textContent = '开始分析';
    });
}

// Sync
function syncTechniques() {
    if (!window.event) {
        console.error('Event object not available');
        return;
    }
    
    const btn = window.event.target;
    const statusDiv = document.getElementById('sync-status');
    const resultsDiv = document.getElementById('sync-results');
    
    btn.disabled = true;
    btn.textContent = '同步中...';
    statusDiv.className = 'sync-status loading';
    statusDiv.textContent = '正在从 Atomic Red Team 仓库同步数据，请稍候...';
    resultsDiv.innerHTML = '';
    
    fetch('/api/techniques/sync', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusDiv.className = 'sync-status success';
            statusDiv.textContent = `同步完成！成功同步 ${data.count} 个技术。`;
            
            if (data.synced.length > 0) {
                resultsDiv.innerHTML = `
                    <h3>同步成功:</h3>
                    <p>${data.synced.join(', ')}</p>
                `;
            }
            
            if (data.errors.length > 0) {
                resultsDiv.innerHTML += `
                    <h3>同步失败:</h3>
                    <ul>
                        ${data.errors.map(e => `<li>${e}</li>`).join('')}
                    </ul>
                `;
            }
            
            // Reload stats and techniques
            loadStats();
            if (document.getElementById('techniques-section').style.display !== 'none') {
                loadTechniques(1);
            }
        } else {
            statusDiv.className = 'sync-status error';
            statusDiv.textContent = '同步失败: ' + (data.error || '未知错误');
        }
        
        btn.disabled = false;
        btn.textContent = '同步数据';
    })
    .catch(error => {
        console.error('Error syncing techniques:', error);
        statusDiv.className = 'sync-status error';
        statusDiv.textContent = '同步失败，请重试。';
        btn.disabled = false;
        btn.textContent = '同步数据';
    });
}
