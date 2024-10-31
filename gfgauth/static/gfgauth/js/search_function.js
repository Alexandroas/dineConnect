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
