// WorldSkills Shanghai 2026 - 64 Professions
console.log("🏆 WorldSkills App Loaded");

// 64 Professions by Category
const PROFESSIONS = {
    "🏭 Ishlab chiqarish va Muhandislik": [
        "Industrial Mechanics | Sanoat mexanikasi",
        "Mechatronics | Mexatronika",
        "Mechanical Engineering CAD | Mexanik muhandislik CAD",
        "CNC Turning | CNC tokarlik ishlovi",
        "CNC Milling | CNC frezalash",
        "Welding | Payvandlash",
        "Electronics | Elektronika",
        "Industrial Control | Sanoat boshqaruvi",
        "Autonomous Mobile Robotics | Avtonom mobil robototexnika",
        "Industry 4.0 | Sanoat 4.0 texnologiyalari",
        "Chemical Laboratory Technology | Kimyo laboratoriya texnologiyasi",
        "Water Technology | Suv texnologiyasi",
        "Additive Manufacturing | 3D chop etish",
        "Industrial Design Technology | Sanoat dizayn texnologiyasi",
        "Optoelectronic Technology | Optoelektron texnologiya",
        "Renewable Energy | Qayta tiklanuvchi energiya",
        "Robot Systems Integration | Robot tizimlarini integratsiyalash"
    ],
    "💻 Axborot va Kommunikatsiya": [
        "ICT Network Infrastructure | AKT tarmoq infratuzilmasi",
        "Mobile Applications Development | Mobil ilovalar ishlab chiqish",
        "Software Applications Development | Dasturiy ta'minot ishlab chiqish",
        "Web Technologies | Veb texnologiyalar",
        "IT Network Systems Administration | Kompyuter tarmoqlarini boshqarish",
        "Cloud Computing | Bulutli hisoblash",
        "Cyber Security | Kiberxavfsizlik",
        "Software Testing | Dasturiy ta'minotni sinash"
    ],
    "🏗️ Qurilish va Bino Texnologiyalari": [
        "Wall and Floor Tiling | Devor va pol plitkalash",
        "Plumbing and Heating | Santexnika va isitish tizimlari",
        "Electrical Installations | Elektr o'rnatish ishlari",
        "Bricklaying | G'isht terish",
        "Plastering and Drywall Systems | Suvoq va gipsokarton tizimlari",
        "Painting and Decorating | Bo'yash va bezatish",
        "Cabinetmaking | Shkaf yasash duradgorlik",
        "Joinery | Duradgorlik yig'ish ishlari",
        "Carpentry | Duradgorlik yog'och ishlari",
        "Landscape Gardening | Landshaft bog'dorchiligi",
        "Refrigeration and Air Conditioning | Sovutish va konditsioner tizimlari",
        "Concrete Construction Work | Beton qurilish ishlari",
        "Digital Construction | Raqamli qurilish",
        "Intelligent Security Technology | Aqlli xavfsizlik texnologiyalari"
    ],
    "🚚 Transport va Logistika": [
        "Autobody Repair | Avtomobil kuzovini ta'mirlash",
        "Aircraft Maintenance | Samolyotlarga texnik xizmat",
        "Automobile Technology | Avtomobil texnologiyasi",
        "Car Painting | Avtomobil bo'yash",
        "Heavy Vehicle Technology | Og'ir transport texnologiyasi",
        "Logistics and Freight Forwarding | Logistika va yuk tashish",
        "Rail Vehicle Technology | Temiryo'l transporti texnologiyasi",
        "Unmanned Aerial Systems | Uchuvchisiz uchish apparatlari"
    ],
    "🎨 Ijodiy San'at va Moda": [
        "Jewellery | Zargarlik",
        "Floristry | Gulchilik san'ati",
        "Fashion Technology | Moda texnologiyasi",
        "Graphic Design Technology | Grafik dizayn texnologiyasi",
        "Visual Merchandising | Vizual savdo bezagi",
        "3D Digital Game Art | 3D raqamli o'yin san'ati",
        "Digital Interactive Media Design | Raqamli interaktiv media dizayni"
    ],
    "👥 Ijtimoiy va Shaxsiy Xizmatlar": [
        "Hairdressing | Sartaroshlik",
        "Beauty Therapy | Go'zallik terapiyasi",
        "Pâtisserie and Confectionery | Pishiriqlar va shirinliklar",
        "Cooking | Oshpazlik",
        "Restaurant Service | Restoran xizmati",
        "Health and Social Care | Sog'liqni saqlash va ijtimoiy g'amxo'rlik",
        "Bakery | Nonvoychilik",
        "Hotel Reception | Mehmonxona qabulxonasi",
        "Dental Prosthetics | Tish protezlash",
        "Retail Sales | Chakana savdo"
    ]
};

// Global variables
let tg = null;
let telegramId = null;
let selectedProfession = "";
let currentLang = "uz";

// Translations
const translations = {
    uz: {
        title: "Ro'yxatdan O'tish",
        subtitle: "WorldSkills Shanghai 2026",
        btnSubmit: "Ro'yxatdan O'tish",
        loading: "Yuborilmoqda...",
        successTitle: "Muvaffaqiyatli!",
        successText: "Ro'yxatdan o'tdingiz!",
        errorTitle: "Xatolik!",
        selectCategory: "🎓 Kompetensiya Kategoriyasi",
        selectProfession: "🎓 Kompetensiyani tanlang",
        professionPlaceholder: "Kategoriyadan tanlang..."
    },
    ru: {
        title: "Регистрация",
        subtitle: "WorldSkills Shanghai 2026",
        btnSubmit: "Зарегистрироваться",
        loading: "Отправка...",
        successTitle: "Успешно!",
        successText: "Вы зарегистрированы!",
        errorTitle: "Ошибка!",
        selectCategory: "🎓 Категория компетенции",
        selectProfession: "🎓 Выберите компетенцию",
        professionPlaceholder: "Выберите из категории..."
    },
    en: {
        title: "Registration",
        subtitle: "WorldSkills Shanghai 2026",
        btnSubmit: "Register",
        loading: "Submitting...",
        successTitle: "Success!",
        successText: "You are registered!",
        errorTitle: "Error!",
        selectCategory: "🎓 Skill Category",
        selectProfession: "🎓 Select Skill",
        professionPlaceholder: "Select from category..."
    }
};

// Initialize
function initTelegram() {
    try {
        tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        const user = tg.initDataUnsafe?.user;
        telegramId = user?.id;
        
        if (!telegramId) {
            showError("❌ Telegram ID topilmadi!");
            return false;
        }
        
        if (user.first_name) document.getElementById('firstName').value = user.first_name;
        if (user.last_name) document.getElementById('lastName').value = user.last_name;
        
        // Show form with profession selector
        document.getElementById('registerForm').style.display = 'block';
        return true;
    } catch (error) {
        console.error("❌ Error:", error);
        showError("❌ Telegram xatosi: " + error.message);
        return false;
    }
}

// Show category selection
function showCategoryStep() {
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('categoryStep').style.display = 'block';
    document.getElementById('professionStep').style.display = 'none';
    
    const list = document.getElementById('categoryList');
    list.innerHTML = '';
    
    Object.keys(PROFESSIONS).forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'btn';
        btn.style.padding = '14px';
        btn.style.background = '#f5f5f5';
        btn.style.color = '#000';
        btn.style.border = '2px solid #d0d0d0';
        btn.style.borderRadius = '12px';
        btn.style.textAlign = 'left';
        btn.innerHTML = `<strong>${category}</strong><br><small style="color:#666">${PROFESSIONS[category].length} ta kompetensiya</small>`;
        btn.onclick = () => showProfessionStep(category);
        list.appendChild(btn);
    });
}

// Show profession selection
function showProfessionStep(category) {
    document.getElementById('categoryStep').style.display = 'none';
    document.getElementById('professionStep').style.display = 'block';
    
    document.getElementById('categoryTitle').textContent = `🎓 ${category}`;
    
    const list = document.getElementById('professionList');
    list.innerHTML = '';
    
    PROFESSIONS[category].forEach(prof => {
        const display = prof.split(' | ')[0];
        const btn = document.createElement('button');
        btn.className = 'btn';
        btn.style.padding = '12px';
        btn.style.background = '#fff';
        btn.style.color = '#000';
        btn.style.border = '2px solid #d0d0d0';
        btn.style.borderRadius = '10px';
        btn.style.textAlign = 'left';
        btn.textContent = display;
        btn.onclick = () => selectProfession(prof);
        list.appendChild(btn);
    });
}

// Select profession
function selectProfession(prof) {
    selectedProfession = prof;
    document.getElementById('profession').value = prof.split(' | ')[0];
    document.getElementById('professionStep').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

// Show form step
function showFormStep() {
    document.getElementById('categoryStep').style.display = 'none';
    document.getElementById('professionStep').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

// Form submission
function setupFormSubmit() {
    const form = document.getElementById('registerForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!selectedProfession) {
            showError("❌ Iltimos, kompetensiyani tanlang!");
            showCategoryStep();
            return;
        }
        
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
            profession: selectedProfession
        };
        
        console.log("📤 Sending:", data);
        
        try {
            const backendUrl = window.location.origin;
            const response = await fetch(`${backendUrl}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                mode: 'cors',
                body: JSON.stringify(data)
            });
            
            if (!response.ok) throw new Error(`Server error: ${response.status}`);
            
            const result = await response.json();
            
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
    document.querySelector('.subtitle').textContent = t.subtitle;
    document.getElementById('submitBtn').textContent = t.btnSubmit;
    document.querySelector('.loading-text').textContent = t.loading;
    document.querySelector('.success h2').textContent = t.successTitle;
    document.querySelector('.success p').textContent = t.successText;
    document.querySelector('.error h2').textContent = t.errorTitle;
    document.getElementById('profession').placeholder = t.professionPlaceholder;
    
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
