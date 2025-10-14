document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    form.addEventListener('submit', function (e) {
        const password1 = form.password1.value;
        const password2 = form.password2.value;
        if (password1 !== password2) {
            e.preventDefault();
            alert('As senhas não coincidem!');
        }
    });
});