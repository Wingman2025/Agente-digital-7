// chat-widget.js
// Widget de chat CRM modular y moderno

class CRMChatWidget {
  constructor(options = {}) {
    this.options = Object.assign({
      agentName: 'Agente CRM',
      welcomeMessage: 'Estoy aquí para ayudarte con tu CRM. (Integración backend pendiente)',
      buttonText: '💬 Habla con tu agente CRM',
    }, options);
    this.init();
    // Session ID para historial compartido
    this.sessionId = localStorage.getItem('crm_session_id') || crypto.randomUUID();
    localStorage.setItem('crm_session_id', this.sessionId);
    // Carga historial del servidor
    this.loadServerHistory();
  }

  init() {
    this.createButton();
    this.createChatBox();
    this.attachEvents();
  }

  createButton() {
    this.chatBtn = document.createElement('button');
    this.chatBtn.className = 'crm-chat-btn';
    this.chatBtn.innerText = this.options.buttonText;
    document.body.appendChild(this.chatBtn);
  }

  createChatBox() {
    this.chatBox = document.createElement('div');
    this.chatBox.className = 'crm-chat-box';
    this.chatBox.innerHTML = `
      <div class="crm-chat-header">
        <img src="assets/logo.png" alt="Logo agente" class="crm-agent-logo" style="height:32px;vertical-align:middle;margin-right:8px;">
        ${this.options.agentName}
        <span class="crm-chat-actions">
          <button class="crm-newchat-btn" title="Nuevo chat" type="button">🆕</button>
          <span class="close">×</span>
        </span>
      </div>
      <div class="crm-chat-messages"></div>
      <form class="crm-chat-form">
        <input type="text" placeholder="Escribe tu mensaje..." required />
        <button type="submit">Enviar</button>
      </form>
    `;
    this.chatBox.style.display = 'none';
    document.body.appendChild(this.chatBox);
    this.messages = this.chatBox.querySelector('.crm-chat-messages');
    this.form = this.chatBox.querySelector('.crm-chat-form');
    this.input = this.form.querySelector('input');
    this.newChatBtn = this.chatBox.querySelector('.crm-newchat-btn');
  }

  attachEvents() {
    this.chatBtn.addEventListener('click', () => {
      this.chatBox.style.display = 'block';
      this.chatBtn.style.display = 'none';
    });
    this.chatBox.querySelector('.close').addEventListener('click', () => {
      this.chatBox.style.display = 'none';
      this.chatBtn.style.display = 'block';
    });
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.sendMessage(this.input.value);
      this.input.value = '';
    });
    this.newChatBtn.addEventListener('click', () => {
      this.startNewChat();
    });
  }

  startNewChat() {
    // Genera un nuevo session_id único y lo guarda en localStorage
    this.sessionId = crypto.randomUUID();
    localStorage.setItem('crm_session_id', this.sessionId);
    this.messages.innerHTML = '';
    // No carga historial del servidor, chat vacío
  }

  async sendMessage(text) {
    if (!text.trim()) return;
    this.addMessage(text, 'user');
    // Mostrar indicador de carga
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'msg agent';
    loadingMsg.textContent = '...';
    this.messages.appendChild(loadingMsg);
    this.messages.scrollTop = this.messages.scrollHeight;
    try {
      console.log('Enviando mensaje al backend CRM:', text);
      // Enviar con session_id y URL base del backend
      const base = this.getBackendBase();
      const resp = await fetch(`${base}/crm-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: this.sessionId, message: text })
      });
      console.log('Status de respuesta:', resp.status);
      const data = await resp.json();
      console.log('Respuesta del agente CRM:', data);
      loadingMsg.remove();
      this.addMessage(data.reply, 'agent');
    } catch (e) {
      console.error('Error al conectar con el agente CRM:', e);
      loadingMsg.remove();
      this.addMessage('Error al conectar con el agente CRM.', 'agent');
    }
  }

  // Devuelve la URL base del backend
  getBackendBase() {
    return window.BACKEND_URL ||
      ((location.hostname === 'localhost' || location.hostname === '127.0.0.1')
        ? 'http://localhost:8090'
        : '');
  }

  // Carga el historial desde el servidor
  async loadServerHistory() {
    try {
      const resp = await fetch(`${this.getBackendBase()}/history/${this.sessionId}`);
      const { messages } = await resp.json();
      messages.forEach(m => this.addMessage(m.text, m.type));
    } catch (e) {
      console.error('Error cargando historial:', e);
    }
  }

  addMessage(text, type) {
    const div = document.createElement('div');
    div.className = `msg ${type}`;
    // Detectar URLs y convertirlas en enlaces clicables
    div.innerHTML = this.linkify(text);
    this.messages.appendChild(div);
    this.messages.scrollTop = this.messages.scrollHeight;
  }

  // Convierte URLs en texto en enlaces HTML
  linkify(text) {
    // Regex para URLs (http/https)
    return text.replace(/(https?:\/\/[^\s]+)/g, function(url) {
      let label = url;
      // WhatsApp
      if (url.startsWith('https://wa.me/')) {
        label = 'Ir a WhatsApp';
      } else {
        // Mostrar solo dominio
        try {
          const u = new URL(url);
          label = u.hostname + '...';
        } catch {
          label = url;
        }
      }
      return `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`;
    });
  }
}

// Exportar para uso con ES Modules
export default CRMChatWidget;
