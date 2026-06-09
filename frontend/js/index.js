const API_URL = "http://localhost:8000";
const token = localStorage.getItem("token");

console.log("=== INDEX.HTML LOADED ===");
console.log("Token from localStorage:", token);

if (!token) {
    console.log("No token found, redirecting to login");
    window.location.href = "login.html";
} else {
    console.log("Token found, initializing app");
}

let currentChatId = null;
let currentUserId = null;
let socket = null;
let messageIds = new Set();
let currentUser = null;
let isMobile = window.innerWidth <= 768;
let userLastSeen = null;
let isPageVisible = true;
let statusUpdateInterval = null;

// 👁️ Отслеживание видимости вкладки
document.addEventListener("visibilitychange", async () => {
    isPageVisible = !document.hidden;
    
    if (document.hidden) {
        // Вкладка неактивна
        console.log("👋 Ушли со вкладки");
        await updateUserStatus("away");
    } else {
        // Вкладка активна
        console.log("👀 Вернулись на вкладку");
        await updateUserStatus("online");
    }
});

// 📤 Отправить статус на сервер
async function updateUserStatus(status) {
    try {
        const response = await fetch(`${API_URL}/users/me/status`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                status: status,
                last_seen: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            console.error("Ошибка обновления статуса:", response.status);
        }
    } catch (error) {
        console.error("Ошибка:", error);
    }
}

// 📊 Загрузить статус пользователя
async function loadUserStatus(userId) {
    try {
        const response = await fetch(`${API_URL}/users/${userId}/status`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!response.ok) return;
        
        const data = await response.json();
        
        if (data.status === "online") {
            document.getElementById("chatStatus").textContent = "в сети";
            document.getElementById("chatStatus").style.color = "#34c759";
            
            // 👇 Добавьте это - обновляем кружок в списке чатов
            const chatAvatar = document.getElementById("chatAvatar");
            if (chatAvatar) {
                chatAvatar.classList.add("online");
            }
        } else {
            const lastSeen = new Date(data.last_seen).toLocaleTimeString('ru-RU', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            document.getElementById("chatStatus").textContent = "был(а) в " + lastSeen;
            document.getElementById("chatStatus").style.color = "#999";
            
            // 👇 Добавьте это - убираем кружок
            const chatAvatar = document.getElementById("chatAvatar");
            if (chatAvatar) {
                chatAvatar.classList.remove("online");
            }
        }
    } catch (error) {
        console.error("Ошибка загрузки статуса:", error);
    }
}

// 🔄 Запустить автообновление статуса
function startStatusAutoUpdate() {
    // Очищаем предыдущий интервал если был
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
    
    // Обновляем статус каждую минуту (60000 мс)
    statusUpdateInterval = setInterval(async () => {
        if (currentChatId && currentUserId) {
            console.log("🔄 Auto-updating status...");
            const otherUserId = allChats.find(c => c.id === currentChatId)?.members.find(id => id !== currentUserId);
            if (otherUserId) {
                await loadUserStatus(otherUserId);
            }
        }
    }, 15000); // 15 сек
}

// ⏹️ Остановить автообновление статуса
function stopStatusAutoUpdate() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
        statusUpdateInterval = null;
    }
}

// 📱 Проверка мобильного экрана
window.addEventListener("resize", () => {
    isMobile = window.innerWidth <= 768;
});

// 🌙 Инициализация темы
function initTheme() {
    const savedTheme = localStorage.getItem("theme") || "light";
    if (savedTheme === "dark") {
        document.body.classList.add("dark-theme");
        document.getElementById("themeToggle").classList.add("active");
    }
}

// 🌙 Переключение темы
function toggleTheme() {
    document.body.classList.toggle("dark-theme");
    const themeToggle = document.getElementById("themeToggle");
    themeToggle.classList.toggle("active");
    
    const isDark = document.body.classList.contains("dark-theme");
    localStorage.setItem("theme", isDark ? "dark" : "light");
}

// 📱 Переход на чат
function showChat() {
    if (!isMobile) return;
    
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("mainContent");
    
    sidebar.classList.add("hidden");
    mainContent.classList.remove("hidden");
    mainContent.classList.add("show");
}

// 📱 Возврат на список чатов
function goBack() {
    if (!isMobile) return;
    
    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("mainContent");
    
    sidebar.classList.remove("hidden");
    mainContent.classList.add("hidden");
    mainContent.classList.remove("show");
    
    // Закрываем меню при возврате
    document.getElementById("menuDropdown").classList.remove("show");
    stopStatusAutoUpdate();
}

// 🔐 Получить текущего пользователя
async function getCurrentUser() {
    try {
        console.log("Getting current user...");
        const response = await fetch(`${API_URL}/auth/me`, {
            method: "GET",
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });
        
        console.log("Auth response status:", response.status);
        
        if (!response.ok) {
            console.error("Auth failed with status:", response.status);
            const errorData = await response.json();
            console.error("Error details:", errorData);
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            window.location.href = "login.html";
            return null;
        }
        
        const user = await response.json();
        console.log("Current user:", user);
        return user;
        
    } catch (error) {
        console.error("Error getting current user:", error);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "login.html";
        return null;
    }
}

// 📥 Загрузить чаты
let allChats = [];
async function loadChats() {
    try {
        const response = await fetch(`${API_URL}/chats/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!response.ok) {
            console.error("Error loading chats:", response.status);
            return;
        }
        
        const chats = await response.json();
        allChats = chats;
        console.log("Loaded chats:", chats);
        
        const chatsList = document.getElementById("chatsList");
        chatsList.innerHTML = "";
        
        if (chats.length === 0) {
            chatsList.innerHTML = '<div class="empty-sidebar-message">Нет чатов. Найдите пользователя.</div>';
            return;
        }
        
        chats.forEach(async (chat) => {
            const div = document.createElement("div");
            div.className = "chat-item";
            
            // Найти собеседника
            const otherUserId = chat.members.find(id => id !== currentUserId);
            
            // Загрузить его статус
            let isOnline = false;
            if (otherUserId) {
                try {
                    const response = await fetch(`${API_URL}/users/${otherUserId}/status`, {
                        headers: { "Authorization": `Bearer ${token}` }
                    });
                    if (response.ok) {
                        const data = await response.json();
                        isOnline = data.status === "online";
                    }
                } catch (error) {
                    console.error("Error loading status:", error);
                }
            }
            
            const avatar = document.createElement("div");
            avatar.className = `chat-avatar ${isOnline ? 'online' : ''}`;  // 👈 Добавляем класс online
            avatar.textContent = chat.name.charAt(0).toUpperCase();
            
            div.innerHTML = `
                <div class="chat-info">
                    <div class="chat-name">${chat.name}</div>
                </div>
            `;
            div.insertBefore(avatar, div.firstChild);
            
            div.onclick = () => selectChat(chat);
            chatsList.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading chats:", error);
    }
}

// 🔍 Поиск пользователей
let searchTimeout;
document.getElementById("searchInput").addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();
    
    if (query.length < 1) {
        document.getElementById("searchResults").classList.remove("show");
        return;
    }
    
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`${API_URL}/users/?query=${encodeURIComponent(query)}`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            
            if (!response.ok) return;
            
            const users = await response.json();
            console.log("Search results:", users);
            
            const resultsDiv = document.getElementById("searchResults");
            resultsDiv.innerHTML = "";
            
            if (users.length === 0) {
                resultsDiv.classList.remove("show");
                return;
            }
            
            users.forEach(user => {
                const div = document.createElement("div");
                div.className = "search-result-item";
                div.textContent = user.username;
                div.onclick = () => createPrivateChat(user.id, user.username);
                resultsDiv.appendChild(div);
            });
            
            resultsDiv.classList.add("show");
        } catch (error) {
            console.error("Error searching users:", error);
        }
    }, 300);
});

// Закрыть поиск при клике вне
document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-box")) {
        document.getElementById("searchResults").classList.remove("show");
    }
    if (!e.target.closest(".sidebar-header")) {
        document.getElementById("menuDropdown").classList.remove("show");
    }
});

// 💬 Создать приватный чат
async function createPrivateChat(userId, username) {
    try {
        console.log("Creating private chat with user:", userId);
        
        const response = await fetch(`${API_URL}/chats/private`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ user_id: userId })
        });
        
        if (!response.ok) {
            console.error("Error creating chat:", response.status);
            const errorData = await response.json();
            console.error("Error details:", errorData);
            return;
        }
        
        const chat = await response.json();
        console.log("Chat created:", chat);
        
        document.getElementById("searchInput").value = "";
        document.getElementById("searchResults").classList.remove("show");
        
        await loadChats();
        
        // Найти и выбрать созданный чат
        const chatItems = document.querySelectorAll(".chat-item");
        chatItems.forEach(item => {
            if (item.textContent.includes(chat.name)) {
                item.click();
            }
        });
    } catch (error) {
        console.error("Error creating private chat:", error);
    }
}

// ✅ Выбрать чат
async function selectChat(chat) {
    console.log("Selecting chat:", chat);
    
    currentChatId = chat.id;
    
    // Загружаем статус собеседника
    const otherUserId = chat.members.find(id => id !== currentUserId);
    if (otherUserId) {
        await loadUserStatus(otherUserId);
    }
    
    document.getElementById("chatAvatar").textContent = chat.name.charAt(0).toUpperCase();
    document.getElementById("chatAvatar").style.display = "flex";
    document.getElementById("chatName").textContent = chat.name;
    document.getElementById("inputArea").style.display = "flex";
    
    messageIds.clear();
    
    // Правильно добавляем active класс
    const chatItems = document.querySelectorAll(".chat-item");
    chatItems.forEach(item => {
        item.classList.remove("active");
    });
    
    const activeChat = Array.from(chatItems).find(item => 
        item.textContent.includes(chat.name)
    );
    if (activeChat) {
        activeChat.classList.add("active");
    }
    
    await loadMessages();
    connectWebSocket();
    startStatusAutoUpdate();
    if (isMobile) {
        showChat();
    }
}

// 📨 Загрузить сообщения
async function loadMessages() {
    try {
        console.log("Loading messages for chat:", currentChatId);
        
        const response = await fetch(`${API_URL}/messages/?chat_id=${currentChatId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!response.ok) {
            console.error("Error loading messages:", response.status);
            return;
        }
        
        const messages = await response.json();
        console.log("Loaded messages:", messages);
        
        const container = document.getElementById("messagesContainer");
        container.innerHTML = "";
        messageIds.clear();
        
        messages.forEach(msg => {
            messageIds.add(msg.id);
            addMessageToUI(msg);
        });
        
        container.scrollTop = container.scrollHeight;
    } catch (error) {
        console.error("Error loading messages:", error);
    }
}

// 🌐 WebSocket подключение
function connectWebSocket() {
    if (socket) {
        socket.close();
    }
    
    console.log("Connecting WebSocket for chat:", currentChatId);
    
    socket = new WebSocket(`ws://localhost:8000/ws/chat/${currentChatId}?token=${token}`);
    
    socket.onopen = () => {
        console.log("WebSocket connected");
        // Перезагружаем статус собеседника при переподключении
        const otherUserId = allChats.find(c => c.id === currentChatId)?.members.find(id => id !== currentUserId);
        if (otherUserId) {
            loadUserStatus(otherUserId);
        }
    };
    
    socket.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            console.log("Message received:", msg);
            
            if (!messageIds.has(msg.id)) {
                messageIds.add(msg.id);
                addMessageToUI(msg);
            }
        } catch (error) {
            console.error("Error parsing message:", error);
        }
    };
    
    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        document.getElementById("chatStatus").textContent = "Ошибка";
    };
    
    socket.onclose = () => {
        console.log("WebSocket disconnected");
        document.getElementById("chatStatus").textContent = "Подключение";
    };
}

//👤 Показать профиль собеседника из header чата
function showChatMemberProfile() {
    console.log("=== PROFILE CLICK ===");

    console.log("currentChatId:", currentChatId);
    console.log("currentUserId:", currentUserId);

    const chat = allChats.find(
        c => Number(c.id) === Number(currentChatId)
    );

    console.log("chat:", chat);

    if (!chat) return;

    console.log("members:", chat.members);

    const memberId = chat.members.find(
        id => Number(id) !== Number(currentUserId)
    );

    console.log("memberId:", memberId);

    if (memberId) {
        showUserProfile(memberId);
    }
}
// 👤 Показать профиль собеседника
async function showUserProfile(userId) {
    try {
        const response = await fetch(`${API_URL}/users/${userId}`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            console.error("Ошибка загрузки профиля");
            return;
        }

        const user = await response.json();
        console.log("User data:", user);

        // аватар (инициал или картинка)
        const avatarContainer = document.getElementById("userAvatar");

        if (avatarContainer) {
            avatarContainer.innerHTML = "";

            const letterAvatar = document.createElement("div");
            letterAvatar.className = "setava";

            const name = user.username || "";
            letterAvatar.textContent = name
                ? name.charAt(0).toUpperCase()
                : "?";

            avatarContainer.appendChild(letterAvatar);
        }

        document.getElementById("userName").textContent = user.username || "";
        document.getElementById("usernameid").textContent = user.usernameid || "@unknown";
        document.getElementById("userBio").textContent = user.bio || "(нет описания)";
        document.getElementById("userBirthday").textContent = user.birthday || "(не указан)";

        document.getElementById("userProfileOverlay").classList.add("active");

    } catch (error) {
        console.error("Error loading user profile:", error);
    }
}

// // ❌ Закрыть профиль
// function closeUserProfile() {
//     document.getElementById("userProfileOverlay").classList.remove("active");
// }

// 📤 Отправить сообщение
function sendMessage() {
    const input = document.getElementById("messageInput");
    const content = input.value.trim();
    
    if (!content || !currentChatId || !socket) {
        return;
    }
    
    console.log("Sending message:", content);
    
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(content);
        input.value = "";
        input.focus();
    } else {
        showToast("❌ Соединение потеряно. Пожалуйста, выберите чат заново.");
    }
}

// 🧱 Добавить сообщение в UI
function addMessageToUI(msg) {
    const container = document.getElementById("messagesContainer");
    
    const emptyState = container.querySelector(".empty-state");
    if (emptyState) {
        emptyState.remove();
    }
    
    const div = document.createElement("div");
    div.className = "message";
    
    if (msg.sender_id === currentUserId) {
        div.classList.add("sent");
    } else {
        div.classList.add("received");
    }
    const dateStr = msg.created_at.endsWith('Z') ? msg.created_at : `${msg.created_at}Z`;
    const time = new Date(dateStr).toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    div.innerHTML = `
        <div class="message-content">
            ${msg.content}
            <div class="message-time">${time}</div>
        </div>
    `;
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// 🔘 Переключить меню
function toggleMenu() {
    const menu = document.getElementById("menuDropdown");
    menu.classList.toggle("show");
}




//return
function openProfile(user, isOwnProfile = false) {

    const overlay = document.getElementById("modalOverlay");

    // аватар
    const avatarContainer = document.getElementById("avatar");

    avatarContainer.innerHTML = "";

    const letterAvatar = document.createElement("div");
    letterAvatar.className = "setava";
    letterAvatar.textContent =
        user.username?.charAt(0).toUpperCase() || "?";

    avatarContainer.appendChild(letterAvatar);

    // данные
    document.getElementById("ausername").textContent =
        user.username || "";

    document.getElementById("ausernameid").textContent =
        user.usernameid || "@unknown";

    document.getElementById("abio").textContent =
        user.bio || "Не указано";

    document.getElementById("ahappy").textContent =
        user.birthday || "Не указано";

    // режим просмотра
    document.getElementById("info").style.display = "flex";
    document.getElementById("infoEdit").style.display = "none";

    const editBtn = document.querySelector(".btn-edit");

    if (isOwnProfile) {
        editBtn.style.display = "block";
    } else {
        editBtn.style.display = "none";
    }

    overlay.classList.add("active");
}

// ⚙️ Открыть настройки
function openSettings(event) {

    if (event) event.preventDefault();

    const menuDropdown =
        document.getElementById("menuDropdown");

    menuDropdown?.classList.remove("show");

    const savedUser =
        JSON.parse(localStorage.getItem("user"));

    if (!savedUser) return;

    openProfile(savedUser, true);
}



function closeSettings(event) {
  if (event) event.preventDefault();
  
  // Удаляем класс active — окно плавно улетает вверх, блюр исчезает
  const overlay = document.getElementById("modalOverlay");
  overlay.classList.remove("active");
}

async function showUserProfile(userId) {

    try {

        const response = await fetch(
            `${API_URL}/users/${userId}`,
            {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
        );

        if (!response.ok) return;

        const user = await response.json();

        openProfile(user, false);

    } catch (error) {

        console.error(error);

    }
}

// 🔧 Переключить режим редактирования
function toggleEditMode() {
    const infoView = document.getElementById("info");
    const infoEdit = document.getElementById("infoEdit");
    const btnEdit = document.querySelector(".btn-edit");
    
    const isEditing = infoEdit.style.display !== "none";
    
    if (isEditing) {
        // Переключаемся в режим просмотра
        infoView.style.display = "flex";
        infoEdit.style.display = "none";
        btnEdit.textContent = "✏️ Редактировать";
    } else {
        // Переключаемся в режим редактирования
        infoView.style.display = "none";
        infoEdit.style.display = "flex";
        btnEdit.style.display = "none";
        
        // Заполняем форму текущими данными
        const userData = JSON.parse(localStorage.getItem("user"));
        document.getElementById("editUsername").value = userData.username || "";
        document.getElementById("editUsernameid").value = userData.usernameid || "";
        document.getElementById("editBio").value = userData.bio || "";
        document.getElementById("editBirthday").value = userData.birthday || "";
    }
}

// 📝 Сохранить профиль
async function saveProfile() {
    const username = document.getElementById("editUsername").value.trim();
    const usernameid = document.getElementById("editUsernameid").value.trim();
    const bio = document.getElementById("editBio").value.trim();
    const birthday = document.getElementById("editBirthday").value;
    
    if (!username) {
        showToast("❌ Имя пользователя не может быть пустым");
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/users/me`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                username: username,
                usernameid: usernameid,
                bio: bio,
                birthday: birthday
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            showToast("❌ Ошибка сохранения: " + (errorData.detail || "Неизвестная ошибка"));
            return;
        }
        
        const updatedUser = await response.json();
        console.log("Profile updated:", updatedUser);
        
        // Обновляем localStorage БЕЗ выхода
        localStorage.setItem("user", JSON.stringify(updatedUser));
        currentUser = updatedUser;
        currentUserId = updatedUser.id;  // 👈 Обновляем ID
        
        // Если был активный чат, переподключаемся к WebSocket
        if (currentChatId && socket) {
            console.log("Reconnecting WebSocket after profile update...");
            socket.close();
            connectWebSocket();  // 👈 Переподключаемся
        }
        
        // Закрываем редактор и обновляем просмотр
        cancelEdit();
        openSettings(null);
        
       showToast("✅ Профиль сохранён");
    } catch (error) {
        console.error("Error saving profile:", error);
        showToast("❌ Ошибка при сохранёние");
    }
}

// ❌ Отменить редактирование
function cancelEdit() {
    const infoView = document.getElementById("info");
    const infoEdit = document.getElementById("infoEdit");
    const btnEdit = document.querySelector(".btn-edit");
    
    infoView.style.display = "flex";
    infoEdit.style.display = "none";
    btnEdit.style.display = "block";
    btnEdit.textContent = "✏️ Редактировать";
}


function showToast(text) {

    const toast = document.getElementById("toast");

    toast.textContent = text;

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}

// 🚪 Выход
function logout(event) {
    event.preventDefault();
    if (socket) {
        socket.close();
    }
    stopStatusAutoUpdate();
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "login.html";
}

// 🚀 ��апуск
async function init() {
    console.log("=== APP INIT ===");
    
    // Инициализируем тему
    initTheme();
    
    const user = await getCurrentUser();
    if (!user) {
        console.log("Failed to get user, stopping init");
        return;
    }
    
    console.log("User ID:", user.id);
    currentUserId = user.id;
    currentUser = user;
    localStorage.setItem("user", JSON.stringify(user));
    await loadChats();
    
    setInterval(loadChats, 5000);
}

// Обработка Enter для отправки сообщения
document.getElementById("messageInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// Запустить инициализацию
init();