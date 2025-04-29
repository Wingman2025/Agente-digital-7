// Widget de chat CRM simple para el home page
const chatBtn = document.createElement('button');
chatBtn.className = 'crm-chat-btn';
chatBtn.innerText = '💬 Habla con tu agente CRM';

document.body.appendChild(chatBtn);

const chatBox = document.createElement('div');
chatBox.className = 'crm-chat-box';
chatBox.innerHTML = `
  <div class="crm-chat-header">Agente CRM <span class="close">×</span></div>
  <div class="crm-chat-messages"></div>
  <form class="crm-chat-form">
    <input type="text" placeholder="Escribe tu mensaje..." required />
    <button type="submit">Enviar</button>
  </form>
`;
chatBox.style.display = 'none';
document.body.appendChild(chatBox);

// Mostrar/ocultar chat
chatBtn.onclick = () => {
  chatBox.style.display = 'block';
  chatBtn.style.display = 'none';
};
chatBox.querySelector('.close').onclick = () => {
  chatBox.style.display = 'none';
  chatBtn.style.display = 'block';
};

// Lógica de mensajes (simulado)
const messages = chatBox.querySelector('.crm-chat-messages');
const form = chatBox.querySelector('.crm-chat-form');
form.onsubmit = async (e) => {
  e.preventDefault();
  const input = form.querySelector('input');
  const userMsg = input.value;
  messages.innerHTML += `<div class='msg user'>${userMsg}</div>`;
  input.value = '';
  messages.scrollTop = messages.scrollHeight;

  // Simulación de respuesta del agente
  messages.innerHTML += `<div class='msg agent'>Estoy aquí para ayudarte con tu CRM. (Integración backend pendiente)</div>`;
  messages.scrollTop = messages.scrollHeight;
};
