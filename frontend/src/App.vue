<script setup>
import { ref, nextTick, watch } from 'vue';
import { useChat } from './composables/useChat';
import LoginScreen from './components/LoginScreen.vue';
import { onMounted } from 'vue';

// --- ESTADO DE LA APP ---
const estaLogueado = ref(false); // Controla si mostramos Login o Chat
const textoInput = ref('');
const chatContainer = ref(null); // Para el auto-scroll
const modelos = ['Gemini', 'ChatGPT', 'Claude', 'Grok']; // Opciones del dropdown

// --- LÓGICA DEL COMPOSABLE ---
const { 
  mensajes, 
  cargando, 
  enviarMensaje, 
  modeloSeleccionado, 
  usuarioActual, 
  login, 
  nuevoChat, 
  historialSesion,
  restaurarSesion
} = useChat();

// --- MANEJADORES DE LOGIN/LOGOUT ---
const alLoginExitoso = (nombreUsuario) => {
  login(nombreUsuario);
  estaLogueado.value = true;
};

const alEntrarInvitado = () => {
  login("Invitado");
  estaLogueado.value = true;
};

const cerrarSesion = () => {
  estaLogueado.value = false;
  nuevoChat(); // Limpia la pantalla actual
  login("Invitado"); // Resetea usuario
};

// --- MANEJADORES DEL CHAT ---
const manejarEnvio = async () => {
  if (!textoInput.value.trim()) return;
  
  const texto = textoInput.value;
  textoInput.value = ''; // Limpiar input
  
  await enviarMensaje(texto);
};

// Auto-scroll al fondo cuando llegan mensajes nuevos
watch(mensajes, async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
}, { deep: true });

onMounted(() => {
  const sesionRecuperada = restaurarSesion();
  if (sesionRecuperada) {
    estaLogueado.value = true; //
  }
});
</script>

<template>
  <LoginScreen 
    v-if="!estaLogueado" 
    @login-exitoso="alLoginExitoso" 
    @entrar-invitado="alEntrarInvitado"
  />

  <div v-else class="flex h-screen bg-slate-900 text-gray-100 font-sans overflow-hidden">
    
    <aside class="hidden md:flex flex-col w-64 bg-slate-800/50 border-r border-slate-700/50 p-4">
      
      <div class="mb-8 flex items-center gap-2">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">✨</div>
        <h1 class="font-bold text-xl tracking-wide">IA 2.2</h1>
      </div>
      
      <button 
        @click="nuevoChat" 
        class="flex items-center gap-3 px-4 py-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition-all shadow-lg mb-6 text-sm font-medium border border-slate-600/50 group"
      >
        <span class="group-hover:rotate-90 transition-transform duration-300">+</span> Nuevo Chat
      </button>

      <div class="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
        <p v-if="historialSesion.length === 0" class="text-xs text-slate-500 text-center mt-4 italic">
          Tu historial aparecerá aquí...
        </p>
        
        <div 
          v-for="chat in historialSesion" 
          :key="chat.id" 
          class="p-3 text-sm text-slate-300 bg-slate-800/30 hover:bg-slate-700/50 rounded-lg cursor-pointer transition-colors border border-transparent hover:border-slate-600/50"
        >
          <div class="font-medium truncate">{{ chat.titulo }}</div>
          <div class="text-[10px] uppercase font-bold text-slate-500 mt-1">{{ chat.modelo }}</div>
        </div>
      </div>
      
      <div class="mt-auto pt-4 border-t border-slate-700/50 flex items-center justify-between gap-2 p-1">
        <div class="flex items-center gap-3 overflow-hidden">
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center font-bold text-xs shadow-inner shrink-0">
            {{ usuarioActual.charAt(0).toUpperCase() }}
          </div>
          <div class="text-xs truncate">
            <p class="font-medium text-white truncate">{{ usuarioActual }}</p>
          </div>
        </div>
        
        <button 
          @click="cerrarSesion" 
          class="text-slate-500 hover:text-red-400 hover:bg-red-500/10 p-2 rounded-lg transition-all" 
          title="Cerrar Sesión"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
        </button>
      </div>
    </aside>

    <main class="flex-1 flex flex-col relative bg-gradient-to-b from-slate-900 via-slate-900 to-slate-800">
      
      <header class="absolute top-4 left-0 right-0 z-10 flex justify-center pointer-events-none">
        <div class="pointer-events-auto bg-slate-800/80 backdrop-blur-xl border border-slate-700/50 rounded-full px-5 py-2 shadow-2xl flex items-center gap-3 hover:border-slate-600 transition-colors">
          <span class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Modelo</span>
          <div class="h-4 w-px bg-slate-700"></div>
          <select 
            v-model="modeloSeleccionado" 
            class="bg-transparent text-sm font-medium text-white focus:outline-none cursor-pointer appearance-none pr-4"
            style="background-image: none;"
          >
            <option v-for="mod in modelos" :key="mod" :value="mod" class="bg-slate-800 text-slate-200">
              {{ mod }}
            </option>
          </select>
          <span class="text-slate-500 text-xs">▼</span>
        </div>
      </header>

      <div 
        ref="chatContainer" 
        class="flex-1 p-4 pt-24 overflow-y-auto space-y-6 scroll-smooth custom-scrollbar"
      >
        <div v-if="mensajes.length === 0" class="h-full flex flex-col items-center justify-center opacity-60 animate-in fade-in duration-700">
            <div class="text-7xl mb-6 grayscale opacity-50">🤖</div>
            <h2 class="text-3xl font-bold mb-3 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Hola, {{ usuarioActual }}
            </h2>
            <p class="text-slate-400 text-lg font-light">
              Estoy listo. ¿Probamos el modelo <span class="font-bold text-slate-200">{{ modeloSeleccionado }}</span>?
            </p>
        </div>

        <div 
          v-for="msg in mensajes" 
          :key="msg.id" 
          class="flex w-full animate-in slide-in-from-bottom-2 duration-300"
          :class="msg.emisor === 'usuario' ? 'justify-end' : 'justify-start'"
        >
          <div 
            class="max-w-[85%] md:max-w-[70%] p-4 rounded-2xl shadow-lg leading-relaxed relative group"
            :class="msg.emisor === 'usuario' 
              ? 'bg-blue-600 text-white rounded-br-sm' 
              : 'bg-slate-800 border border-slate-700 text-slate-100 rounded-bl-sm'"
          >
            <div v-if="msg.emisor === 'ia'" class="flex items-center gap-2 mb-2 pb-2 border-b border-white/5">
               <span class="text-[10px] font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1">
                 <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span> {{ modeloSeleccionado }}
               </span>
               <span class="text-[10px] text-slate-500 ml-auto">{{ new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
            </div>

            <p class="whitespace-pre-wrap">{{ msg.texto }}</p>
            
            <div v-if="msg.esError" class="mt-2 text-xs text-red-300 flex items-center gap-1 bg-red-500/10 p-1 rounded">
              ⚠️ No se pudo guardar
            </div>
          </div>
        </div>

        <div v-if="cargando" class="flex justify-start w-full px-4">
           <div class="bg-slate-800 border border-slate-700 px-4 py-3 rounded-2xl rounded-bl-none flex items-center gap-2 shadow-lg">
             <span class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></span>
             <span class="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-150"></span>
             <span class="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-300"></span>
           </div>
        </div>
      </div>

      <div class="p-4 md:p-6 w-full max-w-4xl mx-auto z-20">
        <div 
          class="relative flex items-end bg-slate-800/90 backdrop-blur-md rounded-2xl border border-slate-700/50 shadow-2xl transition-all focus-within:ring-2 focus-within:ring-blue-500/50 focus-within:border-blue-500/50"
        >
          <input 
            v-model="textoInput"
            @keyup.enter="manejarEnvio"
            :disabled="cargando"
            type="text" 
            :placeholder="`Envía un mensaje a ${modeloSeleccionado}...`" 
            class="w-full bg-transparent border-none p-4 min-h-[60px] text-white placeholder-slate-500 focus:outline-none disabled:opacity-50"
          />
          
          <button 
            @click="manejarEnvio"
            :disabled="!textoInput.trim() || cargando"
            class="m-2 p-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-xl transition-all shadow-lg hover:shadow-blue-500/20 active:scale-95"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          </button>
        </div>
        <p class="text-center text-[10px] text-slate-600 mt-3 font-medium">
          IA 2.2 Proyecto DAM • Acceso a Datos • Puede cometer errores.
        </p>
      </div>

    </main>
  </div>
</template>

<style>
/* Personalización de la barra de scroll para Webkit (Chrome/Edge/Safari) */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #334155; /* Slate-700 */
  border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #475569; /* Slate-600 */
}
</style>