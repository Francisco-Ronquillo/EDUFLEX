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
    niveles = data;
    cargarNivel(nivelActual, palabraActual); // ✅ aquí sí funciona, ya hay datos
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

  // 👇 Si soltó sobre una letra (dentro de cualquier contenedor), subimos al contenedor
  if (destino.classList.contains("letra")) {
    destino = destino.parentElement;
  }

  // ✅ Si soltó sobre un espacio vacío
  if (destino.classList.contains("espacio-vacio")) {
    if (destino.children.length > 0) {
      const letraAnterior = destino.firstElementChild;
      const disponibles = document.querySelector(".letras-disponibles");
      disponibles.appendChild(letraAnterior);
    }
    destino.appendChild(letra);
    return;
  }

  // ✅ Si soltó sobre el contenedor completo
  if (destino.classList.contains("letras-disponibles")) {
    destino.appendChild(letra);
    return;
  }

  // ✅ Si soltó sobre una letra DENTRO del contenedor .letras-disponibles
  if (
    destino.classList.contains("letra") &&
    destino.parentElement.classList.contains("letras-disponibles")
  ) {
    destino.parentElement.appendChild(letra);
    return;
  }

  // 🔁 Extra: Si soltó en otro lugar no válido (por seguridad), volver al contenedor original
  if (contenedorOriginal) {
    contenedorOriginal.appendChild(letra);
  }
}

function verificarRespuesta() {
  const nivelData = niveles[nivelActual];
  const contenedorPalabra = document.getElementById('contenedorPalabra');

  let palabraFormada = "";
  let espaciosVacios = false;
  for (const span of contenedorPalabra.children) {
    const texto = span.textContent.trim();
    if (span.classList.contains('espacio-vacio') && texto === '') {
      espaciosVacios = true;
    }
    palabraFormada += texto || "_";
  }

  if (espaciosVacios) {
    mostrarMensajeFlotante("Debes completar la palabra antes de verificar.", "orange");
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
    document.getElementById('ventanaSiguienteNivel').classList.add('show');
  }, 1500);

  const letras = document.querySelectorAll(".letra");
  letras.forEach(letra => {
    letra.setAttribute("draggable", "false");
    letra.removeAttribute("ondragstart");
  });
}

function cargarNivel(nivelIdx, palabraIdx) {
  const nivel = niveles[nivelIdx];
  const palabraObj = nivel.palabras[palabraIdx];
  const palabra = palabraObj.palabra;

  // Mostrar imagen de referencia
  const imagen = document.getElementById('imagenGuia');
  imagen.src = `/static/${palabraObj.imagen}`;


  // Limpiar el contenedor de la palabra
  const contenedorPalabra = document.getElementById('contenedorPalabra');
  contenedorPalabra.innerHTML = '';

  // 👉 Seleccionar posiciones donde la letra esté en letras[]
  const posicionesPermitidas = [];
  for (let i = 0; i < palabra.length; i++) {
    if (palabraObj.letras.includes(palabra[i])) {
      posicionesPermitidas.push(i);
    }
  }

  // ✅ Solo vaciar una letra aleatoria de las permitidas
  // 🔁 Vaciar más letras según el nivel actual
let posicionesVacias = [];
if (posicionesPermitidas.length > 0) {
  const maxVacios = Math.min(nivelIdx + 1, posicionesPermitidas.length, palabra.length - 1);
  posicionesVacias = posicionesPermitidas
    .sort(() => Math.random() - 0.5)
    .slice(0, maxVacios);
}

  // Construir la palabra con espacios y letras
  for (let i = 0; i < palabra.length; i++) {
    const letra = palabra[i];
    if (posicionesVacias.includes(i)) {
      contenedorPalabra.innerHTML += `
        <span class="letra-celda espacio-vacio" ondrop="soltar(event)" ondragover="permitirSoltar(event)">
        </span>`;
    } else {
      contenedorPalabra.innerHTML += `<span class="letra-celda">${letra}</span>`;
    }
  }

  // Cargar letras disponibles
  const contenedorLetras = document.getElementById('contenedorLetras');
  contenedorLetras.innerHTML = '';
  palabraObj.letras.forEach((letra, i) => {
    contenedorLetras.innerHTML += `
      <div class="letra" draggable="true" ondragstart="arrastrar(event)" id="letra${i}">
        ${letra}
      </div>`;
  });
}

function irSiguiente() {
  ocultarVentanaSiguiente();
  const nivel = niveles[nivelActual];

  palabraActual++;

  if (palabraActual >= nivel.palabras.length) {
    // Final del nivel: mostrar estadísticas
    mostrarVentanaEstadisticas();
    return;
  }

  cargarNivel(nivelActual, palabraActual);
}

function ocultarVentanaSiguiente() {
  document.getElementById('ventanaSiguienteNivel').classList.remove('show');
}

function actualizarTextoSiguiente() {
  const textoBtn  = document.getElementById('texto-btn-nivel');
  if (palabraActual >= niveles[nivelActual].palabras.length - 1) {
    textoBtn.textContent = 'Finalizar';
  } else {
    textoBtn.textContent = 'Siguiente palabra';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Activar botón de pausa
  const pausaBtn = document.getElementById("pausaBtn");
  if (pausaBtn) {
    pausaBtn.addEventListener("click", togglePausa);
  }
});

function togglePausa() {
  const modal = document.getElementById('modalPausa');
  const overlay = document.getElementById('modalOverlay');

  modal.classList.toggle('show');
  overlay.classList.toggle('show');
}

function mostrarVentanaEstadisticas() {
  tiempoTotal = Math.floor((Date.now() - tiempoInicio) / 1000); // Tiempo en segundos

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
