document.addEventListener("DOMContentLoaded", () => {
  const musica = document.getElementById("musicaJuegos");

  // === Cargar preferencias desde el servidor ===
  fetch("/preferencias/")
    .then(response => response.json())
    .then(data => {
      if (data && typeof data.sonido_activado === "boolean") {
        if (data.sonido_activado) {
          musica?.play().catch(err => {
            console.warn("Reproducción bloqueada:", err);
          });
        } else {
          musica?.pause();
        }
      }

      if (data && typeof data.texto_grande === "boolean" && data.texto_grande) {
        document.body.classList.add("texto-grande");
      }
    })
    .catch(error => {
      console.warn("No se pudo cargar preferencias del servidor:", error);
    });
});
