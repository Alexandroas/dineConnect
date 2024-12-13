function sortBusinesses(sortBy) {
    // Get current URL
    let url = new URL(window.location.href);
    
    // Update or add sort parameter
    url.searchParams.set('sort', sortBy);
    
    // Preserve the page parameter if it exists
    const currentPage = url.searchParams.get('page');
    if (currentPage) {
        url.searchParams.set('page', '1'); // Reset to first page when sorting
    }
    
    // Replace current URL with sorted version
    window.location.href = url.toString();
}

// Helper function to get rating
function getRating(businessElement) {
    const ratingText = businessElement.querySelector('.text-muted').innerText;
    const ratingMatch = ratingText.match(/\((\d+)\s+reviews\)/);
    return ratingMatch ? parseInt(ratingMatch[1]) : 0;
}

// Initialize sorting on page load
document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        // Set initial value based on URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const currentSort = urlParams.get('sort');
        if (currentSort) {
            sortSelect.value = currentSort;
        }
        
        sortSelect.addEventListener('change', function() {
            sortBusinesses(this.value);
        });
    }
});