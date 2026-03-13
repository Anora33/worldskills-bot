// Telegram Web App init
const tg = window.Telegram.WebApp;
tg.expand();

// User data
let userData = {
    id: tg.initDataUnsafe?.user?.id || 0,
    first_name: tg.initDataUnsafe?.user?.first_name || 'Foydalanuvchi',
    username: tg.initDataUnsafe?.user?.username || '',
    competition: '',
    points: 0
};

// DOM Elements
const userCard = document.getElementById('userCard');
const userName = document.getElementById('userName');
const userCompetition = document.getElementById('userCompetition');
const userPoints = document.getElementById('userPoints');
const backBtn = document.getElementById('backBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadUserData();
    showUserCard();
});

// Load user data from backend
async function loadUserData() {
    try {
        const response = await fetch(`/api/user/${userData.id}`);
        if (response.ok) {
            const data = await response.json();
            userData.competition = data.competition || "Yo'nalish tanlanmagan";
            userData.points = data.points || 0;
        }
    } catch (error) {
        console.log('User data not loaded yet');
    }
}

// Show user card
function showUserCard() {
    userCard.style.display = 'block';
    userName.textContent = userData.first_name;
    userCompetition.textContent = userData.competition;
    userPoints.textContent = userData.points;
    
    // Update profile section
    document.getElementById('profileName').textContent = userData.first_name;
    document.getElementById('profileId').textContent = userData.id;
    document.getElementById('profileCompetition').textContent = userData.competition;
    document.getElementById('profilePoints').textContent = userData.points;
}

// Show section
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    const section = document.getElementById(sectionName + 'Section');
    if (section) {
        section.style.display = 'block';
        backBtn.style.display = 'block';
    }
    
    // Haptic feedback
    tg.HapticFeedback.impactOccurred('light');
}

// Back to menu
function backToMenu() {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    backBtn.style.display = 'none';
    tg.HapticFeedback.impactOccurred('light');
}

// Send message in AI chat
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.textContent = message;
    messages.appendChild(userMsg);
    
    input.value = '';
    
    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;
    
    // Send to backend
    try {
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userData.id,
                message: message
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            const botMsg = document.createElement('div');
            botMsg.className = 'message bot';
            botMsg.textContent = data.response;
            messages.appendChild(botMsg);
        } else {
            const botMsg = document.createElement('div');
            botMsg.className = 'message bot';
            botMsg.textContent = "Kechirasiz, hozir javob bera olmayman. Keyinroq urinib ko'ring.";
            messages.appendChild(botMsg);
        }
    } catch (error) {
        const botMsg = document.createElement('div');
        botMsg.className = 'message bot';
        botMsg.textContent = "Xatolik yuz berdi. Internetni tekshiring.";
        messages.appendChild(botMsg);
    }
    
    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;
    tg.HapticFeedback.impactOccurred('light');
}

// Enter key to send
document.getElementById('chatInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Set header color
tg.setHeaderColor('#667eea');
tg.setBackgroundColor('#667eea');

// Ready
tg.ready();
