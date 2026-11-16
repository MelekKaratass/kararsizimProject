document.addEventListener("DOMContentLoaded", () => {
  const list = document.querySelector("#option-list");
  const addButton = document.querySelector("#add-option");
  const updateRows = () => {
    const rows = [...list.querySelectorAll("[data-option-row]")];
    rows.forEach((row, index) => {
      row.querySelector(".option-number").textContent = index + 1;
      const input = row.querySelector("input");
      input.name = `option_${index}`;
      input.id = `id_option_${index}`;
      input.placeholder = `Seçenek ${index + 1}`;
      input.required = index < 2;
      row.querySelector(".remove-option").disabled = rows.length <= 2;
    });
    addButton.disabled = rows.length >= 5;
  };
  addButton.addEventListener("click", () => {
    const rows = list.querySelectorAll("[data-option-row]");
    if (rows.length >= 5) return;
    const row = rows[rows.length - 1].cloneNode(true);
    row.querySelector("input").value = "";
    list.append(row);
    updateRows();
  });
  list.addEventListener("click", (event) => {
    if (event.target.matches(".remove-option") && list.querySelectorAll("[data-option-row]").length > 2) {
      event.target.closest("[data-option-row]").remove();
      updateRows();
    }
  });
  updateRows();
});
