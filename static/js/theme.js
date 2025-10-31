// 🌙 深浅模式切换逻辑
const root = document.documentElement;
const toggleBtn = document.getElementById("themeToggle");

function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    toggleBtn.textContent = theme === "dark" ? "☀️" : "🌙";
}

// 初始化主题
const savedTheme = localStorage.getItem("theme") || "light";
setTheme(savedTheme);

// 点击切换主题
toggleBtn.addEventListener("click", () => {
    const newTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    setTheme(newTheme);
});
