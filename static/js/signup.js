// Toggle password visibility
function togglePassword(id) {
    const field = document.getElementById(id);
    field.type = field.type === "password" ? "text" : "password";
}

// Password strength checker
const passwordInput = document.getElementById('password');
const strengthLevel = document.getElementById('strength-level');
const strengthText = document.getElementById('strength-text');

passwordInput.addEventListener('input', () => {
    const value = passwordInput.value;
    let strength = 0;

    const regexes = [
        /.{8,}/,         // at least 8 characters
        /[0-9]/,         // contains a number
        /[!@#$%^&*]/     // contains a special character
    ];

    regexes.forEach((regex) => {
        if (regex.test(value)) strength++;
    });

    let colors = ['red', 'orange', 'green'];
    let texts = ['Weak', 'Moderate', 'Strong'];

    strengthLevel.style.width = `${(strength / 3) * 100}%`;
    strengthLevel.style.background = colors[strength - 1] || 'red';
    strengthText.textContent = value ? texts[strength - 1] || 'Too Weak' : '';
});
