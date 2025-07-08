document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("theme-toggle");
  const root = document.documentElement;

  // Check saved mode
  if (localStorage.getItem("theme") === "dark") {
    root.classList.add("dark");
  }

  toggle?.addEventListener("click", () => {
    root.classList.toggle("dark");
    localStorage.setItem("theme", root.classList.contains("dark") ? "dark" : "light");
  });
});
