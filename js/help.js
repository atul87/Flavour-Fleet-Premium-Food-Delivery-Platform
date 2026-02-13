function switchTab(tab) {
    // Update tabs
    document.querySelectorAll('.help-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    // Update content
    document.querySelectorAll('.faq-section').forEach(s => s.classList.remove('active'));
    document.getElementById(`${tab}-faq`).classList.add('active');
}

document.addEventListener('DOMContentLoaded', () => {
    // Accordion Logic
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', () => {
            const item = question.parentElement;

            // Close other items
            document.querySelectorAll('.faq-item').forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('open');
                    otherItem.querySelector('.faq-answer').style.maxHeight = null;
                }
            });

            // Toggle current item
            item.classList.toggle('open');
            const answer = item.querySelector('.faq-answer');
            if (item.classList.contains('open')) {
                answer.style.maxHeight = answer.scrollHeight + "px";
            } else {
                answer.style.maxHeight = null;
            }
        });
    });
});
