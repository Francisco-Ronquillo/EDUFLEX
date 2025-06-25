function mostrarFormulario(rol) {
      localStorage.setItem('rol', rol);
      document.getElementById('form-padre').classList.remove('active');
      document.getElementById('form-nino').classList.remove('active');
      document.getElementById('form-profesor').classList.remove('active');
      if (rol === 'padre') {
        document.getElementById('form-padre').classList.add('active');
      } else if (rol==='nino') {
        document.getElementById('form-nino').classList.add('active');
      }else {
          document.getElementById('form-profesor').classList.add('active');
      }
}


document.addEventListener('DOMContentLoaded', function() {
  const rolGuardado = localStorage.getItem('rol');
  if (rolGuardado) {
    mostrarFormulario(rolGuardado);
  }
});