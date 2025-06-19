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

// ✅ Guardar en el servidor
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

// ✅ Cargar desde el servidor
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

// ✅ Aplicar preferencias
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
