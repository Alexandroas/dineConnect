
    function toggleFavorite(button) {
        button.classList.toggle('active');
        const icon = button.querySelector('i');
        if (button.classList.contains('active')) {
            icon.classList.remove('bi-heart');
            icon.classList.add('bi-heart-fill');
        } else {
            icon.classList.remove('bi-heart-fill');
            icon.classList.add('bi-heart');
        }
    }

    // Search functionality
    document.getElementById('searchInput').addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const cards = document.querySelectorAll('.business-card');
        
        cards.forEach(card => {
            const businessName = card.querySelector('.business-name').textContent.toLowerCase();
            const businessInfo = card.querySelector('.business-info').textContent.toLowerCase();
            
            if (businessName.includes(searchTerm) || businessInfo.includes(searchTerm)) {
                card.closest('.col').style.display = '';
            } else {
                card.closest('.col').style.display = 'none';
            }
        });
    });
