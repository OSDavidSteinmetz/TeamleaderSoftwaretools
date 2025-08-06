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

document.addEventListener('DOMContentLoaded', function() {
    // Alle Box-Elemente finden
    const boxes = document.querySelectorAll('.box');
    
    // Zu jedem Link in jeder Box einen Event-Listener hinzufügen
    boxes.forEach(box => {
        const link = box.querySelector('a');
        if (link) {
            link.addEventListener('click', function(e) {
                // Loader anzeigen (bestehender Code)
                const loader = document.getElementById('loader');
                loader.className = "loading";
                
                // Alle Boxen deaktivieren
                setTimeout(function() {
                    boxes.forEach(b => {
                        b.style.opacity = '0.6';
                        b.style.pointerEvents = 'none';
                    });
                    console.log('Alle Boxen deaktiviert');
                }, 100); // Kurzer Timeout, um die Navigation zu ermöglichen
            });
        }
    });
});