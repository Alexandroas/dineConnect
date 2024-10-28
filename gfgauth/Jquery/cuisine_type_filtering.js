function filterByCuisineType() {
    const selectedCuisine = document.getElementById('cuisineTypeSearch').value.toLowerCase();
    console.log('Selected cuisine:', selectedCuisine);

    const restaurantCards = document.querySelectorAll('.cuisine_type_filter');
    console.log('Total cards found:', restaurantCards.length);

    restaurantCards.forEach(card => {
        const cardCuisines = card.dataset.cuisines ? card.dataset.cuisines.split(',') : [];
        console.log('Card cuisines:', cardCuisines);

        // Get the parent column element
        const columnElement = card.closest('.col');

        if (selectedCuisine === 'all') {
            columnElement.style.display = '';  // Show the column
            console.log('Showing all cards');
        } else {
            if (cardCuisines.includes(selectedCuisine)) {
                columnElement.style.display = '';  // Show the column
                console.log('Showing card with cuisine:', selectedCuisine);
            } else {
                columnElement.style.display = 'none';  // Hide the column
                console.log('Hiding card. Card does not have cuisine:', selectedCuisine);
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Script loaded');
    const select = document.getElementById('cuisineTypeSearch');
    console.log('Select element:', select);
    
    if (select) {
        select.addEventListener('change', filterByCuisineType);
    }
});