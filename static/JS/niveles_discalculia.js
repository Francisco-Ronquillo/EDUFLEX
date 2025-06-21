// Esperar a que cargue el DOM
document.addEventListener("DOMContentLoaded", () => {
  const musica = document.getElementById("musicaJuegos");

  // ✅ Cargar preferencias del servidor
  fetch("/preferencias/")
    .then(res => res.json())
    .then(data => {
      // Aplicar sonido
      if (musica) {
        if (data.sonido_activado) {
          musica.play().catch(err => {
            console.warn("Reproducción bloqueada por el navegador:", err);
          });
        } else {
          musica.pause();
        }
      }

      // Aplicar texto grande
      if (data.texto_grande) {
        document.body.classList.add("texto-grande");
      }
    })
    .catch(error => {
      console.warn("No se pudieron cargar las preferencias del servidor:", error);
    });
});

// ✅ Función para mostrar mensajes flotantes
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
