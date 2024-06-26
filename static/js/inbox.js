const toggleButton = document.querySelector('.dark-light');
const colors = document.querySelectorAll('.color');

if (localStorage.darkMode == 'true') { document.body.classList.add('dark-mode'); }
else { document.body.classList.remove('dark-mode'); }

document.body.setAttribute('data-theme', localStorage.colorTheme)
colors.forEach(c => {
  if (c.getAttribute('data-color') === localStorage.colorTheme) {
    c.classList.add('selected');
  } else {
    c.classList.remove('selected')
  }
});

colors.forEach(color => {
  color.addEventListener('click', (e) => {
    colors.forEach(c => c.classList.remove('selected'));
    const theme = color.getAttribute('data-color');
    document.body.setAttribute('data-theme', theme);
    color.classList.add('selected');
    localStorage.colorTheme = theme;
  });
});

toggleButton.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');

  if (document.body.classList.contains('dark-mode')) {
    localStorage.setItem('darkMode', true);
  } else {
    localStorage.setItem('darkMode', false);
  }
});