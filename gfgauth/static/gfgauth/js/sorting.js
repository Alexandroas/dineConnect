// sorting.js
function sortBusinesses(sortBy) {
    console.log("Initiated sorting");
    const container = document.querySelector('.row.row-cols-1.row-cols-md-2.row-cols-lg-3');
    const businesses = Array.from(container.getElementsByClassName('col'));

    businesses.sort((a, b) => {
        switch(sortBy) {
            case 'name':
                console.log("Sorting by name:" + sortBy);
                const nameA = a.querySelector('.card-title').innerText.toLowerCase();
                console.log("Name A:" + nameA);
                const nameB = b.querySelector('.card-title').innerText.toLowerCase();
                console.log("Name B:" + nameB);
                return nameA.localeCompare(nameB);
            
            case 'name-desc':
                const nameDescA = a.querySelector('.card-title').innerText.toLowerCase();
                const nameDescB = b.querySelector('.card-title').innerText.toLowerCase();
                return nameDescB.localeCompare(nameDescA);
            
            case 'rating':
                const ratingA = getRating(a);
                const ratingB = getRating(b);
                return ratingA - ratingB; // Sort high to low
                
            default:
                return 0;
        }
    });

    // Clear and re-append sorted items
    businesses.forEach(business => {
        container.appendChild(business);
    });
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
        sortSelect.addEventListener('change', function() {
            sortBusinesses(this.value);
        });
    }
});