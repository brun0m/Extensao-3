const cadastroForm = document.querySelector("form");

cadastroForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = cadastroForm.username.value;
  const email = cadastroForm.email.value;
  const password1 = cadastroForm.password1.value;
  const password2 = cadastroForm.password2.value;

  if(password1 !== password2){
    alert("Senhas não conferem!");
    return;
  }

  const response = await fetch("/cadastro/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({ username, email, password: password1 })
  });

  const data = await response.json();
  if(data.success){
    window.location.href = "/login/";
  } else {
    alert(data.error);
  }
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(cookie => {
      const c = cookie.trim();
      if (c.startsWith(name + '=')) cookieValue = decodeURIComponent(c.substring(name.length + 1));
    });
  }
  return cookieValue;
}
