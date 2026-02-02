<script setup>
import { ref } from 'vue';

// Definimos los eventos que este componente envía al padre (App.vue)
const emit = defineEmits(['login-exitoso', 'entrar-invitado']);

const esRegistro = ref(false); // Alternar entre Login y Registro
const cargando = ref(false);
const errorMsg = ref('');

// Datos del formulario
const form = ref({
  nombre: '',
  email: '',
  password: ''
});

// Llamada a TU API (Backend)
const procesarFormulario = async () => {
  errorMsg.value = '';
  cargando.value = true;
  
  const endpoint = esRegistro.value ? '/api/auth/register' : '/api/auth/login';
  const url = `http://127.0.0.1:8000${endpoint}`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    });
    
    const data = await response.json();
    
    if (!response.ok) throw new Error(data.detail || 'Error en la solicitud');
    
    // Si es registro, cambiamos a login o logueamos directamente
    if (esRegistro.value) {
        // Autologin después de registro (opcional, aquí simplificamos volviendo al login)
        esRegistro.value = false;
        errorMsg.value = "¡Cuenta creada! Ahora inicia sesión.";
        // Limpiar password
        form.value.password = '';
    } else {
        // LOGIN EXITOSO: Avisamos a App.vue
        emit('login-exitoso', data.usuario);
    }

  } catch (error) {
    errorMsg.value = error.message;
  } finally {
    cargando.value = false;
  }
};
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-slate-900 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-800 to-slate-900 p-4">
    
    <div class="w-full max-w-md bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl shadow-2xl p-8">
      
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20 text-3xl">
          ✨
        </div>
      </div>
      
      <h1 class="text-2xl font-bold text-center text-white mb-2">
        {{ esRegistro ? 'Crear Cuenta' : 'Bienvenido a IA 2.2' }}
      </h1>
      <p class="text-slate-400 text-center text-sm mb-8">
        {{ esRegistro ? 'Únete para guardar tu historial' : 'Tu asistente inteligente te espera' }}
      </p>

      <form @submit.prevent="procesarFormulario" class="space-y-4">
        
        <div v-if="esRegistro">
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Nombre</label>
          <input v-model="form.nombre" type="text" required class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-600" placeholder="Ej: Santy">
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Email</label>
          <input v-model="form.email" type="email" required class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-600" placeholder="nombre@ejemplo.com">
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Contraseña</label>
          <input v-model="form.password" type="password" required class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-600" placeholder="••••••••">
        </div>

        <div v-if="errorMsg" class="text-red-400 text-xs text-center p-2 bg-red-900/20 rounded-lg border border-red-900/50">
          {{ errorMsg }}
        </div>

        <button type="submit" :disabled="cargando" class="w-full py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed mt-2">
          {{ cargando ? 'Procesando...' : (esRegistro ? 'Registrarse' : 'Iniciar Sesión') }}
        </button>
      </form>

      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-700"></div></div>
        <div class="relative flex justify-center text-xs uppercase"><span class="bg-slate-800 px-2 text-slate-500">O continúa con</span></div>
      </div>

      <button @click="$emit('entrar-invitado')" class="w-full py-3 bg-slate-700/50 hover:bg-slate-700 text-slate-200 font-medium rounded-xl transition-all border border-slate-600/50">
        Continuar como Invitado
      </button>

      <p class="text-center text-sm text-slate-400 mt-6">
        {{ esRegistro ? '¿Ya tienes cuenta?' : '¿No tienes cuenta?' }}
        <button @click="esRegistro = !esRegistro; errorMsg=''" class="text-blue-400 hover:text-blue-300 font-semibold ml-1">
          {{ esRegistro ? 'Inicia Sesión' : 'Regístrate' }}
        </button>
      </p>

    </div>
  </div>
</template>