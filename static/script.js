// Функция логина
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Пример учётных данных
    if(username === 'admin' && password === '1234') {
        localStorage.setItem('loggedIn', 'true');
        window.location.href = 'index.html'; // переход в ToDo
    } else {
        alert('Invalid credentials'); // если данные не совпали
    }
}

// Проверка при загрузке index.html
function checkLogin() {
    if(localStorage.getItem('loggedIn') !== 'true') {
        window.location.href = 'login.html';
    }
}
