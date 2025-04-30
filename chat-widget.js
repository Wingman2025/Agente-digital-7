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
      <div class="crm-chat-header">${this.options.agentName}
        <span class="crm-chat-actions">
          <button class="crm-clear-btn" title="Limpiar chat" type="button">🧹</button>
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
    this.clearBtn = this.chatBox.querySelector('.crm-clear-btn');
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
    this.clearBtn.addEventListener('click', () => {
      this.clearMessages();
    });
    this.newChatBtn.addEventListener('click', () => {
      this.startNewChat();
    });
  }

  clearMessages() {
    this.messages.innerHTML = '';
  }

  startNewChat() {
    // Genera un nuevo session_id único y lo guarda en localStorage
    this.sessionId = crypto.randomUUID();
    localStorage.setItem('crm_session_id', this.sessionId);
    this.clearMessages();
    // Opcional: mostrar mensaje de bienvenida
    if (this.options.welcomeMessage) {
      this.addMessage(this.options.welcomeMessage, 'agent');
    }
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
    div.textContent = text;
    this.messages.appendChild(div);
    this.messages.scrollTop = this.messages.scrollHeight;
  }
}

// Exportar para uso con ES Modules
export default CRMChatWidget;
