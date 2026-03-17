// ============================================
// WorldSkills Uzbekistan - Rain Animation JS
// ============================================

console.log("🌧️ Rain Animation Loaded");

// Create rain drops
function createRain() {
    const rainContainer = document.querySelector('.rain-container');
    if (!rainContainer) return;
    
    const dropCount = 50;
    
    for (let i = 0; i < dropCount; i++) {
        const drop = document.createElement('div');
        drop.className = 'raindrop';
        drop.style.left = Math.random() * 100 + '%';
        drop.style.animationDuration = (Math.random() * 1 + 0.5) + 's';
        drop.style.animationDelay = Math.random() * 2 + 's';
        drop.style.opacity = Math.random() * 0.5 + 0.2;
        rainContainer.appendChild(drop);
    }
}

// Create floating particles
function createParticles() {
    const particleCount = 15;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.width = particle.style.height = (Math.random() * 10 + 5) + 'px';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        particle.style.animationDelay = Math.random() * 5 + 's';
        document.body.appendChild(particle);
    }
}

// Initialize rain on load
window.addEventListener('DOMContentLoaded', () => {
    createRain();
    createParticles();
    initTelegram();
});

// Global variables
let tg = null;
let telegramId = null;
let currentLang = 'uz';

// Translations
const translations = {
    uz: {
        title: "Ro'yxatdan O'tish",
        btnSubmit: "✅ Ro'yxatdan o'tish",
        loading: "Yuborilmoqda...",
        successTitle: "Muvaffaqiyatli!",
        successText: "Ro'yxatdan o'tdingiz!",
        errorTitle: "Xatolik!"
    },
    ru: {
        title: "Регистрация",
        btnSubmit: "✅ Зарегистрироваться",
        loading: "Отправка...",
        successTitle: "Успешно!",
        successText: "Вы зарегистрированы!",
        errorTitle: "Ошибка!"
    },
    en: {
        title: "Registration",
        btnSubmit: "✅ Register",
        loading: "Submitting...",
        successTitle: "Success!",
        successText: "You are registered!",
        errorTitle: "Error!"
    }
};

// Initialize Telegram
function initTelegram() {
    console.log("📱 Initializing Telegram...");
    
    try {
        tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        const user = tg.initDataUnsafe?.user;
        telegramId = user?.id;
        
        console.log("User:", user);
        console.log("ID:", telegramId);
        
        if (!telegramId) {
            showError("❌ Telegram ID topilmadi! Telegram ichida oching.");
            return false;
        }
        
        if (user.first_name) document.getElementById('firstName').value = user.first_name;
        if (user.last_name) document.getElementById('lastName').value = user.last_name;
        
        return true;
    } catch (error) {
        console.error("❌ Error:", error);
        showError("❌ Telegram xatosi: " + error.message);
        return false;
    }
}

// Form submission
function setupFormSubmit() {
    const form = document.getElementById('registerForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log("📝 Form submitted");
        
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        const success = document.getElementById('success');
        
        error.style.display = 'none';
        success.style.display = 'none';
        submitBtn.disabled = true;
        loading.style.display = 'block';
        form.style.display = 'none';
        
        const data = {
            telegramId: telegramId,
            firstName: document.getElementById('firstName')?.value || '',
            lastName: document.getElementById('lastName')?.value || '',
            phone: document.getElementById('phone')?.value || '',
            profession: document.getElementById('profession')?.value || ''
        };
        
        console.log("📤 Sending:", data);
        
        try {
            const backendUrl = window.location.origin;
            console.log("🌐 Backend:", backendUrl);
            
            const response = await fetch(`${backendUrl}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                mode: 'cors',
                body: JSON.stringify(data)
            });
            
            console.log("📥 Status:", response.status);
            
            if (!response.ok) throw new Error(`Server error: ${response.status}`);
            
            const result = await response.json();
            console.log("📥 Result:", result);
            
            if (result.success) {
                loading.style.display = 'none';
                success.style.display = 'block';
                
                if (tg?.showAlert) tg.showAlert("✅ Muvaffaqiyatli!");
                
                setTimeout(() => { if (tg?.close) tg.close(); }, 2000);
            } else {
                throw new Error(result.error || 'Failed');
            }
            
        } catch (err) {
            console.error("❌ Error:", err);
            loading.style.display = 'none';
            form.style.display = 'block';
            submitBtn.disabled = false;
            showError(`${translations[currentLang].errorTitle}\n\n${err.message}`);
        }
    });
}

// Show error
function showError(msg) {
    const errorDiv = document.getElementById('error');
    const errorMsg = document.getElementById('errorMessage');
    if (errorMsg) errorMsg.textContent = msg;
    if (errorDiv) errorDiv.style.display = 'block';
}

// Language switcher
window.changeLang = function(lang) {
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    const t = translations[lang];
    document.getElementById('title').textContent = t.title;
    document.getElementById('submitBtn').textContent = t.btnSubmit;
    document.querySelector('.loading-text').textContent = t.loading;
    document.querySelector('.success h2').textContent = t.successTitle;
    document.querySelector('.success p').textContent = t.successText;
    document.querySelector('.error h2').textContent = t.errorTitle;
    
    localStorage.setItem('ws_lang', lang);
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const initialized = initTelegram();
    if (initialized) setupFormSubmit();
    
    const savedLang = localStorage.getItem('ws_lang');
    if (savedLang && translations[savedLang]) {
        const btn = document.querySelector(`.lang-btn[onclick="changeLang('${savedLang}')"]`);
        if (btn) btn.click();
    }
});
