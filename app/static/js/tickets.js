document.addEventListener('DOMContentLoaded', function() {
    const tickets = document.querySelectorAll('.ticket');
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const closeBtn = document.getElementsByClassName('close')[0];
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    let currentImageIndex = 0;
    let currentImages = [];

    tickets.forEach(ticket => {
        ticket.addEventListener('click', function(e) {
            if (!e.target.closest('.status-form') && !e.target.closest('.ticket-images')) {
                this.classList.toggle('active');
            }
        });

        const form = ticket.querySelector('.status-form');
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const status = form.querySelector('select[name="status"]').value;
            const ticketId = ticket.getAttribute('data-id');

            fetch(`/update_status/${ticketId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: status })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === 'Status aktualisiert') {
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });

        const images = ticket.querySelectorAll('.ticket-images img');
        images.forEach((img, index) => {
            img.addEventListener('click', function(e) {
                e.stopPropagation();
                currentImages = Array.from(images);
                currentImageIndex = index;
                showModal(this.src);
            });
        });
    });

    function showModal(src) {
        modal.style.display = 'block';
        modalImg.src = src;
    }

    function showPrevImage() {
        currentImageIndex = (currentImageIndex - 1 + currentImages.length) % currentImages.length;
        modalImg.src = currentImages[currentImageIndex].src;
    }

    function showNextImage() {
        currentImageIndex = (currentImageIndex + 1) % currentImages.length;
        modalImg.src = currentImages[currentImageIndex].src;
    }

    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }

    prevBtn.onclick = showPrevImage;
    nextBtn.onclick = showNextImage;

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    // Tastaturnavigation hinzufügen
    document.addEventListener('keydown', function(e) {
        if (modal.style.display === 'block') {
            if (e.key === 'ArrowLeft') {
                showPrevImage();
            } else if (e.key === 'ArrowRight') {
                showNextImage();
            } else if (e.key === 'Escape') {
                modal.style.display = 'none';
            }
        }
    });
});

function deleteTicket(ticketId) {
    fetch(`/delete_ticket/${ticketId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Ticket gelöscht') {
            // Seite neu laden, um das gelöschte Ticket zu entfernen
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function filterTable() {
  var input, filter, table, div, ticket, i, txtValue;
  input = document.getElementById("searchField");
  filter = input.value.toUpperCase();
  table = document.getElementById("ticketsview");
  div = table.getElementsByClassName("ticket");

  for (i = 0; i < div.length; i++) {
    ticket = div[i];  // Jedes einzelne Ticket-Div
    txtValue = ticket.textContent || ticket.innerText;

    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      ticket.style.display = "";  // Zeige das Ticket an, wenn der Filter übereinstimmt
    } else {
      ticket.style.display = "none";  // Verstecke das Ticket, wenn es nicht übereinstimmt
    }
  }
}


function clearSearch() {
  document.getElementById("searchField").value = "";
  filterTable();
}

function archiveTickets() {
    // Eine POST-Anfrage an die /archive_closed_tickets Route senden, um alle geschlossenen Tickets zu archivieren
    fetch(`/archive_closed_tickets`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message.includes('Ticket(s) wurden archiviert')) {
            // Optional: Seite neu laden, um den aktualisierten Status anzuzeigen
            window.location.reload();
        } else {
            console.log(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


/**
 * Startet den Download der Tickets-Datei.
 */
function downloadTickets() {
    window.location.href = '/download-tickets';
}
