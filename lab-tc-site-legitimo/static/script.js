/* ============================================
   SIMULAÇÃO ACADÊMICA - SEGURANÇA DA INFORMAÇÃO
   JavaScript Principal

   Este script gerencia:
   - Animação de carregamento da página
   - Validação do formulário de login (client-side)
   - Animação de loading no botão de envio
   - Lógica do dashboard (página home)
   ============================================ */

// --- Page Loader ---
// Remove a animação de carregamento após o DOM estar pronto
document.addEventListener('DOMContentLoaded', () => {
  const loader = document.querySelector('.page-loader');
  if (loader) {
    setTimeout(() => {
      loader.classList.add('hidden');
      setTimeout(() => loader.remove(), 500);
    }, 600);
  }
});

// --- LOGIN PAGE LOGIC ---
function initLoginPage() {
  const form = document.getElementById('loginForm');
  const usuarioInput = document.getElementById('usuario');
  const senhaInput = document.getElementById('senha');
  const loginBtn = document.getElementById('loginBtn');

  // Se o formulário não existir nesta página, sair
  if (!form) return;

  // Limpa mensagens de erro quando o usuário começa a digitar
  [usuarioInput, senhaInput].forEach(input => {
    input.addEventListener('input', () => {
      input.closest('.form-group').classList.remove('error');
    });

    input.addEventListener('focus', () => {
      input.closest('.form-group').classList.remove('error');
    });
  });

  // Intercepta o envio do formulário para validação client-side
  form.addEventListener('submit', (e) => {
    e.preventDefault(); // bloqueia envio padrão

    let hasError = false;

    // Valida campo de usuário/e-mail
    if (!usuarioInput.value.trim()) {
      usuarioInput.closest('.form-group').classList.add('error');
      hasError = true;
    }

    // Valida campo de senha
    if (!senhaInput.value.trim()) {
      senhaInput.closest('.form-group').classList.add('error');
      hasError = true;
    }

    // Se houver erro, não envia
    if (hasError) return;

    // Mostra a animação de loading no botão
    loginBtn.classList.add('loading');
    loginBtn.disabled = true;

    // Armazena dados na sessão do navegador para uso no dashboard
    const userEmail = usuarioInput.value.trim();
    const userName = userEmail.split('@')[0];
    const displayName = userName.charAt(0).toUpperCase() + userName.slice(1);

    sessionStorage.setItem('loggedIn', 'true');
    sessionStorage.setItem('userName', displayName);
    sessionStorage.setItem('userEmail', userEmail);
    sessionStorage.setItem('loginTime', new Date().toLocaleString('pt-BR'));

    // 🔥 Força envio real do formulário via POST para /login
    form.submit();
  });
}

// --- HOME PAGE LOGIC ---
function initHomePage() {
  const page = document.querySelector('.dashboard-page');
  if (!page) return;

  // -------------------------------------------------------
  // Faz um GET para /login/check para transmitir os cookies
  // de sessão via GET (visível em capturas de rede)
  // -------------------------------------------------------
  fetch('/login/check', { credentials: 'same-origin' })
    .then(res => res.json())
    .then(data => {
      console.log('[SecureBank] Sessão verificada:', data);
    })
    .catch(err => {
      console.log('[SecureBank] Erro ao verificar sessão:', err);
    });

  // Popula dados do usuário a partir da sessão do navegador
  const userName = sessionStorage.getItem('userName') || 'Usuário';
  const userEmail = sessionStorage.getItem('userEmail') || 'usuario@email.com';
  const loginTime = sessionStorage.getItem('loginTime') || new Date().toLocaleString('pt-BR');

  // Mensagem de boas-vindas
  const welcomeEl = document.getElementById('welcomeName');
  if (welcomeEl) {
    welcomeEl.textContent = userName;
  }

  // Iniciais do avatar
  const avatarEls = document.querySelectorAll('.avatar-initials');
  avatarEls.forEach(el => {
    el.textContent = userName.charAt(0).toUpperCase();
  });

  // Nome do usuário na navbar
  const navNameEl = document.getElementById('navUserName');
  if (navNameEl) navNameEl.textContent = userName;

  // E-mail do usuário
  const navEmailEl = document.getElementById('navUserEmail');
  if (navEmailEl) navEmailEl.textContent = userEmail;

  // Último acesso
  const lastAccessEl = document.getElementById('lastAccess');
  if (lastAccessEl) lastAccessEl.textContent = loginTime;

  // Saudação dinâmica baseada no horário
  const greetingEl = document.getElementById('greeting');
  if (greetingEl) {
    const hour = new Date().getHours();
    let greeting = 'Bom dia';
    if (hour >= 12 && hour < 18) greeting = 'Boa tarde';
    else if (hour >= 18 || hour < 6) greeting = 'Boa noite';
    greetingEl.textContent = greeting;
  }

  // Toggle do menu mobile
  const menuToggle = document.getElementById('menuToggle');
  const navLinks = document.getElementById('navLinks');
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
      });
    });
  }

  // Botão de logout — redireciona para a página de login
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      sessionStorage.clear();
      window.location.href = '/';
    });
  }

  // Anima os números das estatísticas
  animateStatNumbers();
}

// --- Animação dos números das estatísticas ---
function animateStatNumbers() {
  const statValues = document.querySelectorAll('.stat-value[data-value]');
  statValues.forEach(el => {
    const target = el.getAttribute('data-value');
    const isMonetary = target.includes('R$') || target.includes(',');

    if (isMonetary) {
      // Valores monetários — fade in simples
      el.style.opacity = '0';
      setTimeout(() => {
        el.textContent = target;
        el.style.transition = 'opacity 0.5s ease';
        el.style.opacity = '1';
      }, 300);
    } else {
      // Valores numéricos — contagem animada
      const targetNum = parseInt(target.replace(/\D/g, ''));
      if (isNaN(targetNum)) {
        el.textContent = target;
        return;
      }

      const suffix = target.replace(/[\d]/g, '');
      let current = 0;
      const increment = Math.ceil(targetNum / 40);
      const timer = setInterval(() => {
        current += increment;
        if (current >= targetNum) {
          current = targetNum;
          clearInterval(timer);
        }
        el.textContent = current + suffix;
      }, 30);
    }
  });
}

// --- Handler para "Esqueci minha senha" ---
function handleForgotPassword(e) {
  e.preventDefault();
  alert('Um link de recuperação foi enviado para o seu e-mail cadastrado.');
}

// --- Inicializa a lógica da página correta ---
document.addEventListener('DOMContentLoaded', () => {
  initLoginPage();
  initHomePage();
});
