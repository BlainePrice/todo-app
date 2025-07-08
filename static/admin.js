const toggle = document.getElementById('theme-toggle');
const root = document.documentElement;

const showMoreUsersBtn = document.getElementById('showMoreUsers');
const usersTable = document.getElementById('usersTable');
const noMoreUsersMsg = document.getElementById('noMoreUsers');

const showMoreTodosBtn = document.getElementById('showMoreTodos');
const todosTable = document.getElementById('todosTable');
const noMoreTodosMsg = document.getElementById('noMoreTodos');

const showMoreTicketsBtn = document.getElementById('showMoreTickets');
const ticketsTable = document.getElementById('ticketsTable');
const noMoreTicketsMsg = document.getElementById('noMoreTickets');

const usersFilterInput = document.getElementById('userSearch');
const todosFilterInput = document.getElementById('todoSearch');
const ticketsFilterInput = document.getElementById('ticketSearch');

// Set Theme
function setTheme(theme) {
  root.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

toggle.addEventListener('click', () => {
  const currentTheme = root.getAttribute('data-theme');
  setTheme(currentTheme === 'light' ? 'dark' : 'light');
});

const savedTheme = localStorage.getItem('theme') || 'light';
setTheme(savedTheme);

// ----------------------------
// SHOW MORE FUNCTIONALITY
// ----------------------------

let visibleUsers = 5; // start with 5
let visibleTodos = 5;
let visibleTickets = 5;

function updateUsersVisibility(){
  const rows = usersTable.querySelectorAll('tbody tr');

  rows.forEach((row, i) => {
    row.style.display = i < visibleUsers ? '' : 'none';
  });

  if (visibleUsers >= rows.length) {
    showMoreUsersBtn.style.display = 'none';
    noMoreUsersMsg.style.display = 'block';
  } else {
    showMoreUsersBtn.style.display = 'inline-block';
    noMoreUsersMsg.style.display = 'none';
  }
}

function showMoreUsers(step = 5) {
  visibleUsers += step;
  updateUsersVisibility();
}

function updateTodosVisibility() {
  const rows = todosTable.querySelectorAll('tbody tr');

  rows.forEach((row, i) => {
    row.style.display = i < visibleTodos ? '' : 'none';
  });

  if (visibleTodos >= rows.length) {
    showMoreTodosBtn.style.display = 'none';
    noMoreTodosMsg.style.display = 'block';
  } else {
    showMoreTodosBtn.style.display = 'inline-block';
    noMoreTodosMsg.style.display = 'none';
  }
}

function showMoreTodos(step = 5) {
  visibleTodos += step;
  updateTodosVisibility();
}

function updateTicketsVisibility() {
  const rows = ticketsTable.querySelectorAll('tbody tr');

  rows.forEach((row, i) => {
    row.style.display = i < visibleTickets ? '' : 'none';
  });

  if (visibleTickets >= rows.length) {
    showMoreTicketsBtn.style.display = 'none';
    noMoreTicketsMsg.style.display = 'block';
  } else {
    showMoreTicketsBtn.style.display = 'inline-block';
    noMoreTicketsMsg.style.display = 'none';
  }
}

function showMoreTickets(step = 5) {
  visibleTickets += step;
  updateTicketsVisibility();
}

// ----------------------------
// FILTER FUNCTIONALITY
// ----------------------------

function filterUsers() {
  console.log("filtered users")
  const input = document.getElementById('userSearch').value.toLowerCase();
  const rows = document.querySelectorAll('#usersTable tbody tr');

  if (input) {
    rows.forEach(row => {
      const username = row.cells[1].textContent.toLowerCase();
      row.style.display = username.includes(input) ? '' : 'none';
    });
    showMoreUsersBtn.style.display = 'none';
    noMoreUsersMsg.style.display = 'none';
  } else {
    updateUsersVisibility();
  }
}

function filterTodos() {
  console.log("filtered todos")
  const input = document.getElementById('todoSearch').value.toLowerCase();
  const rows = document.querySelectorAll('#todosTable tbody tr');

  if (input) {
    rows.forEach(row => {
      const title = row.cells[2].textContent.toLowerCase();
      row.style.display = title.includes(input) ? '' : 'none';
    });
    showMoreTodosBtn.style.display = 'none';
    noMoreTodosMsg.style.display = 'none';
  } else {
    updateTodosVisibility();
  }
}

function filterTickets() {
  console.log("filtered tickets")
  const input = document.getElementById('ticketSearch').value.toLowerCase();
  const rows = document.querySelectorAll('#ticketsTable tbody tr');

  if (input) {
    rows.forEach(row => {
      const user = row.cells[1].textContent.toLowerCase();
      const title = row.cells[2].textContent.toLowerCase();
      row.style.display = user.includes(input) || title.includes(input) ? '' : 'none';
    });
    showMoreTicketsBtn.style.display = 'none';
    noMoreTicketsMsg.style.display = 'none';
  } else {
    updateTicketsVisibility();
  }
}



document.addEventListener('DOMContentLoaded', () => {
  updateUsersVisibility();
  updateTodosVisibility();
  updateTicketsVisibility();

  if (showMoreUsersBtn){
    showMoreUsersBtn.addEventListener('click', () => showMoreUsers());
  }

  if (showMoreTodosBtn) {
    showMoreTodosBtn.addEventListener('click', () => showMoreTodos());
  }

  if (showMoreTicketsBtn){
    showMoreTicketsBtn.addEventListener('click', () => showMoreTickets());
  }
});

usersFilterInput.addEventListener('keyup', function(){
  filterUsers();
});

todosFilterInput.addEventListener('keyup', function(){
  filterTodos();
});

ticketsFilterInput.addEventListener('keyup', function(){
  filterTickets();
});
