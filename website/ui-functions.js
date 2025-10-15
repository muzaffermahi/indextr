/**
 * UI Helper Functions for Academic Search Engine - DARK MODE MULTI-SOURCE EDITION
 * Because sometimes you need to separate your concerns like a civilized developer
 * instead of cramming everything into one massive HTML file like a digital barbarian
 * 
 * NOW WITH 100% MORE CHECKBOX CHAOS AND DARK MODE SUPREMACY
 */

/**
 * Creates an article card with proper action buttons based on source type
 * This function embodies the philosophical principle of "different sources, different UX"
 * Now with enhanced dark mode aesthetics because your retinas deserve respect
 * 
 * @param {Object} article - Article data from API
 * @returns {string} HTML string for the article card
 */
/*function createArticleCard(article) {
    const keywords = article.keywords && article.keywords !== 'N/A' && article.keywords !== 'No keywords' 
        ? article.keywords.split(',').map(k => k.trim()).slice(0, 5)
        : [];

    const keywordTags = keywords.length > 0 
        ? keywords.map(keyword => `<span class="keyword-tag">${keyword}</span>`).join('')
        : '';

    // Debug: Log what we're working with because transparency is beautiful
    console.log('Article data:', {
        source: article.source,
        thesis_id: article.thesis_id,
        url: article.url,
        title: article.title?.substring(0, 50)
    });

    // Generate the appropriate action button based on source type
    const actionButton = generateActionButton(article);

    return `
        <div class="article-card">
            <div class="article-title">${article.title}</div>
            ${article.authors && article.authors !== 'N/A' && article.authors !== 'Unknown Author'
                ? `<div class="article-authors">👥 ${article.authors}</div>` 
                : ''}
            <div class="article-meta">
                📅 ${article.publication_date || 'Unknown date'}
                ${article.volume && article.volume !== 'N/A' ? ` • Vol. ${article.volume}` : ''}
                ${article.issue && article.issue !== 'N/A' ? ` Issue ${article.issue}` : ''}
                ${article.thesis_id ? ` • Thesis ID: ${article.thesis_id}` : ''}
                • Source: ${article.source || 'Unknown'}
            </div>
            ${keywordTags ? `<div class="article-keywords">${keywordTags}</div>` : ''}
            <div class="article-actions">${actionButton}</div>
        </div>
    `;
}
*/
/**
 * Generates the appropriate action button based on article source
 * Because YÖK Tez, Dergipark, and TR Dizin live in different UX universes
 * Updated to handle our new TR Dizin overlord
 * 
 * @param {Object} article - Article data
 * @returns {string} HTML for the action button
 */
function generateActionButton(article) {
    // Check if this is YÖK Tez (multiple detection strategies because bureaucracy is chaos)
    const isYokTez = article.source && article.source.includes('YÖK Tez') || 
                     article.thesis_id || 
                     article.journal_slug === 'yoktez';
    
    // Check if this is TR Dizin (the new kid on the academic block)
    const isTRDizin = article.source && (
        article.source.includes('TRDizin') || 
        article.source.includes('TR Dizin') ||
        article.journal_slug === 'trdizin'
    );
    
    if (isYokTez) {
        // YÖK Tez - Copy ID button because their website is a JavaScript hellscape
        const thesisId = article.thesis_id || 'unknown';
        return `<button class="copy-id-btn" onclick="copyThesisId('${thesisId}')">📋 Copy ID: ${thesisId}</button>`;
    } else if (isTRDizin && article.doi) {
        // TR Dizin - DOI link because they actually believe in standards
        return `<a href="https://doi.org/${article.doi}" target="_blank" class="article-link">🔗 View DOI</a>`;
    } else if (article.url) {
        // Dergipark or others - Normal view article link because they believe in functional URLs
        return `<a href="${article.url}" target="_blank" class="article-link">📄 View Article</a>`;
    } else {
        // Fallback for mysterious edge cases
        return `<div class="no-action">No direct link available</div>`;
    }
}

/**
 * Copy thesis ID to clipboard with visual feedback
 * Because YÖK Tez forces us to be creative about accessing content
 * 
 * @param {string} thesisId - The thesis ID to copy
 */
function copyThesisId(thesisId) {
    navigator.clipboard.writeText(thesisId).then(function() {
        // Visual feedback for successful copy
        const buttons = document.querySelectorAll(`button[onclick="copyThesisId('${thesisId}')"]`);
        buttons.forEach(button => {
            const originalText = button.textContent;
            button.textContent = '✅ ID Copied!';
            button.classList.add('copy-success');
            
            // Reset after 2 seconds because sustained visual feedback is annoying
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('copy-success');
            }, 2000);
        });
    }).catch(function(err) {
        // Fallback for older browsers or permission issues
        console.error('Could not copy text: ', err);
        alert(`Thesis ID: ${thesisId}\n\nCopy this ID manually to search on YÖK Tez website.`);
    });
}

/**ƒ
 * Creates a source section with results
 * Because organizing results by source makes users happy
 * 
 * @param {string} title - Section title
 * @param {Array} results - Array of article objects
 * @returns {string} HTML for the source section
 */
function createSourceSection(title, results) {
    let html = `<div class="source-results">
        <h3 class="source-title">${title} (${results.length})</h3>`;

    results.forEach(result => {
        html += createArticleCard(result);
    });

    html += '</div>';
    return html;
}

/**
 * Creates a collapsible source section with expandable results
 * Because information hierarchy is basically digital feng shui
 * Now with enhanced dark mode styling that doesn't burn your retinas
 */
function createCollapsibleSourceSection(title, results, sourceType) {
    const sectionId = `section-${sourceType}`;
    const contentId = `content-${sourceType}`;
    
    let html = `
        <div class="source-results collapsible-section" id="${sectionId}">
            <div class="source-header" onclick="toggleSection('${contentId}', '${sectionId}')">
                <h3 class="source-title">
                    <span class="expand-icon" id="icon-${contentId}">▶</span>
                    ${title} 
                    <span class="result-count">(${results.length} sonuç)</span>
                </h3>
            </div>
            <div class="source-content collapsed" id="${contentId}">
    `;

    // Add all results to the collapsible content
    results.forEach(result => {
        html += createArticleCard(result);
    });

    html += `
            </div>
        </div>
    `;
    
    return html;
}

/**
 * Toggle section expansion/collapse with beautiful animations
 * This is where the accordion magic happens
 */
function toggleSection(contentId, sectionId) {
    const content = document.getElementById(contentId);
    const icon = document.getElementById(`icon-${contentId}`);
    const section = document.getElementById(sectionId);
    
    if (content.classList.contains('collapsed')) {
        // EXPAND THE SECTION
        content.classList.remove('collapsed');
        content.classList.add('expanded');
        icon.textContent = '▼';
        section.classList.add('active');
        
        // Smooth scroll to section if it's not fully visible
        setTimeout(() => {
            if (!isElementInViewport(section)) {
                section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }, 300);
        
    } else {
        // COLLAPSE THE SECTION
        content.classList.remove('expanded');
        content.classList.add('collapsed');
        icon.textContent = '▶';
        section.classList.remove('active');
    }
}

/**
 * Check if element is in viewport for smooth scrolling decisions
 */
function isElementInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * COMPLETELY REWRITTEN displayResults function for the new multi-source checkbox reality
 * This function now handles the beautiful chaos of user-selected source combinations
 * No more dropdown tyranny - we live in a checkbox democracy now!
 */
function displayResults(data, keyword, requestedSources) {
    console.log("🎯 displayResults called with:", { data, keyword, requestedSources });
    console.log("🔍 Raw data structure:", JSON.stringify(data, null, 2));
    
    const resultsSection = document.getElementById('resultsSection');
    const resultsTitle = document.getElementById('resultsTitle');
    const resultsMeta = document.getElementById('resultsMeta');
    const resultsContent = document.getElementById('resultsContent');
    
    // Clear previous results
    resultsContent.innerHTML = '';
    
    // DEFENSIVE VALIDATION - Because trust no one, not even your own backend
    if (!data) {
        console.error("💥 No data received");
        showError('No data received from API');
        return;
    }
    
    // Handle different response formats because your backend is inconsistent as fuck
    let sources = {};
    
    if (data.sources) {
        // Standard format: { sources: { dergipark: { results: [...] } } }
        sources = data.sources;
        console.log("✅ Standard format detected");
    } else if (data.results && Array.isArray(data.results)) {
        // Direct results format: { results: [...] }
        console.log("🔧 Converting direct results format");
        const sourceType = requestedSources?.[0] || 'unknown';
        sources[sourceType] = {
            results: data.results,
            total_results: data.results.length,
            search_type: 'direct'
        };
    } else if (data.dergipark_results || data.trdizin_results || data.yoktez_results) {
        // Legacy format: { dergipark_results: [...], trdizin_results: [...] }
        console.log("🔧 Converting legacy format");
        if (data.dergipark_results) {
            sources.dergipark = { results: data.dergipark_results };
        }
        if (data.trdizin_results) {
            sources.trdizin = { results: data.trdizin_results };
        }
        if (data.yoktez_results) {
            sources.yoktez = { results: data.yoktez_results };
        }
    } else {
        console.error("💥 Unrecognized data format:", Object.keys(data));
        console.error("🔍 Full data:", data);
        showError('Unrecognized response format from API');
        return;
    }
    
    // Log what we found
    const availableSources = Object.keys(sources);
    console.log("📊 Available sources:", availableSources);
    
    // Count total results
    let totalResults = 0;
    availableSources.forEach(source => {
        const sourceData = sources[source];
        const resultsCount = sourceData?.results?.length || 0;
        totalResults += resultsCount;
        console.log(`  ${source}: ${resultsCount} results`);
    });
    
    console.log(`📈 Total results: ${totalResults}`);
    
    // Update header
    resultsTitle.textContent = `"${keyword}" için arama sonuçları`;
    resultsMeta.innerHTML = `
        ${totalResults} sonuç bulundu • 
        Kaynak${availableSources.length > 1 ? 'lar' : ''}: ${availableSources.join(', ')} • 
        Alaka seviyesi: ${data.similarity_threshold || 'Bilinmiyor'}
    `;
    
    // Handle no results
    if (totalResults === 0) {
        console.warn("⚠️ No results found");
        resultsContent.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <h3>Hiç sonuç bulunamadı</h3>
                <p>"${keyword}" için herhangi bir sonuç bulunamadı.</p>
                <div class="search-suggestions">
                    <h4>Öneriler:</h4>
                    <ul>
                        <li>Daha genel terimler kullanın</li>
                        <li>Alaka seviyesini düşürün</li>
                        <li>Farklı kaynaklar seçin</li>
                    </ul>
                </div>
            </div>
        `;
        resultsSection.style.display = 'block';
        return;
    }
    
    // Create expand/collapse controls
    if (availableSources.length > 1) {
        const controlsHtml = `
            <div style="margin-bottom: 20px;">
                <button class="expand-all-btn" onclick="expandAll()">Tümünü Aç</button>
                <button class="collapse-all-btn" onclick="collapseAll()">Tümünü Kapat</button>
            </div>
        `;
        resultsContent.innerHTML = controlsHtml;
    }
    
    // Create sections for each source
    availableSources.forEach(sourceName => {
        const sourceData = sources[sourceName];
        const results = sourceData?.results || [];
        
        if (results.length === 0) {
            console.log(`⏭️ Skipping ${sourceName} - no results`);
            return;
        }
        
        console.log(`🔨 Creating section for ${sourceName}: ${results.length} results`);
        
        // Create source section
        const sourceSection = createSourceSection(sourceName, results, sourceData.search_type);
        resultsContent.appendChild(sourceSection);
    });
    
    // Show results
    resultsSection.style.display = 'block';
    
    console.log("✅ displayResults completed successfully");
}


function createSourceSection(sourceName, results, searchType) {
    console.log(`🔧 Creating source section for: ${sourceName} (${results.length} results)`);
    
    // Source name mapping for display
    const sourceNames = {
        'dergipark': '📚 Dergipark',
        'trdizin': '🇹🇷 TR Dizin', 
        'yoktez': '🎓 YÖK Tez'
    };
    
    const displayName = sourceNames[sourceName] || sourceName;
    
    // Create collapsible section
    const section = document.createElement('div');
    section.className = 'collapsible-section active';
    section.id = `source-${sourceName}`;
    
    // Create header
    const header = document.createElement('div');
    header.className = 'source-header';
    header.onclick = () => toggleSection(`content-${sourceName}`, `source-${sourceName}`);
    
    header.innerHTML = `
        <h3 class="source-title">
            <span class="expand-icon" id="icon-content-${sourceName}">▼</span>
            ${displayName}
            <span class="result-count">${results.length} sonuç</span>
        </h3>
    `;
    
    // Create content container
    const content = document.createElement('div');
    content.className = 'source-content expanded';
    content.id = `content-${sourceName}`;
    
    // Add results to content
    results.forEach((result, index) => {
        const articleCard = createArticleCard(result, sourceName, index);
        content.appendChild(articleCard);
    });
    
    section.appendChild(header);
    section.appendChild(content);
    
    console.log(`✅ Created section for ${sourceName}`);
    
    return section;
}

function createArticleCard(article, source, index) {
    const card = document.createElement('div');
    card.className = 'article-card';
    
    // Handle different article structures
    const title = article.title || 'Başlık bulunamadı';
    const authors = article.authors || 'Bilinmeyen yazar';
    const year = article.publication_date || article.year || 'Bilinmeyen tarih';
    const keywords = article.keywords || 'Anahtar kelime yok';
    const url = article.url || '#';
    
    // Create similarity score display if available
    let scoreHtml = '';
    if (article.similarity_score) {
        const scorePercent = Math.round(article.similarity_score * 100);
        scoreHtml = `<div style="color: #58a6ff; font-size: 0.9em; margin-bottom: 8px;">🎯 Benzerlik: %${scorePercent}</div>`;
    }
    
    // Create different action based on source
    let actionHtml = '';
    if (url && url !== '#') {
        actionHtml = `<a href="${url}" target="_blank" class="article-link">📖 Makaleyi Aç</a>`;
    } else if (article.article_id) {
        actionHtml = `<button class="copy-id-btn" onclick="copyToClipboard('${article.article_id}')">📋 ID Kopyala</button>`;
    } else {
        actionHtml = `<div class="no-action">Bağlantı mevcut değil</div>`;
    }
    
    card.innerHTML = `
        ${scoreHtml}
        <div class="article-title">${title}</div>
        <div class="article-authors">👤 ${authors}</div>
        <div class="article-meta">📅 ${year}</div>
        <div class="article-meta">🏷️ ${keywords}</div>
        ${actionHtml}
    `;
    
    return card;
}

/**
 * Shows the results section
 */
function showResults() {
    document.getElementById('resultsSection').style.display = 'block';
}

/**
 * Expand all sections for users who want to see everything
 */
function expandAll() {
    const collapsedSections = document.querySelectorAll('.source-content.collapsed');
    collapsedSections.forEach(section => {
        const contentId = section.id;
        const sectionId = contentId.replace('content-', 'source-');
        toggleSection(contentId, sectionId);
    });
}

/**
 * Collapse all sections for clean overview
 */
function collapseAll() {
    const expandedSections = document.querySelectorAll('.source-content.expanded');
    expandedSections.forEach(section => {
        const contentId = section.id;
        const sectionId = contentId.replace('content-', 'source-');
        toggleSection(contentId, sectionId);
    });
}

// LOADING FUNCTIONS - Now with enhanced Turkish entertainment and dark mode aesthetics

const loadingEmojis = [
    '🔍', '📚', '🎓', '⚡', '🚀', '📖', '🔬', '💡',
    '🎯', '🔥', '🎸', '🗂️', '📊', '🎭', '🧠', '⭐'
];

// Enhanced Turkish loading messages with more personality
const turkishLoadingMessages = [
    "Sıkı Tutun! O kadar şeyi taramak kolay değil..",
    "Bekleyin! Akademik hazineleri çıkarıyoruz..",
    "Durun! Binlerce makaleyi tarıyoruz..",
    "Sabır! En iyi sonuçları buluyoruz..",
    "Hazır olun! Bilgisel sihir yapıyoruz..",
    "Bekleyin! Türk akademisini keşfediyoruz..",
    "Durun! Araştırma ruhlarını çağırıyoruz..",
    "Sıkı Tutun! Bilimsel keşifler geliyor..",
    "Sabır! Akademik gizleri çözüyoruz..",
    "Hazır olun! Dergipark'ı fethediyoruz..",
    "Bekleyin! YÖK Tez arşivini tarıyoruz..",
    "Durun! TR Dizin hazinelerini açıyoruz..",
    "Sıkı Tutun! Araştırma süper güçleri aktif..",
    "Sabır! Akademik büyü demleniyoruz..",
    "Hazır olun! Veri sihirbazlığı başlıyor..",
    "Bekleyin! Bilimsel aydınlanma yükleniyor..",
    "Durun! Türkiye'nin akademik gücünü topluyoruz..",
    "Sıkı Tutun! Binlerce yayını analiz ediyoruz..",
    "Sabır! En değerli bulgular seçiliyor..",
    "Hazır olun! Akademik macera başlıyor..",
    "Bekleyin! Checkbox'lar sihir yapıyor..",
    "Durun! Dark mode'da arama yapıyoruz..",
    "Sıkı Tutun! Çoklu kaynak koordinasyonu.."
];

let emojiInterval;
let messageInterval;

function startDynamicLoading() {
    const emojiSpinner = document.getElementById('emojiSpinner');
    const loadingText = document.getElementById('loadingText');
    
    let emojiIndex = 0;
    let messageIndex = 0;
    loadingText.textContent = turkishLoadingMessages[0];
    emojiSpinner.textContent = loadingEmojis[0];
    
    // Change emoji every 800ms for maximum visual entertainment
    emojiInterval = setInterval(() => {
        emojiIndex = (emojiIndex + 1) % loadingEmojis.length;
        emojiSpinner.textContent = loadingEmojis[emojiIndex];
    }, 800);
    
    // Change Turkish message every 2.5 seconds for linguistic variety
    messageInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % turkishLoadingMessages.length;
        loadingText.textContent = turkishLoadingMessages[messageIndex];
        
        // Add a subtle fade effect for smooth transitions
        loadingText.style.opacity = '0.7';
        setTimeout(() => {
            loadingText.style.opacity = '1';
        }, 200);
    }, 2500);
}

function stopDynamicLoading() {
    if (emojiInterval) clearInterval(emojiInterval);
    if (messageInterval) clearInterval(messageInterval);
    
    // Reset to original state
    const loadingText = document.getElementById('loadingText');
    loadingText.style.opacity = '1';
}

// Updated loading functions to work with the new form system
function showLoading() {
    const searchBtn = document.getElementById('searchBtn');
    const loading = document.getElementById('loading');
    
    searchBtn.disabled = true;
    searchBtn.textContent = 'Arıyor...';
    loading.style.display = 'block';
    startDynamicLoading(); // START THE TURKISH ENTERTAINMENT SHOW
}

function hideLoading() {
    const searchBtn = document.getElementById('searchBtn');
    const loading = document.getElementById('loading');
    
    searchBtn.disabled = false;
    searchBtn.textContent = '🔍 Ara';
    loading.style.display = 'none';
    stopDynamicLoading(); // STOP THE MOTIVATIONAL CAROUSEL
}

/**
 * Shows error message in results area with dark mode styling
 * @param {string} message - Error message to display
 */
function showError(message) {
    const resultsContent = document.getElementById('resultsContent');
    const resultsTitle = document.getElementById('resultsTitle');
    const resultsMeta = document.getElementById('resultsMeta');
    
    resultsContent.innerHTML = `<div class="error-message">💀 ${message}</div>`;
    resultsTitle.textContent = 'Hata Oluştu';
    resultsMeta.textContent = '';
    showResults();
}

// Export functions for use in main application
// (This would be for a proper module system, but for HTML includes just make sure functions are global)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createArticleCard,
        generateActionButton,
        copyThesisId,
        createSourceSection,
        createCollapsibleSourceSection,
        displayResults,
        showResults,
        showError,
        showLoading,
        hideLoading,
        expandAllSections,
        collapseAllSections,
        toggleSection
    };
}
