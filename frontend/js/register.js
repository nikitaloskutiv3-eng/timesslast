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

// 📝 Регистрация
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const passwordConfirm = document.getElementById("passwordConfirm").value;
    const errorDiv = document.getElementById("error");
    const successDiv = document.getElementById("success");
    
    // Скрываем сообщения
    errorDiv.style.display = "none";
    successDiv.style.display = "none";
    
    // Проверка паролей
    if (password !== passwordConfirm) {
        errorDiv.textContent = "Пароли не совпадают";
        errorDiv.style.display = "block";
        return;
    }
    
    console.log("Register attempt:", username);
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
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
            errorDiv.textContent = data.detail || "Ошибка регистрации";
            errorDiv.style.display = "block";
            return;
        }
        
        // Успешная регистрация
        successDiv.textContent = "✅ Регистрация успешна! Перенаправляю на вход...";
        successDiv.style.display = "block";
        
        console.log("Register successful, redirecting...");
        setTimeout(() => {
            window.location.href = "login.html";
        }, 2000);
        
    } catch (error) {
        console.error("Register error:", error);
        errorDiv.textContent = "Ошибка соединения с сервером";
        errorDiv.style.display = "block";
    }
}

// Инициализация темы при загрузке
initTheme();