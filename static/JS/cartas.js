// === CONFIGURACIÓN ===
const availableCards = ['🐷', '🐶', '👻', '🤡', '😱', '💩', '😫', '❤️', '🥸', '😁', '🙈', '🐧'];
const cartasPorNivel = [8, 10, 12, 18, 24]; // Cartas por nivel
const tiemposPorNivel = [5000, 4000, 3000, 2000, 2000]; // tiempo en milisegundos según el nivel

let cards = [], selectedCards = [], valuesUsed = [];
let currentMove = 0, currentAttempts = 0, matchedPairs = 0;
let tiempoInicio, tiempoPausado = 0;
let acumulado = 0;  // Variable para almacenar el tiempo acumulado
let cronometrar = false;  // Variable para controlar si el cronómetro está activo
let pausaInicio = 0;
let juegoPausado = false;
let musicaBackup = false;

const nivelActual = obtenerNivelDesdeURL();
const totalCards = cartasPorNivel[nivelActual] || 12;

// Determinamos el número de columnas en función del nivel
const columnasPorNivel = [4, 5, 4, 6, 8]; // Número de columnas por nivel
const columnas = columnasPorNivel[nivelActual]; // Establece el número de columnas según el nivel

// Actualiza el estilo CSS dinámicamente para las columnas
document.querySelector('#game').style.gridTemplateColumns = `repeat(${columnas}, 1fr)`;

// Plantilla de las cartas
const cardTemplate = '<div class="card"><div class="back"></div><div class="face"></div></div>';

// === CRONÓMETRO ===
function formatearTiempo(tiempo_ms) {
    const totalSegundos = Math.floor(tiempo_ms / 1000);
    const horas = Math.floor(totalSegundos / 3600);
    const minutos = Math.floor((totalSegundos % 3600) / 60);
    const segundos = totalSegundos % 60;

    let tiempoFormateado = "";
    if (horas > 0) tiempoFormateado += `${horas}h `;
    if (minutos > 0 || horas > 0) tiempoFormateado += `${minutos}m `;
    tiempoFormateado += `${segundos}s`;

    return tiempoFormateado;
}

//id
// === INICIO DEL JUEGO ===
function iniciarJuegoConCartasVisibles() {
    for (let i = 0; i < totalCards; i++) {
        let div = document.createElement('div');
        div.innerHTML = cardTemplate;
        cards.push(div);
        document.querySelector('#game').append(cards[i]);

        randomValue();
        const cardElement = cards[i].querySelector('.card');
        cardElement.querySelector('.face').innerHTML = getFaceValue(valuesUsed[i]);
        cardElement.classList.add('active'); // Mostrar la carta
        cardElement.addEventListener('click', activate);
    }

    const tiempoVisible = tiemposPorNivel[nivelActual] || 2000;

    // Después de que las cartas desaparezcan, empieza el cronómetro
    setTimeout(() => {
        cards.forEach(card => {
            card.querySelector('.card').classList.remove('active');
        });
        tiempoInicio = Date.now(); // Marca el inicio del cronómetro
        cronometrar = true; // Activa el cronómetro
    }, tiempoVisible);
}

iniciarJuegoConCartasVisibles();

// === FUNCIONES ===
function activate(e) {
    if (currentMove < 2) {
        const card = e.target.closest('.card');
        if ((!selectedCards[0] || selectedCards[0] !== card) && !card.classList.contains('active')) {
            card.classList.add('active');
            selectedCards.push(card);

            if (++currentMove === 2) {
                currentAttempts++;
                document.querySelector('#stats').innerHTML = currentAttempts + ' intentos';

                const face1 = selectedCards[0].querySelector('.face').innerHTML;
                const face2 = selectedCards[1].querySelector('.face').innerHTML;

                if (face1 === face2) {
                    matchedPairs++;
                    selectedCards = [];
                    currentMove = 0;

                    if (matchedPairs === totalCards / 2) {
                        setTimeout(finalizarNivel, 800);
                    }
                } else {
                    setTimeout(() => {
                        selectedCards[0].classList.remove('active');
                        selectedCards[1].classList.remove('active');
                        selectedCards = [];
                        currentMove = 0;
                    }, 600);
                }
            }
        }
    }
}

function finalizarNivel() {
    cronometrar = false;  // Detener el cronómetro cuando se finalice el nivel

    const tiempoTotal = Math.round((Date.now() - tiempoInicio - tiempoPausado) / 1000);
    const intentosIdeales = totalCards / 2;
    let puntaje = 100;

    if (currentAttempts > intentosIdeales) {
        const penalizacion = (currentAttempts - intentosIdeales) * 5;
        puntaje = Math.max(0, 100 - penalizacion);
    }

    fetch('/guardar_progreso_cartas/', {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: `nivel=${nivelActual + 1}&puntaje=${puntaje}&tiempo=${tiempoTotal}`
    })
    .then(res => res.json())
    .then(() => {
        mostrarVentanaEstadisticas(tiempoTotal, puntaje);
    });
}

function mostrarVentanaEstadisticas(tiempo, puntaje) {
const tiempoFormateado = formatearTiempo(tiempo * 1000);  // Convertimos de seg a ms

    const modal = document.createElement("div");
    modal.className = "ventana-estadisticas";
    modal.style.cssText = "position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 9999";

    modal.innerHTML = `
        <div class="contenedor-estadisticas" style="background: white; padding: 30px; border-radius: 20px; text-align: center;">
            <h2>¡Nivel completado!</h2>
            <p>Intentos realizados: ${currentAttempts}</p>
            <p>Tiempo total: ${tiempoFormateado}</p> 
            <p>Puntaje obtenido: ${puntaje}</p>
            <button class="button-input" onclick="window.location.href='/niveles_cartas/'">Volver al menú</button>
        </div>`;
    document.body.appendChild(modal);
}

function randomValue() {
    let rnd = Math.floor(Math.random() * (totalCards / 2));
    let values = valuesUsed.filter(value => value === rnd);
    if (values.length < 2) {
        valuesUsed.push(rnd);
    } else {
        randomValue();
    }
}

function getFaceValue(value) {
    return availableCards[value % availableCards.length];
}

function obtenerNivelDesdeURL() {
    const params = new URLSearchParams(window.location.search);
    const nivel = parseInt(params.get('nivel'));
    return isNaN(nivel) ? 0 : nivel;
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

// === Botón de Pausa ===
document.addEventListener("DOMContentLoaded", () => {
    const pausaBtn = document.getElementById("pausaBtn");
    if (pausaBtn) {
        pausaBtn.addEventListener("click", togglePausa);
    }
});

function togglePausa() {
    const modal = document.getElementById('modalPausa');
    const overlay = document.getElementById('modalOverlay');
    const musica = document.getElementById("musicaJuegos");

    modal.classList.toggle('show');
    overlay.classList.toggle('show');

    juegoPausado = modal.classList.contains('show');

    if (juegoPausado) {
        pausaInicio = Date.now();
        cronometrar = false;

        if (musica && !musica.paused) {
            musicaBackup = true;
            musica.pause();
        }
    } else {
        const tiempoTranscurrido = Date.now() - pausaInicio;
        tiempoPausado += tiempoTranscurrido;
        cronometrar = true;

        if (musica && musicaBackup) {
            musica.play().catch(() => {});
        }
    }
}

// === CRONÓMETRO ACTUALIZADO ===
// Hacer que el cronómetro se actualice constantemente
setInterval(() => {
    if (cronometrar) {
        acumulado = Date.now() - tiempoInicio - tiempoPausado;
    }
}, 100);

document.addEventListener('DOMContentLoaded', () => {
  // Leer preferencias del servidor
  fetch("/preferencias/")
    .then(res => res.json())
    .then(data => {
      // Aplicar preferencia de texto grande
      if (data && data.texto_grande) {
        document.body.classList.add("texto-grande");
      }

      // Aplicar preferencia de sonido
      const musica = document.getElementById("musicaJuegos");
      if (musica) {
        if (data && data.sonido_activado) {
          musica.play().catch(err => {
            console.warn("Reproducción bloqueada por el navegador:", err);
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
