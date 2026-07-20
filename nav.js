/* nav.js — injects shared nav overlay and footer */
(function () {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  const pages = [
    { href: 'index.html',        label: 'Home' },
    { href: 'history.html',      label: 'Our History' },
    { href: 'news-events.html',  label: 'News & Events' },
    { href: 'facilities.html',   label: 'Facilities' },
    { href: 'nature-trail.html', label: 'Nature Trail' },
    { href: 'donate.html',       label: 'Donate' },
    { href: 'photo-archive.html',label: 'Photo Archive' },
    { href: 'executive.html',    label: 'Executive' },
    { href: 'contact.html',      label: 'Contact' },
  ];

  const navHTML = `
  <nav>
    <a href="index.html" class="nav-brand">
      <img class="nav-logo-img" src="NCC_logo.png" alt="NCC Logo" />
      <div class="nav-brand-text">Nauwigewauk<small>Community Club Inc.</small></div>
    </a>
    <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false">
      <span class="menu-btn-lines"><span></span><span></span></span>
      <span class="menu-btn-label">Menu</span>
    </button>
  </nav>
  <div class="menu-overlay" id="menuOverlay">
    <div class="menu-overlay-top">
      <a href="index.html" class="nav-brand">
        <img class="nav-logo-img" src="NCC_logo.png" alt="NCC Logo" />
        <div class="nav-brand-text">Nauwigewauk<small>Community Club Inc.</small></div>
      </a>
      <button class="menu-close" id="menuClose" aria-label="Close menu">&times;</button>
    </div>
    <ul class="menu-list">
      ${pages.map((p,i) => `<li><a href="${p.href}" class="${path===p.href?'active':''}"><span class="menu-num">${String(i+1).padStart(2,'0')}</span>${p.label}</a></li>`).join('')}
    </ul>
    <div class="menu-overlay-bottom">
      <span>Est. 1948 · Route 100, New Brunswick</span>
      <a href="contact.html">Get in touch →</a>
    </div>
  </div>`;

  const footerHTML = `
  <div class="contact-strip">
    <div class="contact-inner">
      <div>
        <h2>Be Part of the <em>Community</em></h2>
        <p>Whether a longtime resident or new to the area — everyone is welcome.</p>
      </div>
      <div style="display:flex; gap:1rem; flex-wrap:wrap;">
        <a href="donate.html" class="btn btn-outline-navy">Donate</a>
        <a href="contact.html" class="btn btn-navy">Get In Touch</a>
      </div>
    </div>
  </div>
  <footer>
    <img src="NCC_logo.png" alt="NCC" />
    <div class="footer-text">© 2026 Nauwigewauk Community Club Inc. · Route 100, New Brunswick, Canada</div>
    <div class="footer-links">
      <a href="history.html">Our History</a>
      <a href="donate.html">Donate</a>
      <a href="contact.html">Contact</a>
    </div>
  </footer>`;

  document.body.insertAdjacentHTML('afterbegin', navHTML);
  document.body.insertAdjacentHTML('beforeend', footerHTML);

  // menu toggle
  const menuBtn = document.getElementById('menuBtn');
  const menuClose = document.getElementById('menuClose');
  const overlay = document.getElementById('menuOverlay');
  function openMenu() {
    overlay.classList.add('open');
    menuBtn.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    overlay.classList.remove('open');
    menuBtn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
  menuBtn.addEventListener('click', openMenu);
  menuClose.addEventListener('click', closeMenu);
  overlay.querySelectorAll('.menu-list a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });

  // scroll reveal
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 90);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
})();

