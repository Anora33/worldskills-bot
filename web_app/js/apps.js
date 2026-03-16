// apps.js - WorldSkills Mini App JavaScript

console.log("🚀 apps.js loaded");

// Global variables
let tg = null;
let telegramId = null;

// Initialize Telegram WebApp
function initTelegram() {
    tg = window.Telegram.WebApp;
    tg.expand();
    tg.ready();
    
    const user = tg.initDataUnsafe?.user;
    telegramId = user?.id;
    
    console.log("User:", user, "ID:", telegramId);
    
    if (!telegramId) {
        showError("❌ Telegram ID topilmadi! Telegram ichida oching.");
        showDebug(`initDataUnsafe: ${JSON.stringify(tg.initDataUnsafe)}`);
    } else {
        // Auto-fill form from Telegram
        if (user.first_name) {
            const firstNameInput = document.getElementById('firstName');
            if (firstNameInput) firstNameInput.value = user.first_name;
        }
        if (user.last_name) {
            const lastNameInput = document.getElementById('lastName');
            if (lastNameInput) lastNameInput.value = user.last_name;
        }
    }
}

// Form submission handler
function setupFormSubmit() {
    const form = document.getElementById('registerForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log("📝 Form submitted");
        
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        
        // Reset UI
        if (error) error.style.display = 'none';
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
            // ✅ Dynamic backend URL
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
                const success = document.getElementById('success');
                if (success) success.style.display = 'block';
                
                // Show Telegram alert
                if (tg?.showAlert) {
                    tg.showAlert("✅ Muvaffaqiyatli ro'yxatdan o'tdingiz!");
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
            
            // Reset UI on error
            if (loading) loading.style.display = 'none';
            if (form) form.style.display = 'block';
            if (submitBtn) submitBtn.disabled = false;
            
            showError(`❌ ${err.message}\n\n🔍 Maslahat:\n• Internetni tekshiring\n• Qayta urinib ko'ring`);
            showDebug(`Error: ${err.message}\nStack: ${err.stack}\nURL: ${window.location.origin}`);
        }
    });
}

// Show error message
function showError(msg) {
    const errorDiv = document.getElementById('error');
    const errorMsg = document.getElementById('errorMessage');
    if (errorMsg) errorMsg.textContent = msg;
    if (errorDiv) errorDiv.style.display = 'block';
}

// Show debug info
function showDebug(msg) {
    const debug = document.getElementById('debugInfo');
    if (debug) {
        debug.textContent = msg;
        debug.style.display = 'block';
    }
}

// Run when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM loaded");
    initTelegram();
    setupFormSubmit();
});

// Also run if DOM already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTelegram);
} else {
    initTelegram();
}
