// api-config.js - Configuração de API Frontend
// NUNCA coloque API keys ou secrets aqui! Este arquivo é público!

const API_CONFIG = {
  baseURL: window.location.origin + '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
};

// API keys devem ser gerenciadas exclusivamente no backend!
