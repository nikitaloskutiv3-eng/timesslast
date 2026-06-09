const API_URL = "http://localhost:8000";

// 🌙 Инициализация темы
function initTheme() {
    const savedTheme = localStorage.getItem("theme") || "light";
    if (savedTheme === "dark") {
        document.body.classList.add("dark-theme");
    }
}

// 🌙 Переключение темы
function toggleTheme() {
    document.body.classList.toggle("dark-theme");
    const isDark = document.body.classList.contains("dark-theme");
    localStorage.setItem("theme", isDark ? "dark" : "light");
}

// 🔐 Вход
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorDiv = document.getElementById("error");
    
    console.log("Login attempt:", username);
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        console.log("Response status:", response.status);
        const data = await response.json();
        console.log("Response data:", data);
        
        if (!response.ok) {
            errorDiv.textContent = data.detail || "Ошибка входа";
            errorDiv.style.display = "block";
            return;
        }
        
        // Сохраняем токен и юзера
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify({
            user_id: data.user_id,
            username: data.username
        }));
        
        console.log("Login successful, redirecting...");
        window.location.href = "index.html";
        
    } catch (error) {
        console.error("Login error:", error);
        errorDiv.textContent = "Ошибка соединения с сервером";
        errorDiv.style.display = "block";
    }
}

// Инициализация темы при загрузке
initTheme();