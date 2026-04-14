// Rotating words
const words = ['AI', 'code', 'ML models', 'RAG pipelines', 'agents', 'ideas'];
const el = document.getElementById('rotateWord');
let i = 0;

setInterval(() => {
    el.style.opacity = 0;
    el.style.transform = 'translateY(8px)';
    setTimeout(() => {
        i = (i + 1) % words.length;
        el.textContent = words[i];
        el.style.opacity = 1;
        el.style.transform = 'translateY(0)';
    }, 300);
}, 2200);

// Count items in grids and display counts
function updateSectionCounts() {
    const writingGrid = document.querySelector('.blog-grid');
    const modelsGrid = document.querySelector('.model-grid');
    
    if (writingGrid) {
        const blogCount = writingGrid.querySelectorAll('.blog-card').length;
        const writingCountEl = document.getElementById('writingCount');
        if (writingCountEl) {
            writingCountEl.textContent = `${blogCount} ${blogCount === 1 ? 'article' : 'articles'} total`;
        }
    }
    
    if (modelsGrid) {
        const modelCount = modelsGrid.querySelectorAll('.model-card').length;
        const modelsCountEl = document.getElementById('modelsCount');
        if (modelsCountEl) {
            modelsCountEl.textContent = `${modelCount} ${modelCount === 1 ? 'model' : 'models'} total`;
        }
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', updateSectionCounts);
// Also call after a short delay to catch dynamically loaded content
setTimeout(updateSectionCounts, 500);

// Terminal typewriter
(function terminal() {
    const el = document.getElementById('termText');
    if (!el) return;
    const lines = [
        'whoami',
        'python build.py --stack ai+fullstack',
        'deploy rag-pipeline --vector pinecone',
        'run agent --graph langgraph',
        'git commit -m "ship it"'
    ];
    let li = 0, ci = 0, deleting = false;

    function tick() {
        const line = lines[li];
        if (!deleting) {
            ci++;
            el.textContent = line.slice(0, ci);
            if (ci >= line.length) {
                deleting = true;
                setTimeout(tick, 1500);
                return;
            }
        } else {
            ci--;
            el.textContent = line.slice(0, ci);
            if (ci <= 0) {
                deleting = false;
                li = (li + 1) % lines.length;
            }
        }
        setTimeout(tick, deleting ? 22 : 55 + Math.random() * 40);
    }
    tick();
})();

// Scroll fade-in
const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });

document.querySelectorAll(
    '.about-row, .about-stats, .pill-group, .journey-card, .edu-chip, .connect-section, .blog-card, .model-card, .section-sub, .section-more'
).forEach(el => {
    el.classList.add('fade-up');
    observer.observe(el);
});

// Stagger cards
document.querySelectorAll('.journey-card').forEach((c, i) => {
    c.style.transitionDelay = `${i * 0.1}s`;
});
document.querySelectorAll('.pill-group').forEach((c, i) => {
    c.style.transitionDelay = `${i * 0.08}s`;
});
document.querySelectorAll('.blog-card').forEach((c, i) => {
    c.style.transitionDelay = `${(i % 3) * 0.08}s`;
});
document.querySelectorAll('.model-card').forEach((c, i) => {
    c.style.transitionDelay = `${i * 0.1}s`;
});
