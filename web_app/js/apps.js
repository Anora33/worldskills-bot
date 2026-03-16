// ============================================
// WorldSkills Uzbekistan - Modern JavaScript
// ============================================

// Global variables
let tg = null;
let telegramId = null;
let currentLang = 'uz';

// Translations
const translations = {
    uz: {
        title: "Ro'yxatdan O'tish",
        subtitle: "WorldSkills Uzbekistan",
        labelFirstName: "👤 Ism:",
        placeholderFirstName: "Ismingizni kiriting",
        labelLastName: "👤 Familiya:",
        placeholderLastName: "Familiyangizni kiriting",
        labelPhone: "📱 Telefon:",
        placeholderPhone: "+998901234567",
        labelProfession: "🎓 Yo'nalish:",
        selectProfession: "Tanlang...",
        btnSubmit: "✅ Ro'yxatdan o'tish",
        loading: "Yuborilmoqda...",
        successTitle: "Muvaffaqiyatli!",
        successText: "Ro'yxatdan o'tdingiz!",
        errorTitle: "Xatolik!",
        ball: "ball"
    },
    ru: {
        title: "Регистрация",
        subtitle: "WorldSkills Uzbekistan",
        labelFirstName: "👤 Имя:",
        placeholderFirstName: "Введите имя",
        labelLastName: "👤 Фамилия:",
        placeholderLastName: "Введите фамилию",
        labelPhone: "📱 Телефон:",
        placeholderPhone: "+998901234567",
        labelProfession: "🎓 Направление:",
        selectProfession: "Выберите...",
        btnSubmit: "✅ Зарегистрироваться",
        loading: "Отправка...",
        successTitle: "Успешно!",
        successText: "Вы зарегистрированы!",
        errorTitle: "Ошибка!",
        ball: "баллов"
    },
    en: {
        title: "Registration",
        subtitle: "WorldSkills Uzbekistan",
        labelFirstName: "👤 First Name:",
        placeholderFirstName: "Enter your name",
        labelLastName: "👤 Last Name:",
        placeholderLastName: "Enter surname",
        labelPhone: "📱 Phone:",
        placeholderPhone: "+998901234567",
        labelProfession: "🎓 Direction:",
        selectProfession: "Select...",
        btnSubmit: "✅ Register",
        loading: "Submitting...",
        successTitle: "Success!",
        successText: "You are registered!",
        errorTitle: "Error!",
        ball: "points"
    }
};

// Initialize Telegram WebApp
function initTelegram() {
    console.log("🚀 Initializing Telegram WebApp...");
    
    tg = window.Telegram.WebApp;
    tg.expand();
    tg.ready();
    
    const user = tg.initDataUnsafe?.user;
    telegramId = user?.id;
    
    console.log("User:", user);
    console.log("Telegram ID:", telegramId);
    
    if (!telegramId) {
        showError("❌ Telegram ID topilmadi! Telegram ichida oching.");
        showDebug(`initDataUnsafe: ${JSON.stringify(tg.initDataUnsafe, null, 2)}`);
        return false;
    }
    
    // Auto-fill form
    if (user.first_name) {
        document.getElementById('firstName').value = user.first_name;
    }
    if (user.last_name) {
        document.getElementById('lastName').value = user.last_name;
    }
    
    return true;
}

// Language switcher
function changeLang(lang) {
    currentLang = lang;
    
    // Update buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update texts
    const t = translations[lang];
    document.getElementById('title').textContent = t.title;
    document.querySelector('.subtitle').textContent = t.subtitle;
    document.querySelector('[for="firstName"]').textContent = t.labelFirstName;
    document.getElementById('firstName').placeholder = t.placeholderFirstName;
    document.querySelector('[for="lastName"]').textContent = t.labelLastName;
    document.getElementById('lastName').placeholder = t.placeholderLastName;
    document.querySelector('[for="phone"]').textContent = t.labelPhone;
    document.getElementById('phone').placeholder = t.placeholderPhone;
    document.querySelector('[for="profession"]').textContent = t.labelProfession;
    document.getElementById('submitBtn').textContent = t.btnSubmit;
    document.querySelector('.loading-text').textContent = t.loading;
    document.querySelector('.success h2').textContent = t.successTitle;
    document.querySelector('.success p').textContent = t.successText;
    document.querySelector('.error h2').textContent = t.errorTitle;
    
    // Save preference
    localStorage.setItem('ws_lang', lang);
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
        
        // Reset UI
        if (error) error.style.display = 'none';
        if (success) success.style.display = 'none';
        if (submitBtn) submitBtn.disabled = true;
        if (loading) loading.style.display = 'block';
        if (form) form.style.display = 'none';
        
        // Collect data
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
                headers: { 
                    'Content-Type': 'application/json', 
                    'Accept': 'application/json' 
                },
                mode: 'cors',
                body: JSON.stringify(data)
            });
            
            console.log("📥 Status:", response.status);
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const result = await response.json();
            console.log("📥 Result:", result);
            
            if (result.success) {
                // Show success
                if (loading) loading.style.display = 'none';
                if (success) success.style.display = 'block';
                
                // Telegram alert
                if (tg?.showAlert) {
                    tg.showAlert(translations[currentLang].successTitle + " " + translations[currentLang].successText);
                }
                
                // Close after 2 seconds
                setTimeout(() => {
                    if (tg?.close) tg.close();
                }, 2000);
            } else {
                throw new Error(result.error || 'Registration failed');
            }
            
        } catch (err) {
            console.error("❌ Error:", err);
            
            // Reset UI
            if (loading) loading.style.display = 'none';
            if (form) form.style.display = 'block';
            if (submitBtn) submitBtn.disabled = false;
            
            showError(`${translations[currentLang].errorTitle}\n\n${err.message}`);
            showDebug(`Error: ${err.message}\nStack: ${err.stack}\nURL: ${window.location.origin}`);
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

// Show debug
function showDebug(msg) {
    const debug = document.getElementById('debugInfo');
    if (debug) {
        debug.textContent = msg;
        debug.style.display = 'block';
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM loaded");
    
    const initialized = initTelegram();
    if (initialized) {
        setupFormSubmit();
    }
    
    // Load saved language
    const savedLang = localStorage.getItem('ws_lang');
    if (savedLang && translations[savedLang]) {
        // Find and click the button
        const btn = document.querySelector(`.lang-btn[onclick="changeLang('${savedLang}')"]`);
        if (btn) btn.click();
    }
});

// Export functions
window.changeLang = changeLang;
