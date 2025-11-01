// ✅ JobMiner 主题切换脚本（与 [data-theme="dark"] 完全匹配）
document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("theme-toggle");
    const root = document.documentElement; // 这里是 <html> 节点

    if (!toggleBtn) return;

    // 初始化：读取本地存储的主题
    const savedTheme = localStorage.getItem("theme") || "light";
    root.setAttribute("data-theme", savedTheme);
    toggleBtn.textContent = savedTheme === "dark" ? "☀️" : "🌙";

    // 点击切换主题
    toggleBtn.addEventListener("click", () => {
        const currentTheme = root.getAttribute("data-theme");
        const nextTheme = currentTheme === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", nextTheme);
        localStorage.setItem("theme", nextTheme);
        toggleBtn.textContent = nextTheme === "dark" ? "☀️" : "🌙";
    });
});
