
// ====== PROGRESS NOTIFICATIONS ======
function checkDocumentProgress() {
    const total = officialDocs.length; // 9 ta hujjat
    const uploaded = Object.values(userData.documents).filter(d => d.status !== 'upload').length;
    const approved = Object.values(userData.documents).filter(d => d.status === 'approved').length;
    const remaining = total - uploaded;
    
    // Progress bar yangilash
    const percent = Math.round((approved / total) * 100);
    document.getElementById('docProgressFill').style.width = percent + '%';
    document.getElementById('docProgressPercent').textContent = percent + '%';
    
    // Notification messages
    if (approved === total) {
        // ✅ Barcha hujjatlar tayyor!
        showNotification('🎉 Barcha hujjatlaringiz yuklandi va tasdiqlandi!', 'success');
        
        // Sertifikat generatsiyasini taklif qilish
        if (!userData.certificateGenerated) {
            setTimeout(() => {
                Telegram.WebApp.showPopup({
                    title: '🏆 Sertifikat Tayyor!',
                    message: 'Barcha hujjatlaringiz tasdiqlandi! Sertifikatingizni generatsiya qilishni xohlaysizmi?',
                    buttons: [
                        {type: 'ok', text: '✅ Ha, generatsiya qil'},
                        {type: 'cancel', text: '⏳ Keyinroq'}
                    ]
                }).then((btn) => {
                    if (btn === 'ok') {
                        generateCertificate();
                    }
                });
            }, 2000);
        }
    } else if (remaining <= 3 && remaining > 0) {
        // ⚠️ Oz qoldi!
        showNotification(`⚡ Faqat ${remaining} ta hujjat qoldi! Davom eting!`, 'warning');
    } else if (uploaded === 0) {
        // 🚀 Boshlash
        showNotification('🚀 Birinchi hujjatingizni yuklang!', 'info');
    }
    
    // Statistika yangilash
    document.getElementById('docApproved').textContent = approved;
    document.getElementById('docPending').textContent = Object.values(userData.documents).filter(d => d.status === 'pending').length;
    document.getElementById('docRejected').textContent = Object.values(userData.documents).filter(d => d.status === 'rejected').length;
    document.getElementById('docTotal').textContent = total;
}

function showNotification(message, type) {
    // Telegram WebApp notification
    Telegram.WebApp.showPopup({
        title: type === 'success' ? '✅ Muvaffaqiyat!' : 
               type === 'warning' ? '⚠️ Diqqat!' : 'ℹ️ Ma\'lumot',
        message: message,
        buttons: [{type: 'ok'}]
    });
}

async function generateCertificate() {
    try {
        const tg = Telegram.WebApp;
        const initData = tg.initData;
        
        const response = await fetch('/api/certificate/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                telegramId: tg.initDataUnsafe?.user?.id,
                initData: initData
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            userData.certificateGenerated = true;
            localStorage.setItem('ws_user', JSON.stringify(userData));
            
            tg.showPopup({
                title: '🎉 Sertifikat Generatsiya Qilindi!',
                message: `Sertifikat ID: ${result.certificate_id}\n\nMini App → Statistika bo'limidan yuklab olishingiz mumkin.`,
                buttons: [{type: 'ok'}]
            });
        } else {
            tg.showPopup({
                title: '⚠️ Xatolik',
                message: result.message || 'Sertifikat generatsiyasida xatolik yuz berdi',
                buttons: [{type: 'ok'}]
            });
        }
    } catch(err) {
        console.error('Certificate error:', err);
        alert('❌ Xatolik: ' + err.message);
    }
}

// ====== MODAL YANGILASH: Upload tugmasi bosilganda ======
async function uploadDocument() {
    if(!currentDocId || !selectedDocFile) return;
    
    const btn = document.getElementById('uploadBtn');
    btn.disabled = true; 
    btn.textContent = '⏳ Yuklanmoqda...';
    
    try {
        // Simulate upload
        await new Promise(r => setTimeout(r, 1500));
        
        // Save to localStorage
        userData.documents[currentDocId] = {
            status: 'pending',
            fileName: selectedDocFile.name,
            fileSize: selectedDocFile.size,
            uploadedAt: new Date().toISOString()
        };
        localStorage.setItem('ws_user', JSON.stringify(userData));
        
        // Update UI
        renderDocuments();
        checkDocumentProgress(); // ✅ Progress notifications
        closeModal('docModal');
        
        // Show success
        Telegram.WebApp.showPopup({
            title: '✅ Yuklandi!',
            message: 'Hujjatingiz admin ko\'rib chiqishiga yuborildi. 1-3 kun ichida natija ma\'lum bo\'ladi.',
            buttons: [{type:'ok'}]
        });
        
    } catch(err) {
        alert('❌ Xatolik: ' + err.message);
        btn.disabled = false; 
        btn.textContent = '📤 Yuklash';
    }
}

// ====== INIT DA PROGRESS NI TEKSHIRISH ======
window.onload = function() {
    // ... existing init code ...
    
    // Progress notifications ni tekshirish
    if(userData.documents && Object.keys(userData.documents).length > 0) {
        checkDocumentProgress();
    }
};
