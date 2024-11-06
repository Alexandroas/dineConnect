function togglePastReservations() {
    const content = document.getElementById("pastReservationsContent");
    const icon = document.getElementById("dropdownIcon");
    
    // Toggle collapse class
    content.classList.toggle("show");
    
    // Rotate icon
    icon.classList.toggle("rotate");
    
    // Add smooth height animation
    if (content.classList.contains("show")) {
        content.style.maxHeight = content.scrollHeight + "px";
    } else {
        content.style.maxHeight = "0px";
    }
}

// Add smooth scroll when clicking on anchors
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});