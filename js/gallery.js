/* ===== Gallery Page Logic ===== */
document.addEventListener('DOMContentLoaded', () => {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.gallery-card');
    const noResults = document.getElementById('no-results');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxTitle = document.getElementById('lightbox-title');
    const lightboxDesc = document.getElementById('lightbox-desc');
    const lightboxClose = document.getElementById('lightbox-close');
    const lightboxPrev = document.getElementById('lightbox-prev');
    const lightboxNext = document.getElementById('lightbox-next');

    let currentIndex = 0;
    let visibleCards = [...cards];

    // ===== FILTER =====
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            let visibleCount = 0;

            cards.forEach((card, i) => {
                const match = filter === 'all' || card.dataset.category === filter;
                card.style.display = match ? '' : 'none';
                if (match) {
                    visibleCount++;
                    // Stagger animation
                    card.style.animation = 'none';
                    card.offsetHeight; // Force reflow
                    card.style.animation = `fadeInUp 0.5s ease ${i * 0.05}s both`;
                }
            });

            // Update visible cards list for lightbox navigation
            visibleCards = [...cards].filter(c => c.style.display !== 'none');

            // Show/hide no results
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        });
    });

    // ===== LIGHTBOX =====
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const img = card.querySelector('img');
            const overlay = card.querySelector('.overlay-content');
            const title = overlay ? overlay.querySelector('h3')?.textContent : '';
            const desc = overlay ? overlay.querySelector('span')?.textContent : '';

            currentIndex = visibleCards.indexOf(card);
            openLightbox(img.src, title, desc);
        });
    });

    function openLightbox(src, title, desc) {
        lightboxImg.src = src;
        lightboxTitle.textContent = title;
        lightboxDesc.textContent = desc;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    function navigate(direction) {
        currentIndex += direction;
        if (currentIndex < 0) currentIndex = visibleCards.length - 1;
        if (currentIndex >= visibleCards.length) currentIndex = 0;

        const card = visibleCards[currentIndex];
        const img = card.querySelector('img');
        const overlay = card.querySelector('.overlay-content');
        const title = overlay ? overlay.querySelector('h3')?.textContent : '';
        const desc = overlay ? overlay.querySelector('span')?.textContent : '';

        // Animate transition
        lightboxImg.style.opacity = '0';
        lightboxImg.style.transform = 'scale(0.95)';
        setTimeout(() => {
            lightboxImg.src = img.src;
            lightboxTitle.textContent = title;
            lightboxDesc.textContent = desc;
            lightboxImg.style.opacity = '1';
            lightboxImg.style.transform = 'scale(1)';
        }, 200);
    }

    lightboxClose.addEventListener('click', closeLightbox);
    lightboxPrev.addEventListener('click', () => navigate(-1));
    lightboxNext.addEventListener('click', () => navigate(1));

    // Close on background click
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        if (!lightbox.classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') navigate(-1);
        if (e.key === 'ArrowRight') navigate(1);
    });

    // ===== ENTRANCE ANIMATION =====
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                entry.target.style.animation = `fadeInUp 0.6s ease ${i * 0.08}s both`;
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => observer.observe(card));
});

// fadeInUp keyframe (also defined here for standalone use)
if (!document.querySelector('#gallery-keyframes')) {
    const style = document.createElement('style');
    style.id = 'gallery-keyframes';
    style.textContent = `
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(30px); }
      to   { opacity: 1; transform: translateY(0); }
    }
  `;
    document.head.appendChild(style);
}
