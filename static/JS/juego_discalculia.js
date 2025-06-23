
const totalPreguntas = 10;
let contadorCorrecto = 0;
let contadorIncorrecto = 0;
let contadorPreguntas = 0;
let tiempoInicio = 0;
let puntos = 0;
let tiempoPausado = 0;
let pausaInicio = 0;
let musicaBackup = null;
let juegoPausado = false;
let bloquearOpciones = false;
let respuestaPendiente = false;
const preguntasHechasEnNivel = new Set(); // ← NUEVO

const nivelActual = obtenerNivelDesdeURL();
const dificultadPorNivel = [
    [1, 4],    // Nivel 1: Tablas del 1 al 4
    [5, 7],    // Nivel 2: Tablas del 5 al 7
    [8, 10],   // Nivel 3: Tablas del 8 al 10
    [10, 20],  // Nivel 4: Multiplicaciones de dos cifras sencillas
    [10, 30],  // Nivel 5: Multiplicaciones de dos cifras un poco más difíciles
];




function mostrarMensajeFlotante(texto, color) {
    const mensaje = document.getElementById("mensaje-flotante");
    if (!mensaje) return;
    mensaje.textContent = texto;
    mensaje.style.backgroundColor = color;
    mensaje.style.display = "block";
    mensaje.style.animation = "none";
    void mensaje.offsetWidth;
    mensaje.style.animation = "fadeInOut 2s ease-in-out";
    setTimeout(() => {
        mensaje.style.display = "none";
    }, 2000);
}


function crearBurbujas() {
    const contenedor = document.getElementById("burbujas-container");
    for (let i = 0; i < 15; i++) {
        const burbuja = document.createElement("div");
        burbuja.className = "burbuja";
        burbuja.style.left = Math.random() * 100 + "vw";
        burbuja.style.animationDuration = (Math.random() * 2 + 2) + "s";
        contenedor.appendChild(burbuja);
    }
}


function generarPregunta() {
    if (contadorPreguntas >= totalPreguntas) {
        finalizarJuego();
        return;
    }

    if (contadorPreguntas === 0) {
        tiempoInicio = Date.now();
    }

    const [min, max] = dificultadPorNivel[nivelActual] || [1, 5];
    let num1, num2, clave;
    let intentos = 0;


    do {
        num1 = Math.floor(Math.random() * (max - min + 1)) + min;
        num2 = Math.floor(Math.random() * (max - min + 1)) + min;
        const ordenados = [num1, num2].sort((a, b) => a - b);
        clave = `${ordenados[0]}x${ordenados[1]}`;
        intentos++;
        if (intentos > 100) {
            console.warn("Demasiados intentos para generar una pregunta única. Finalizando.");
            finalizarJuego();
            return;
        }
    } while (preguntasHechasEnNivel.has(clave));

    preguntasHechasEnNivel.add(clave);

    const respuestaCorrecta = num1 * num2;
    contadorPreguntas++;

    document.getElementById('contador-pregunta').innerText = `Nivel ${nivelActual + 1} - Pregunta ${contadorPreguntas} de ${totalPreguntas}`;
    document.getElementById('pregunta').innerText = `¿Cuánto es ${num1} x ${num2}?`;
    document.getElementById('opciones').innerHTML = '';
    bloquearOpciones = false;

    let respuestas = [respuestaCorrecta, respuestaCorrecta + 1, respuestaCorrecta - 1, respuestaCorrecta + 2];
    respuestas = [...new Set(respuestas)].sort(() => Math.random() - 0.5);

    respuestas.forEach(respuesta => {
        const boton = document.createElement('button');
        boton.className = 'opcion';
        boton.innerText = respuesta;
        boton.addEventListener('click', () => verificarRespuesta(respuesta, respuestaCorrecta));
        document.getElementById('opciones').appendChild(boton);
    });
}

function verificarRespuesta(seleccionada, correcta) {
    if (bloquearOpciones) return;
    bloquearOpciones = true;

    const buzoElemento = document.getElementById('buzo');
    const tiburonElemento = document.getElementById('tiburon');
    const opciones = document.querySelectorAll('.opcion');


    opciones.forEach(btn => {
        btn.disabled = true;
        btn.classList.add("desactivado");

        const valor = parseInt(btn.innerText);
        if (valor === correcta) {
            btn.classList.add('correcta');
        }
        if (valor === seleccionada && valor !== correcta) {
            btn.classList.add('incorrecta');
        }
    });

    if (seleccionada === correcta) {
        contadorCorrecto++;
        mostrarMensajeFlotante("¡Correcto! 🎉", "rgba(40, 167, 69, 0.9)");
        buzoElemento.src = buzo2URL;
        puntos += 10;
    } else {
        contadorIncorrecto++;
        mostrarMensajeFlotante("Incorrecto 😞", "rgba(220, 53, 69, 0.9)");
        tiburonElemento.style.transform = "scale(2.5)";
    }

    setTimeout(() => {
        buzoElemento.src = buzo1URL;
        tiburonElemento.style.transform = "scale(1)";
        if (!juegoPausado) {
            generarPregunta();
        } else {
            respuestaPendiente = true;
        }
    }, 1500);
}




function finalizarJuego() {
    const tiempoTotal = Math.round((Date.now() - tiempoInicio - tiempoPausado) / 1000);
    const totalPuntos = puntos;
    const aprobado = contadorCorrecto >= 7;

    document.getElementById("pregunta").innerText = '';
    document.getElementById("opciones").innerHTML = '';
    document.getElementById("contador-pregunta").innerText = '';
    document.getElementById("pausaBtn").disabled = true;

    fetch('/guardar_progreso_multiplicacion/', {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: `nivel=${nivelActual + 1}&puntaje=${totalPuntos}&tiempo=${tiempoTotal}`
    }).catch(err => console.warn("Error al guardar progreso:", err));

    const modal = document.createElement("div");
    modal.className = "ventana-estadisticas";
    modal.innerHTML = `
        <div class="contenedor-estadisticas">
            <h2>¡Nivel completado!</h2>
            <p>✅ Respuestas correctas: ${contadorCorrecto}</p>
            <p>❌ Respuestas incorrectas: ${contadorIncorrecto}</p>
            <p>⏱ Tiempo total: ${formatearTiempo(tiempoTotal)}</p>
            <p>🏆 Puntos: ${totalPuntos} de 100</p>
            <p>${aprobado ? "✅ Nivel aprobado. ¡Muy bien!" : "❌ No aprobaste. Intenta de nuevo."}</p>
            <button onclick="volverAlMenu()">Volver al menú</button>
        </div>`;
    document.body.appendChild(modal);
}


function volverAlMenu() {
    window.location.href = "/niveles_discalculia/";
}

// === PAUSA ===
function togglePausa() {
    const modal = document.getElementById('modalPausa');
    const overlay = document.getElementById('modalOverlay');
    const musica = document.getElementById('musicaJuegos');

    modal.classList.toggle('show');
    overlay.classList.toggle('show');
    juegoPausado = modal.classList.contains('show');

    if (juegoPausado) {
        pausaInicio = Date.now();
        if (musica && !musica.paused) {
            musicaBackup = true;
            musica.pause();
        }
    } else {
        const tiempoTranscurrido = Date.now() - pausaInicio;
        tiempoPausado += tiempoTranscurrido;
        if (musica && musicaBackup) {
            musica.play().catch(() => {});
        }

        if (respuestaPendiente) {
            generarPregunta();
            respuestaPendiente = false;
        }
    }
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


crearBurbujas();
generarPregunta();

document.addEventListener('DOMContentLoaded', () => {
    fetch("/preferencias/")
        .then(res => res.json())
        .then(data => {
            if (data?.texto_grande) {
                document.body.classList.add("texto-grande");
            }

            const musica = document.getElementById("musicaJuegos");
            if (musica) {
                if (data?.sonido_activado) {
                    musica.play().catch(() => {});
                } else {
                    musica.pause();
                }
            }
        });

    const pausaBtn = document.getElementById("pausaBtn");
    if (pausaBtn) {
        pausaBtn.addEventListener("click", togglePausa);
    }
});
