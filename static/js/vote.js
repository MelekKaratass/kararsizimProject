document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".vote-form");
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const choice = form.querySelector('input[name="option_id"]:checked');
    const error = form.querySelector("[data-vote-error]");
    if (!choice) { error.textContent = "Önce bir seçenek seç."; return; }
    const button = form.querySelector("button[type=submit]");
    button.disabled = true;
    error.textContent = "";
    try {
      const response = await fetch(form.dataset.voteUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value },
        body: JSON.stringify({ option_id: choice.value }),
        credentials: "same-origin",
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Oy kaydedilemedi.");
      window.location.assign(result.redirect);
    } catch (problem) {
      error.textContent = problem.message;
      button.disabled = false;
    }
  });
});
