let niveles = [];
let nivelActual = 0;
let palabraActual = 0;
let contenedorOriginal = null;
let tiempoInicio = Date.now();
let respuestasCorrectas = 0;
let respuestasIncorrectas = 0;
let tiempoTotal = 0;  // Variable para almacenar el tiempo total en segundos

function obtenerNivelDesdeURL() {
  const params = new URLSearchParams(window.location.search);
  const nivel = parseInt(params.get('nivel'));
  return isNaN(nivel) ? 0 : nivel;
}

nivelActual = obtenerNivelDesdeURL();

// Cargar el archivo JSON

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
});

function seleccionarPalabrasAleatorias(nivel) {
  const palabrasOriginales = nivel.palabras;
  const palabrasAleatorias = [...palabrasOriginales]
    .sort(() => 0.5 - Math.random()) // Mezcla aleatoria
    .slice(0, 10); // Toma las primeras 10

  return { ...nivel, palabras: palabrasAleatorias };
}

function togglePausa() {
  const modal = document.getElementById('modalPausa');
  const overlay = document.getElementById('modalOverlay');

  if (modal && overlay) {
    modal.classList.toggle('show');
    overlay.classList.toggle('show');
  }
}


// Función para mostrar el mensaje flotante
function mostrarMensajeFlotante(texto, color) {
  const mensaje = document.getElementById('mensaje-flotante');
  mensaje.textContent = texto;
  mensaje.style.backgroundColor = color;
  mensaje.style.display = 'block';

  setTimeout(() => {
    mensaje.style.display = 'none';
  }, 2000);
}

// Funciones de arrastrar y soltar
function permitirSoltar(ev) {
  ev.preventDefault();
}

function arrastrar(ev) {
  ev.dataTransfer.setData("text", ev.target.id);
  contenedorOriginal = ev.target.parentElement; // 🔁 recordamos de dónde salió
}

function soltar(ev) {
  ev.preventDefault();
  const data = ev.dataTransfer.getData("text");
  const letra = document.getElementById(data);
  let destino = ev.target;

  // Si no hay letra, salir de la función
  if (!letra) return;

  // Si soltó sobre una letra (dentro de cualquier contenedor), subimos al contenedor
  if (destino.classList.contains("letra")) {
    destino = destino.parentElement;
  }

  // Si soltó sobre un espacio vacío
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

  // Si soltó sobre el contenedor completo
  if (destino.classList.contains("letras-disponibles")) {
    destino.appendChild(letra);
    return;
  }

  // Si soltó sobre una letra DENTRO del contenedor .letras-disponibles
  if (destino.classList.contains("letra") && destino.parentElement.classList.contains("letras-disponibles")) {
    destino.parentElement.appendChild(letra);
    return;
  }

  // Si soltó en otro lugar no válido (por seguridad), volver al contenedor original
  if (contenedorOriginal) {
    contenedorOriginal.appendChild(letra);
  }
}

function verificarRespuesta() {
  const btnVerificar = document.getElementById('btnVerificar');
  if (btnVerificar) {
    btnVerificar.disabled = true; // Desactivar el botón de verificación para evitar múltiples clics
  }

  const nivelData = niveles[nivelActual];
  const contenedorPalabra = document.getElementById('contenedorPalabra');

  if (!nivelData || !contenedorPalabra || !nivelData.palabras[palabraActual]) {
    console.error("Datos de nivel o palabra actual no encontrados para verificación.");
    if (btnVerificar) btnVerificar.disabled = false; // Reactivar el botón si hay un error
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
    if (btnVerificar) btnVerificar.disabled = false; // Reactivar el botón si falta completar
    return;
  }

  const esCorrecta = palabraFormada.toUpperCase() === nivelData.palabras[palabraActual].palabra.toUpperCase();

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
    if (ventanaSiguiente) {
      ventanaSiguiente.classList.add('show');
    }
  }, 1500);

  const letras = document.querySelectorAll(".letra");
  letras.forEach(letra => {
    letra.setAttribute("draggable", "false");
    letra.removeAttribute("ondragstart");
  });
}

// Cargar nivel
function cargarNivel(nivelIdx, palabraIdx) {
  const nivel = niveles[nivelIdx];
  if (!nivel || !nivel.palabras || nivel.palabras.length <= palabraIdx) {
    console.error(`Error: Nivel ${nivelIdx} o palabra ${palabraIdx} no existen en el JSON.`);
    return;
  }

  const palabraObj = nivel.palabras[palabraIdx];
  const palabra = palabraObj.palabra;

  // Mostrar imagen de referencia
  const imagen = document.getElementById('imagenGuia');
  if (imagen) {
    imagen.src = `/static/${palabraObj.imagen}`;
  }

  const contenedorPalabra = document.getElementById('contenedorPalabra');
  if (contenedorPalabra) {
    contenedorPalabra.innerHTML = '';
  }

  // Lógica para seleccionar posiciones vacías
  let posicionesVacias = [];
  const minVacios = palabra.length > 1 ? 1 : 0;
  const numVaciosParaNivel = Math.min(nivelIdx + 1, palabra.length - minVacios);

  if (palabra.length > 0) {
    const todasLasPosiciones = Array.from({ length: palabra.length }, (_, i) => i);
    posicionesVacias = todasLasPosiciones
      .sort(() => Math.random() - 0.5)
      .slice(0, numVaciosParaNivel);
  }

  if (contenedorPalabra) {
    for (let i = 0; i < palabra.length; i++) {
      const letra = palabra[i];
      if (posicionesVacias.includes(i)) {
        contenedorPalabra.innerHTML += `<span class="letra-celda espacio-vacio" ondrop="soltar(event)" ondragover="permitirSoltar(event)"></span>`;
      } else {
        contenedorPalabra.innerHTML += `<span class="letra-celda">${letra}</span>`;
      }
    }
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
  if (textoBtn && niveles[nivelActual] && niveles[nivelActual].palabras) {
    if (palabraActual >= niveles[nivelActual].palabras.length - 1) {
      textoBtn.textContent = 'Finalizar';
    } else {
      textoBtn.textContent = 'Siguiente palabra';
    }
  }
}

// Ir al siguiente nivel
function irSiguiente() {
  // Reactivar el botón "Verificar" antes de avanzar a la siguiente palabra
  const btnVerificar = document.getElementById('btnVerificar');
  if (btnVerificar) {
    btnVerificar.disabled = false;
  }

  ocultarVentanaSiguiente();
  const nivel = niveles[nivelActual];

  if (!nivel || !nivel.palabras) {
    console.error("Nivel actual o sus palabras no encontrados al intentar ir al siguiente.");
    return;
  }

  palabraActual++;

  if (palabraActual >= nivel.palabras.length) {
    // Final del nivel: mostrar estadísticas
    mostrarVentanaEstadisticas();
    return;
  }

  cargarNivel(nivelActual, palabraActual);
}

function ocultarVentanaSiguiente() {
  const ventanaSiguiente = document.getElementById('ventanaSiguienteNivel');
  if (ventanaSiguiente) {
    ventanaSiguiente.classList.remove('show');
  }
}

// Mostrar estadísticas
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
  }).then(res => res.json()).then(data => {
    console.log("Progreso guardado:", data);
  }).catch(error => {
    console.error("Error al guardar el progreso:", error);
  });

  const modal = document.createElement("div");
  modal.className = "ventana-estadisticas";
  modal.innerHTML = `
    <div class="contenedor-estadisticas">
      <h2>¡Nivel completado!</h2>
      <p>Palabras correctas: ${respuestasCorrectas}</p>
      <p>Palabras incorrectas: ${respuestasIncorrectas}</p>
      <p>Puntaje total: ${puntaje}</p>
      <button onclick="volverAlMenu()">Volver al menú</button>
    </div>`;
  document.body.appendChild(modal);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
