// Rotating words
const words = ['AI', 'code', 'ML models', 'pipelines', 'bots', 'ideas'];
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

// Scroll fade-in
const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });

document.querySelectorAll(
    '.about-row, .about-stats, .pill-group, .journey-card, .edu-chip, .connect-section'
).forEach(el => {
    el.classList.add('fade-up');
    observer.observe(el);
});

// Stagger journey cards
document.querySelectorAll('.journey-card').forEach((c, i) => {
    c.style.transitionDelay = `${i * 0.1}s`;
});
document.querySelectorAll('.pill-group').forEach((c, i) => {
    c.style.transitionDelay = `${i * 0.08}s`;
});
