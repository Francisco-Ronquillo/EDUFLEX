
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

    // Funcionalidades nuevas
    let sonidoActivo = true;
    let modoOscuro = false;
    let textoGrande = false;

    function toggleSonido() {
      sonidoActivo = !sonidoActivo;
      document.getElementById("btnSonido").textContent = sonidoActivo ? "Activado" : "Desactivado";
      localStorage.setItem("sonido", sonidoActivo);
    }

    function toggleModo() {
      modoOscuro = !modoOscuro;
      document.body.classList.toggle("modo-oscuro", modoOscuro);
      document.getElementById("btnModo").textContent = modoOscuro ? "Oscuro" : "Claro";
      localStorage.setItem("modoOscuro", modoOscuro);
    }

    function toggleTexto() {
      textoGrande = !textoGrande;
      document.body.classList.toggle("texto-grande", textoGrande);
      document.getElementById("btnTexto").textContent = textoGrande ? "Grande" : "Normal";
      localStorage.setItem("textoGrande", textoGrande);
    }

    function mostrarAyuda() {
      alert("🧠 Bienvenido a Eduflex.\n\nDesde aquí puedes acceder a tus juegos y métricas.\nSi tienes dudas, contacta a tu tutor o administrador.");
    }

    // Restaurar preferencias al cargar
    document.addEventListener("DOMContentLoaded", () => {
      sonidoActivo = localStorage.getItem("sonido") === "true";
      modoOscuro = localStorage.getItem("modoOscuro") === "true";
      textoGrande = localStorage.getItem("textoGrande") === "true";

      if (modoOscuro) document.body.classList.add("modo-oscuro");
      if (textoGrande) document.body.classList.add("texto-grande");

      document.getElementById("btnSonido").textContent = sonidoActivo ? "Activado" : "Desactivado";
      document.getElementById("btnModo").textContent = modoOscuro ? "Oscuro" : "Claro";
      document.getElementById("btnTexto").textContent = textoGrande ? "Grande" : "Normal";
    });