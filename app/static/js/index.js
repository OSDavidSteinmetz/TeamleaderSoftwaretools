document.addEventListener('DOMContentLoaded', function() {
    // Alle <a>-Elemente selektieren
    const links = document.querySelectorAll('a');

    // Für jedes <a>-Element einen Event Listener hinzufügen
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const loader = document.getElementById('loader');
            loader.className = "loading";        });
    });
});
