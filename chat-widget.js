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
      <div class="crm-chat-header">${this.options.agentName} <span class="close">×</span></div>
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
      // Determina la URL del backend de forma flexible
      const BACKEND_URL = window.BACKEND_URL ||
        ((window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
          ? "http://localhost:8090/crm-agent"
          : "/crm-agent");
      const resp = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
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
