function mostrarFormulario(rol) {
      localStorage.setItem('rol', rol);
      document.getElementById('form-padre').classList.remove('active');
      document.getElementById('form-nino').classList.remove('active');
      document.getElementById('form-profesor').classList.remove('active');
      limpiarInputsLogin(rol);
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

function limpiarInputsLogin(rol) {
  const usuario = document.getElementById('usuario_' + rol);
  const clave = document.getElementById('clave_' + rol);
  if (usuario) usuario.value = '';
  if (clave) clave.value = '';
}