// DOM элементы
const themeToggle = document.getElementById('theme-toggle');
const systemThemeBtn = document.getElementById('system-theme');
const body = document.body;

// Ключ для localStorage
const THEME_STORAGE_KEY = 'user-theme';

// Определение системной темы
function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

// Применение темы
function applyTheme(theme) {
    const isDark = theme === 'dark';
    body.classList.toggle('dark-theme', isDark);
    themeToggle.textContent = isDark ? '☀️' : '🌙';
    return isDark;
}

// Сохранение темы в localStorage
function saveTheme(theme) {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
}

// Загрузка темы из localStorage
function loadTheme() {
    return localStorage.getItem(THEME_STORAGE_KEY);
}

// Переключение темы
function toggleTheme() {
    const currentTheme = body.classList.contains('dark-theme') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    applyTheme(newTheme);
    saveTheme(newTheme);
}

// Сброс к системной теме
function resetToSystemTheme() {
    const systemTheme = getSystemTheme();
    applyTheme(systemTheme);
    localStorage.removeItem(THEME_STORAGE_KEY);
}

// Реакция на изменение системных настроек
function handleSystemThemeChange(e) {
    // Обновляем только если используется системная тема
    if (!loadTheme()) {
        applyTheme(e.matches ? 'dark' : 'light');
    }
}

// Инициализация темы при загрузке страницы
function initTheme() {
    const savedTheme = loadTheme();
    const systemTheme = getSystemTheme();
    
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        applyTheme(systemTheme);
    }
    
    // Следим за изменениями системной темы
    const systemThemeMedia = window.matchMedia('(prefers-color-scheme: dark)');
    systemThemeMedia.addEventListener('change', handleSystemThemeChange);
    
    // Возвращаем MediaQueryList для возможного удаления слушателя
    return systemThemeMedia;
}

// Инициализация при загрузке страницы
let themeMediaQuery;
document.addEventListener('DOMContentLoaded', () => {
    themeMediaQuery = initTheme();
    themeToggle.addEventListener('click', toggleTheme);
    systemThemeBtn.addEventListener('click', resetToSystemTheme);
});

// Очистка при переходе между страницами
window.addEventListener('beforeunload', () => {
    if (themeMediaQuery) {
        themeMediaQuery.removeEventListener('change', handleSystemThemeChange);
    }
});