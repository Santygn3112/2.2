const API_URL = 'http://127.0.0.1:8000/api/chat';

export const enviarMensajeAPI = async (texto, modelo, usuario) => { 
  try {
    const response = await fetch(`${API_URL}/enviar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mensaje: texto,
        modelo: modelo,
        usuario: usuario
      }),
    });

    if (!response.ok) {
      throw new Error('Error en la respuesta del servidor');
    }

    return await response.json();
  } catch (error) {
    console.error('Error conectando con la API:', error);
    throw error;
  }
};