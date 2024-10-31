function filterByCuisineType() {
    const selectedCuisine = document.getElementById('cuisineTypeSearch').value.toLowerCase();
    console.log('Selected cuisine:', selectedCuisine);

    const restaurantCards = document.querySelectorAll('.cuisine_type_filter');
    console.log('Total cards found:', restaurantCards.length);

    restaurantCards.forEach(card => {
        // Get the cuisines from the data attribute and convert to array
        let cardCuisines = card.dataset.cuisines || '';
        console.log('Raw card cuisines:', cardCuisines);
        
        // Split by comma and trim whitespace
        cardCuisines = cardCuisines.split(',').map(cuisine => cuisine.trim().toLowerCase());
        console.log('Processed card cuisines:', cardCuisines);

        // Get the parent column element
        const columnElement = card.closest('.col');

        if (selectedCuisine === 'all') {
            columnElement.style.display = '';
            console.log('Showing all cards');
        } else {
            if (cardCuisines.includes(selectedCuisine)) {
                columnElement.style.display = '';
                console.log('Showing card with matching cuisine:', selectedCuisine);
            } else {
                columnElement.style.display = 'none';
                console.log('Hiding card - no matching cuisine');
            }
        }
    });
}

// Debug function to check initial state
function debugCuisineData() {
    console.log('=== Debugging Cuisine Data ===');
    
    // Check select options
    const select = document.getElementById('cuisineTypeSearch');
    const options = Array.from(select.options).map(opt => ({
        value: opt.value,
        text: opt.text
    }));
    console.log('Available cuisine options:', options);
    
    // Check all restaurant cards
    const cards = document.querySelectorAll('.cuisine_type_filter');
    cards.forEach((card, index) => {
        console.log(`Restaurant ${index + 1}:`, {
            cuisines: card.dataset.cuisines,
            cuisineArray: card.dataset.cuisines.split(',').map(c => c.trim().toLowerCase())
        });
    });
}

// Add event listeners when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Script loaded');
    
    // Run initial debug
    debugCuisineData();
    
    // Add event listener to select
    const select = document.getElementById('cuisineTypeSearch');
    if (select) {
        select.addEventListener('change', filterByCuisineType);
    } else {
        console.error('Cuisine type select element not found!');
    }
});