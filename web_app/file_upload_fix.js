
// ============= FILE UPLOAD - DESKTOP COMPATIBLE =============

// File input'ni to'g'ri ochish funksiyasi
function triggerFileInput(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // 1-usul: Direct click
    try {
        input.click();
    } catch (e) {
        console.log('Direct click failed:', e);
        
        // 2-usul: Event bilan
        try {
            const event = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            input.dispatchEvent(event);
        } catch (e2) {
            console.log('Event dispatch failed:', e2);
            
            // 3-usul: Focus + click
            input.focus();
            input.click();
        }
    }
}

// File validation - desktop va mobil uchun
function validateFile(file, maxSizeMB, allowedTypes = ['application/pdf']) {
    if (!file) {
        safeShowPopup('❌ Xatolik', 'Fayl tanlanmagan!');
        return false;
    }
    
    // Type tekshiruvi (desktop'da ba'zan bo'sh keladi)
    if (file.type && !allowedTypes.includes(file.type)) {
        safeShowPopup('❌ Xatolik', 'Faqat PDF fayllar qabul qilinadi!');
        return false;
    }
    
    // Extension tekshiruvi (desktop uchun qo'shimcha)
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        safeShowPopup('❌ Xatolik', 'Fayl nomi .pdf bilan tugashi kerak!');
        return false;
    }
    
    // Size tekshiruvi
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
        safeShowPopup('❌ Xatolik', `Fayl hajmi ${maxSizeMB} MB dan oshmasligi kerak!`);
        return false;
    }
    
    return true;
}

// Document file select handler
function handleDocFileSelect(e) {
    const file = e.target.files?.[0];
    if (!file) {
        console.log('No file selected');
        return;
    }
    
    console.log('Selected file:', file.name, file.size, file.type);
    
    if (!validateFile(file, 10, ['application/pdf', ''])) {
        e.target.value = '';
        return;
    }
    
    selectedDocFile = file;
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB';
    document.getElementById('filePreview').classList.add('active');
    document.getElementById('uploadBtn').disabled = false;
    
    console.log('✅ File validated and ready for upload');
}

// Portfolio file select handler
function handlePortfolioFileSelect(e) {
    const file = e.target.files?.[0];
    if (!file) {
        console.log('No file selected');
        return;
    }
    
    console.log('Selected file:', file.name, file.size, file.type);
    
    if (!validateFile(file, 20, ['application/pdf', ''])) {
        e.target.value = '';
        return;
    }
    
    selectedPortfolioFile = file;
    document.getElementById('portfolioFileName').textContent = file.name;
    document.getElementById('portfolioFileSize').textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB';
    document.getElementById('portfolioFilePreview').classList.add('active');
    document.getElementById('portfolioUploadBtn').disabled = false;
    
    console.log('✅ File validated and ready for upload');
}

// Upload area click handler - desktop compatible
function setupUploadAreas() {
    // Document upload area
    const docUploadArea = document.querySelector('.upload-area[onclick*="fileInput"]');
    if (docUploadArea) {
        docUploadArea.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            triggerFileInput('fileInput');
        };
    }
    
    // Portfolio upload area
    const portfolioUploadArea = document.querySelector('.upload-area[onclick*="portfolioFileInput"]');
    if (portfolioUploadArea) {
        portfolioUploadArea.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            triggerFileInput('portfolioFileInput');
        };
    }
}

// Init da chaqirish
window.onload = function() {
    // ... existing init code ...
    setupUploadAreas();  // ← Yangi: Upload area'larini sozlash
};

// Modal ochilganda ham setup qilish
function openDocModal(docId) {
    // ... existing code ...
    setTimeout(setupUploadAreas, 100);  // ← DOM yangilangach qayta sozlash
}
