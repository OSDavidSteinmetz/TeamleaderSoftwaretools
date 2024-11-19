let initialCheckboxValues = {};
let initialNumberValues = {};

document.addEventListener("DOMContentLoaded", (event) => {
  const checkboxes = document.querySelectorAll(
    '#userTable input[type="checkbox"]'
  );
  const numberInputs = document.querySelectorAll(
    '#userTable input[type="number"]'
  );

  checkboxes.forEach((checkbox) => {
    const key = `${checkbox.dataset.employee}-${checkbox.dataset.permission}`;
    initialCheckboxValues[key] = checkbox.checked;
  });

  numberInputs.forEach((input) => {
    const employee = input.dataset.employee;
    const field = input.dataset.permission;
    if (!initialNumberValues[employee]) {
      initialNumberValues[employee] = {};
    }
    initialNumberValues[employee][field] = input.valueAsNumber;
  });
});

function openModal() {
  var modal = document.getElementById("myModal");
  modal.style.display = "flex";
}

function closeModal() {
  var modal = document.getElementById("myModal");
  modal.style.display = "none";
}

function uploadTimes() {
  clearData();
  closeModal();
  var csvContentDiv = document.getElementById("csvContent");
  csvContentDiv.innerHTML =
    '<p class="success-message">Die Zeiten wurden erfolgreich hochgeladen!</p>';
}

function filterTable() {
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("searchField");
  filter = input.value.toUpperCase();
  table = document.getElementById("userTable");
  tr = table.getElementsByTagName("tr");

  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}

function clearSearch() {
  document.getElementById("searchField").value = "";
  filterTable();
}

function changeAuthorizations() {
  const saveButton = document.getElementById("save-button");
  saveButton.disabled = false;
}

function downloadToken() {
  window.location.href = "/download-token";
}

function saveChanges() {
  const checkboxes = document.querySelectorAll(
    '#userTable input[type="checkbox"]'
  );
  const numberInputs = document.querySelectorAll(
    '#userTable input[type="number"]'
  );
  let changes = {};

  checkboxes.forEach((checkbox) => {
    const employee = checkbox.dataset.employee;
    const permission = checkbox.dataset.permission;
    const key = `${employee}-${permission}`;
    if (checkbox.checked !== initialCheckboxValues[key]) {
      if (!changes[employee]) {
        changes[employee] = {};
      }
      changes[employee][permission] = checkbox.checked;
    }
  });

  numberInputs.forEach((input) => {
    const employee = input.dataset.employee;
    const field = input.dataset.permission;
    if (input.valueAsNumber !== initialNumberValues[employee][field]) {
      if (!changes[employee]) {
        changes[employee] = {};
      }
      changes[employee][field] = input.valueAsNumber;
    }
  });

  // Nur weitermachen, wenn es tatsächlich Änderungen gibt
  if (Object.keys(changes).length > 0) {
    fetch("/save_changes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(changes),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          showMessage("Änderungen erfolgreich gespeichert", "success");
          // Aktualisieren der initialValues
          checkboxes.forEach((checkbox) => {
            const key = `${checkbox.dataset.employee}-${checkbox.dataset.permission}`;
            initialCheckboxValues[key] = checkbox.checked;
          });
          numberInputs.forEach((input) => {
            const employee = input.dataset.employee;
            const field = input.dataset.permission;
            if (!initialNumberValues[employee]) {
              initialNumberValues[employee] = {};
            }
            initialNumberValues[employee][field] = input.valueAsNumber;
          });
          document.getElementById("save-button").disabled = true;
        } else {
          showMessage(
            "Fehler beim Speichern der Änderungen: " + data.message,
            "error"
          );
        }
      })
      .catch((error) => {
        showMessage("Ein Fehler ist aufgetreten: " + error, "error");
      });
  } else {
    showMessage("Keine Änderungen zum Speichern", "info");
  }
}

function showMessage(message, type) {
  const messageContainer = document.getElementById("message-container");
  const messageElement = document.createElement("div");
  messageElement.className = `message ${type}-message show`;
  messageElement.innerText = message;
  messageContainer.appendChild(messageElement);

  setTimeout(() => {
    messageElement.classList.remove("show");
    setTimeout(() => {
      messageContainer.removeChild(messageElement);
    }, 500);
  }, 2000);
}
