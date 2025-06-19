document.addEventListener("DOMContentLoaded", () => {
  const musica = document.getElementById("musicaJuegos");

  // === Cargar preferencias del servidor ===
  fetch("/preferencias/")
    .then(response => response.json())
    .then(data => {
      if (data && typeof data.texto_grande === "boolean" && data.texto_grande) {
        document.body.classList.add("texto-grande");
      }

      if (data && typeof data.sonido_activado === "boolean") {
        if (data.sonido_activado) {
          musica?.play().catch(err => {
            console.warn("Reproducción bloqueada:", err);
          });
        } else {
          musica?.pause();
        }
      }
    })
    .catch(error => {
      console.warn("No se pudo cargar preferencias del servidor:", error);
    });
});

// === MENSAJE FLOTANTE ===
function mostrarMensajeFlotante(texto, color) {
  const mensaje = document.getElementById('mensaje-flotante');
  if (!mensaje) return;
  mensaje.textContent = texto;
  mensaje.style.backgroundColor = color || 'rgba(0,0,0,0.8)';
  mensaje.style.display = 'block';
  setTimeout(() => {
    mensaje.style.display = 'none';
  }, 2000);
}
