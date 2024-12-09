document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const restaurantGrid = document.querySelector('.restaurants-grid .row');
    const paginationNav = document.querySelector('nav[aria-label="Restaurant navigation"]');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            
            if (searchTerm.length >= 2) {
                // Make AJAX request for search
                fetch(`/?search=${encodeURIComponent(searchTerm)}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Hide pagination during search
                    if (paginationNav) paginationNav.style.display = 'none';
                    
                    // Clear existing grid
                    restaurantGrid.innerHTML = '';
                    
                    // Add search results
                    data.businesses.forEach(business => {
                        restaurantGrid.innerHTML += `
                            <div class="col">
                                <div class="card h-100 border-0 shadow-sm hover-shadow cuisine_type_filter" data-cuisines="${business.cuisine.toLowerCase()}">
                                    <a href="{% url 'Restaurant_handling:restaurant_detail' %}${business.id}" class="text-decoration-none">
                                        <div class="position-relative">
                                            <img src="${business.image_url || '/api/placeholder/400/320'}" 
                                                 alt="${business.name}" 
                                                 class="card-img-top object-fit-cover" 
                                                 style="height: 200px;" />
                                        </div>
                                        <div class="card-body">
                                            <h5 class="card-title mb-3">${business.name}</h5>
                                            <div class="mb-3">
                                                <span class="badge">${business.cuisine}</span>
                                                <div class="mt-2">
                                                    <span class="text-warning">
                                                        ${getStarRating(business.average_rating)}
                                                    </span>
                                                    <small class="text-muted ms-2">(${business.review_count} reviews)</small>
                                                </div>
                                            </div>
                                            <ul class="list-unstyled text-muted small">
                                                <li class="mb-2"><i class="fas fa-user me-2"></i>${business.owner}</li>
                                                <li class="mb-2"><i class="fas fa-map-marker-alt me-2"></i>${business.address}</li>
                                                <li><i class="fas fa-phone me-2"></i>${business.contact}</li>
                                            </ul>
                                        </div>
                                    </a>
                                </div>
                            </div>
                        `;
                    });
                })
                .catch(error => {
                    console.error('Search error:', error);
                });
            } else if (searchTerm.length === 0) {
                // Restore original pagination view
                window.location.reload();
            }
        }, 300));
    }
});

function getStarRating(rating) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        stars += `<i class="fas fa-star${i <= rating ? '' : '-o'}"></i>`;
    }
    return stars;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}