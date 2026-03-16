// Telegram WebApp init
const tg = window.Telegram.WebApp;
tg.expand();

// Sahifa yuklanganda
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ WebApp loaded');
    tg.ready();

    // Foydalanuvchi ma'lumotlarini ko'rsatish
    if (tg.initDataUnsafe?.user) {
        document.getElementById('userName').textContent =
            tg.initDataUnsafe.user.first_name + ' ' +
            (tg.initDataUnsafe.user.last_name || '');
        document.getElementById('userId').textContent = tg.initDataUnsafe.user.id;
    }

    // Telegram MainButton sozlash
    tg.MainButton.setText("Yopish");
    tg.MainButton.onClick(() => tg.close());
});

// Rasm yuklash funksiyasi
async function uploadPhoto() {
    const fileInput = document.getElementById('photoInput');
    const statusDiv = document.getElementById('uploadStatus');
    const previewImg = document.getElementById('photoPreview');
    const previewContainer = document.getElementById('previewContainer');

    const file = fileInput.files[0];

    // Tekshirish: fayl tanlanganmi?
    if (!file) {
        showStatus('❌ Fayl tanlanmagan!', 'error');
        return;
    }

    // Fayl hajmini tekshirish (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showStatus('❌ Fayl hajmi 5MB dan oshmasligi kerak!', 'error');
        return;
    }

    // Fayl turini tekshirish
    if (!file.type.startsWith('image/')) {
        showStatus('❌ Faqat rasm fayllari yuklash mumkin!', 'error');
        return;
    }

    // Rasmni ko'rish uchun preview
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImg.src = e.target.result;
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // Yuklash jarayoni
    showStatus('⏳ Yuklanmoqda...', 'loading');

    const formData = new FormData();
    formData.append('photo', file);
    formData.append('telegram_id', tg.initDataUnsafe?.user?.id || 0);
    formData.append('username', tg.initDataUnsafe?.user?.username || '');

    try {
        // Backend API ga yuborish (hozircha mock response)
        // Haqiqiy backend bo'lsa, URL'ni o'zgartiring
        const response = await fetch('https://your-backend.com/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showStatus('✅ Rasm muvaffaqiyatli yuklandi!', 'success');

            // Telegram bot ga xabar yuborish
            tg.sendData(JSON.stringify({
                action: 'photo_uploaded',
                photo_url: result.photo_url,
                telegram_id: tg.initDataUnsafe?.user?.id
            }));
        } else {
            showStatus('❌ Xatolik: ' + result.error, 'error');
        }
    } catch (error) {
        // Demo mode (backend yo'q bo'lsa)
        console.log('Demo mode - backend yo\'q');
        showStatus('✅ Demo: Rasm yuklandi (backend ulanmagan)', 'success');

        // Telegram bot ga xabar
        tg.sendData(JSON.stringify({
            action: 'photo_uploaded_demo',
            telegram_id: tg.initDataUnsafe?.user?.id
        }));
    }
}

// Status ko'rsatish
function showStatus(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.textContent = message;
    statusDiv.className = 'status ' + type;
    statusDiv.style.display = 'block';

    // 5 soniyadan keyin yo'qoladi
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}