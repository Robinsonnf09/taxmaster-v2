// auth.js - Autenticação Frontend
// NUNCA armazene tokens ou secrets no código frontend!

async function login(usuario, senha) {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuario, senha })
    });
    
    const data = await response.json();
    
    if (data.success && data.token) {
      localStorage.setItem('token', data.token);
      return true;
    }
    return false;
  } catch (error) {
    console.error('Erro no login:', error);
    return false;
  }
}

function logout() {
  localStorage.removeItem('token');
  window.location.href = '/';
}

function getToken() {
  return localStorage.getItem('token');
}
