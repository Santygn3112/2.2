import { ref, onMounted } from 'vue';
import { enviarMensajeAPI } from '../api/chatApi';

export function useChat() {
  const mensajes = ref([]);
  const cargando = ref(false);
  const modeloSeleccionado = ref('Gemini');
  const usuarioActual = ref('Invitado');    
  const historialSesion = ref([]);          

  const SESSION_KEY = 'ia22_session';
  const EXPIRATION_TIME = 24 * 60 * 60 * 1000;

  // Al cargar la app comprobamos si hay sesión guardada
  const restaurarSesion = () => {
    const sesionGuardada = localStorage.getItem(SESSION_KEY);
    
    if (sesionGuardada) {
      try {
        const data = JSON.parse(sesionGuardada);
        const ahora = new Date().getTime();

        // Si la sesión no ha caducado
        if (ahora < data.expiracion) {
          usuarioActual.value = data.usuario;
          return true; 
        } else {
          // Si caducó limpiamos
          localStorage.removeItem(SESSION_KEY);
        }
      } catch (e) {
        localStorage.removeItem(SESSION_KEY);
      }
    }
    return false;
  };

  const enviarMensaje = async (texto) => {
    if (!texto.trim()) return;

    const nuevoMensajeUsuario = {
      id: Date.now().toString(),
      texto: texto,
      emisor: 'usuario',
      timestamp: new Date()
    };
    mensajes.value.push(nuevoMensajeUsuario);

    cargando.value = true;

    try {
      const respuestaBackend = await enviarMensajeAPI(
        texto, 
        modeloSeleccionado.value, 
        usuarioActual.value
      );

      mensajes.value.push({
        id: respuestaBackend.id_conversacion || Date.now() + 1,
        texto: respuestaBackend.respuesta,
        emisor: 'ia',
        timestamp: new Date(respuestaBackend.timestamp)
      });

    } catch (error) {
      mensajes.value.push({
        id: 'err-' + Date.now(),
        texto: 'Error de conexión con el modelo ' + modeloSeleccionado.value,
        emisor: 'ia',
        esError: true
      });
    } finally {
      cargando.value = false;
    }
  };

  const nuevoChat = () => {
    if (mensajes.value.length > 0) {
      historialSesion.value.unshift({
        id: Date.now(),
        titulo: mensajes.value[0].texto.substring(0, 20) + '...',
        modelo: modeloSeleccionado.value
      });
    }
    mensajes.value = []; 
  };

  // Guarda en localStorage al hacer login
  const login = (nombre) => {
    usuarioActual.value = nombre;
    
    if (nombre !== 'Invitado') {
      const datosSesion = {
        usuario: nombre,
        expiracion: new Date().getTime() + EXPIRATION_TIME
      };
      localStorage.setItem(SESSION_KEY, JSON.stringify(datosSesion));
    } else {
      localStorage.removeItem(SESSION_KEY);
    }
  };

  return {
    mensajes,
    cargando,
    modeloSeleccionado,
    usuarioActual,
    historialSesion,
    enviarMensaje,
    nuevoChat,
    login,
    restaurarSesion 
  };
}