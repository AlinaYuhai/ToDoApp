// Проверка логина
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Жёстко закодированные учетные данные
    if(username === 'admin' && password === '1234') {
        localStorage.setItem('loggedIn', 'true');
        window.location.href = 'index.html'; // переходит в ToDo
    } else {
        alert('Invalid credentials');
    }
}

function checkLogin() {
    if(localStorage.getItem('loggedIn') !== 'true') {
        window.location.href = 'login.html';
    }
}
