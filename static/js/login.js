function toggleLoginPassword(inputId, iconElement) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        iconElement.textContent = '🔓'; // open lock
    } else {
        input.type = 'password';
        iconElement.textContent = '🔒'; // closed lock
    }
}
