let niveles = [];
let nivelActual = 0;
let palabraActual = 0;
let contenedorOriginal = null;
let tiempoInicio = Date.now();
let respuestasCorrectas = 0;
let respuestasIncorrectas = 0;
let tiempoTotal = 0;

// Obtener el nivel desde la URL
function obtenerNivelDesdeURL() {
  const params = new URLSearchParams(window.location.search);
  const nivel = parseInt(params.get('nivel'));
  return isNaN(nivel) ? 0 : nivel;
}

nivelActual = obtenerNivelDesdeURL();

// Cargar archivo JSON
fetch(jsonUrl)
  .then(response => response.json())
  .then(data => {
    niveles = data.map(nivel => seleccionarPalabrasAleatorias(nivel));
    cargarNivel(nivelActual, palabraActual);
  })
  .catch(err => {
    console.log('Error al cargar el JSON:', err);
  });

document.addEventListener('DOMContentLoaded', () => {
  const pausaBtn = document.getElementById("pausaBtn");
  if (pausaBtn) {
    pausaBtn.addEventListener("click", togglePausa);
  }

  // ✅ Cargar preferencias desde el servidor
  fetch("/preferencias/")
    .then(res => res.json())
    .then(data => {
      if (data && data.texto_grande) {
        document.body.classList.add("texto-grande");
      }

      const musica = document.getElementById("musicaJuegos");
      if (musica) {
        if (data && data.sonido_activado) {
          musica.play().catch(err => {
            console.warn("Reproducción bloqueada:", err);
          });
        } else {
          musica.pause();
        }
      }
    })
    .catch(error => {
      console.warn("No se pudieron aplicar las preferencias del servidor:", error);
    });
});

// Selección de palabras aleatorias
function seleccionarPalabrasAleatorias(nivel) {
  const palabrasOriginales = nivel.palabras;
  const palabrasAleatorias = [...palabrasOriginales]
    .sort(() => 0.5 - Math.random())
    .slice(0, 10);
  return { ...nivel, palabras: palabrasAleatorias };
}

// Pausar juego
function togglePausa() {
  const modal = document.getElementById('modalPausa');
  const overlay = document.getElementById('modalOverlay');
  if (modal && overlay) {
    modal.classList.toggle('show');
    overlay.classList.toggle('show');
  }
}

// Mostrar mensaje flotante
function mostrarMensajeFlotante(texto, color) {
  const mensaje = document.getElementById('mensaje-flotante');
  mensaje.textContent = texto;
  mensaje.style.backgroundColor = color;
  mensaje.style.display = 'block';
  setTimeout(() => {
    mensaje.style.display = 'none';
  }, 2000);
}

// Drag & Drop
function permitirSoltar(ev) {
  ev.preventDefault();
}

function arrastrar(ev) {
  ev.dataTransfer.setData("text", ev.target.id);
  contenedorOriginal = ev.target.parentElement;
}

function soltar(ev) {
  ev.preventDefault();
  const data = ev.dataTransfer.getData("text");
  const letra = document.getElementById(data);
  let destino = ev.target;

  if (!letra) return;

  if (destino.classList.contains("letra")) {
    destino = destino.parentElement;
  }

  if (destino.classList.contains("espacio-vacio")) {
    if (destino.children.length > 0) {
      const letraAnterior = destino.firstElementChild;
      const disponibles = document.querySelector(".letras-disponibles");
      if (disponibles) {
        disponibles.appendChild(letraAnterior);
      }
    }
    destino.appendChild(letra);
    return;
  }

  if (destino.classList.contains("letras-disponibles")) {
    destino.appendChild(letra);
    return;
  }

  if (destino.classList.contains("letra") && destino.parentElement.classList.contains("letras-disponibles")) {
    destino.parentElement.appendChild(letra);
    return;
  }

  if (contenedorOriginal) {
    contenedorOriginal.appendChild(letra);
  }
}

// Verificar respuesta
function verificarRespuesta() {
  const btnVerificar = document.getElementById('btnVerificar');
  if (btnVerificar) btnVerificar.disabled = true;

  const nivelData = niveles[nivelActual];
  const contenedorPalabra = document.getElementById('contenedorPalabra');
  if (!nivelData || !contenedorPalabra || !nivelData.palabras[palabraActual]) {
    console.error("Datos de nivel o palabra no encontrados.");
    if (btnVerificar) btnVerificar.disabled = false;
    return;
  }

  let palabraFormada = "";
  let espaciosVacios = false;

  for (const span of contenedorPalabra.children) {
    if (span.classList.contains('espacio-vacio')) {
      const letraEnEspacio = span.firstElementChild;
      if (letraEnEspacio) {
        palabraFormada += letraEnEspacio.textContent.trim();
      } else {
        palabraFormada += "_";
        espaciosVacios = true;
      }
    } else {
      palabraFormada += span.textContent.trim();
    }
  }

  if (espaciosVacios) {
    mostrarMensajeFlotante("Debes completar la palabra antes de verificar.", "orange");
    if (btnVerificar) btnVerificar.disabled = false;
    return;
  }

  const palabraCorrecta = nivelData.palabras[palabraActual].palabra;
  const esCorrecta = palabraFormada.toUpperCase() === palabraCorrecta.toUpperCase();

  if (esCorrecta) {
    respuestasCorrectas++;
    mostrarMensajeFlotante("¡Correcto! Muy bien 😊", "rgba(0, 128, 0, 0.85)");
  } else {
    respuestasIncorrectas++;
    mostrarMensajeFlotante("Buena suerte para la siguiente 😅", "rgba(255, 140, 0, 0.85)");
  }

  actualizarTextoSiguiente();
  setTimeout(() => {
    const ventanaSiguiente = document.getElementById('ventanaSiguienteNivel');
    if (ventanaSiguiente) ventanaSiguiente.classList.add('show');
  }, 1500);

  document.querySelectorAll(".letra").forEach(letra => {
    letra.setAttribute("draggable", "false");
    letra.removeAttribute("ondragstart");
  });
}

// Cargar nivel
function cargarNivel(nivelIdx, palabraIdx) {
  const nivel = niveles[nivelIdx];
  if (!nivel || !nivel.palabras || nivel.palabras.length <= palabraIdx) {
    console.error("Nivel o palabra no existe.");
    return;
  }

  const palabraObj = nivel.palabras[palabraIdx];
  const palabra = palabraObj.palabra;

  const imagen = document.getElementById('imagenGuia');
  if (imagen) imagen.src = `/static/${palabraObj.imagen}`;

  const contenedorPalabra = document.getElementById('contenedorPalabra');
  if (contenedorPalabra) contenedorPalabra.innerHTML = '';

  let posicionesVacias = [];
  const minVacios = palabra.length > 1 ? 1 : 0;
  const numVacios = Math.min(nivelIdx + 1, palabra.length - minVacios);

  if (palabra.length > 0) {
    posicionesVacias = Array.from({ length: palabra.length }, (_, i) => i)
      .sort(() => Math.random() - 0.5)
      .slice(0, numVacios);
  }

  for (let i = 0; i < palabra.length; i++) {
    const letra = palabra[i];
    contenedorPalabra.innerHTML += posicionesVacias.includes(i)
      ? `<span class="letra-celda espacio-vacio" ondrop="soltar(event)" ondragover="permitirSoltar(event)"></span>`
      : `<span class="letra-celda">${letra}</span>`;
  }

  const contenedorLetras = document.getElementById('contenedorLetras');
  if (contenedorLetras) {
    contenedorLetras.innerHTML = '';
    palabraObj.letras.forEach((letra, i) => {
      contenedorLetras.innerHTML += `<div class="letra" draggable="true" ondragstart="arrastrar(event)" id="letra${i}">${letra}</div>`;
    });
  }
}

function actualizarTextoSiguiente() {
  const textoBtn = document.getElementById('texto-btn-nivel');
  if (!textoBtn) return;

  const esUltima = palabraActual >= niveles[nivelActual].palabras.length - 1;
  textoBtn.textContent = esUltima ? "Finalizar" : "Siguiente palabra";
}

function irSiguiente() {
  const btnVerificar = document.getElementById('btnVerificar');
  if (btnVerificar) btnVerificar.disabled = false;

  ocultarVentanaSiguiente();

  palabraActual++;
  if (palabraActual >= niveles[nivelActual].palabras.length) {
    mostrarVentanaEstadisticas();
    return;
  }

  cargarNivel(nivelActual, palabraActual);
}

function ocultarVentanaSiguiente() {
  const ventanaSiguiente = document.getElementById('ventanaSiguienteNivel');
  if (ventanaSiguiente) ventanaSiguiente.classList.remove('show');
}

function formatearTiempo(segundosTotales) {
  const horas = Math.floor(segundosTotales / 3600);
  const minutos = Math.floor((segundosTotales % 3600) / 60);
  const segundos = segundosTotales % 60;

  const partes = [];
  if (horas) partes.push(`${horas}h`);
  if (minutos || horas) partes.push(`${minutos}m`);
  partes.push(`${segundos}s`);
  return partes.join(' ');
}

function mostrarVentanaEstadisticas() {
  tiempoTotal = Math.floor((Date.now() - tiempoInicio) / 1000);
  const puntaje = respuestasCorrectas * 10;

  fetch(guardarUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: `nivel=${nivelActual + 1}&puntaje=${puntaje}&tiempo=${tiempoTotal}`
  }).then(res => res.json())
    .then(data => {
      console.log("Progreso guardado:", data);
    }).catch(err => {
      console.error("Error al guardar el progreso:", err);
    });

  const modal = document.createElement("div");
  modal.className = "ventana-estadisticas";
  modal.innerHTML = `
    <div class="contenedor-estadisticas">
      <h2>¡Nivel completado!</h2>
      <p>Palabras correctas: ${respuestasCorrectas}</p>
      <p>Palabras incorrectas: ${respuestasIncorrectas}</p>
      <p>Tiempo total: ${formatearTiempo(tiempoTotal)}</p>
      <p>Puntaje total: ${puntaje}</p>
      <button onclick="volverAlMenu()">Volver al menú</button>
    </div>`;
  document.body.appendChild(modal);
}

function volverAlMenu() {
  window.location.href = urlNivelesDisgrafia;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
