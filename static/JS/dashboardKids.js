function openModal() {
  document.getElementById('configModal').style.display = 'flex';
}

function closeModal(event) {
  if (event.target.id === 'configModal' || event.target.classList.contains('modal-close-btn')) {
    document.getElementById('configModal').style.display = 'none';
  }
}

function openRecordModal() {
  document.getElementById('recordModal').style.display = 'flex';
}

function closeRecordModal(event) {
  if (event.target.id === 'recordModal' || event.target.classList.contains('modal-close-btn')) {
    document.getElementById('recordModal').style.display = 'none';
  }
}

// Abrir modal de VISTA de perfil
function openProfileViewModal() {
  document.getElementById('profileViewModal').style.display = 'flex';
}

function closeProfileViewModal(event) {
  if (event.target.id === 'profileViewModal' || event.target.classList.contains('modal-close-btn')) {
    document.getElementById('profileViewModal').style.display = 'none';
  }
}

// Abrir modal de EDICIÓN de perfil
function openEditProfileModal() {
  document.getElementById('editProfileModal').style.display = 'flex';
}

function closeEditProfileModal(event) {
  if (event.target.id === 'editProfileModal' || event.target.classList.contains('modal-close-btn')) {
    document.getElementById('editProfileModal').style.display = 'none';
  }
}

// ===================
// 🔊 Sonido y texto
// ===================

let sonidoActivo = true;
let textoGrande = false;

function toggleSonido() {
  sonidoActivo = !sonidoActivo;
  actualizarPreferenciasEnServidor();

  document.getElementById("btnSonido").textContent = sonidoActivo ? "Activado" : "Desactivado";

  const musica = document.getElementById("musicaDashboard");
  if (musica) {
    if (sonidoActivo) {
      musica.play().catch(() => {});
    } else {
      musica.pause();
    }
  }
}

function toggleTexto() {
  textoGrande = !textoGrande;
  actualizarPreferenciasEnServidor();

  document.body.classList.toggle("texto-grande", textoGrande);
  document.getElementById("btnTexto").textContent = textoGrande ? "Grande" : "Normal";
}

function mostrarAyuda() {
  alert("🧠 Bienvenido a Eduflex.\n\nDesde aquí puedes acceder a tus juegos y métricas.\nSi tienes dudas, contacta a tu tutor o administrador.");
}

function actualizarPreferenciasEnServidor() {
  const formData = new FormData();
  formData.append("sonido_activado", sonidoActivo);
  formData.append("texto_grande", textoGrande);

  fetch("/preferencias/", {
    method: "POST",
    body: formData
  }).catch(error => {
    console.error("No se pudieron guardar las preferencias:", error);
  });
}

function cargarPreferenciasDesdeServidor() {
  fetch("/preferencias/")
    .then(res => res.json())
    .then(data => {
      if (data && typeof data.sonido_activado === "boolean") {
        sonidoActivo = data.sonido_activado;
      }
      if (data && typeof data.texto_grande === "boolean") {
        textoGrande = data.texto_grande;
      }

      aplicarPreferencias();
    })
    .catch(err => {
      console.warn("No se pudo cargar preferencias del servidor:", err);
      aplicarPreferencias(); // Usa valores por defecto
    });
}

function aplicarPreferencias() {
  document.body.classList.toggle("texto-grande", textoGrande);
  document.getElementById("btnTexto").textContent = textoGrande ? "Grande" : "Normal";

  const musica = document.getElementById("musicaDashboard");
  if (musica) {
    if (sonidoActivo) {
      musica.play().catch(() => {});
    } else {
      musica.pause();
    }
  }

  document.getElementById("btnSonido").textContent = sonidoActivo ? "Activado" : "Desactivado";
}

document.addEventListener("DOMContentLoaded", () => {
  cargarPreferenciasDesdeServidor();
});


// ==========================
// 📤 Enviar formulario edición perfil
// ==========================

document.getElementById("editarPerfilForm").addEventListener("submit", function(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);

  fetch("/editar-perfil/", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.estado === "ok") {
      alert(data.mensaje || "Perfil actualizado correctamente.");
      location.reload();
    } else {
      alert(data.mensaje || "Hubo un error al actualizar el perfil.");
    }
  })
  .catch(err => {
    console.error("Error:", err);
    alert("Error al actualizar perfil.");
  });
});
