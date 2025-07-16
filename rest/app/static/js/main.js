// Основные скрипты для всего сайта

// Мобильное меню
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем наличие элемента мобильного меню
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        const navLinks = document.querySelector('.nav-links');
        
        mobileMenuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Обработка сообщений об успехе/ошибках
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Автоматически скрываем сообщения через 5 секунд
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        }, 5000);

        // Добавляем кнопку закрытия
        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'close-alert';
        closeBtn.style.float = 'right';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.fontWeight = 'bold';
        
        closeBtn.addEventListener('click', function() {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        });
        
        alert.insertBefore(closeBtn, alert.firstChild);
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                event.preventDefault();
            }
        });
    });
});

// Функция для асинхронной загрузки контента
async function loadContent(url, targetElement) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Ошибка загрузки контента');
        }
        const data = await response.text();
        document.querySelector(targetElement).innerHTML = data;
    } catch (error) {
        console.error('Ошибка:', error);
        document.querySelector(targetElement).innerHTML = '<p class="alert alert-danger">Произошла ошибка при загрузке данных</p>';
    }
}

// Функция для отправки форм асинхронно
async function submitForm(formElement, successCallback, errorCallback) {
    try {
        const form = document.querySelector(formElement);
        const formData = new FormData(form);
        
        const response = await fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (successCallback && typeof successCallback === 'function') {
                successCallback(data);
            }
        } else {
            throw new Error(data.detail || 'Произошла ошибка');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        if (errorCallback && typeof errorCallback === 'function') {
            errorCallback(error);
        }
    }
}