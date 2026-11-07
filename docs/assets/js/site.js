(function () {
  var d = document, root = d.documentElement;
  root.classList.remove('no-js');

  // Mobile menu
  var btn = d.querySelector('.menu-btn');
  if (btn) btn.addEventListener('click', function () {
    var open = d.body.classList.toggle('menu-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  d.querySelectorAll('.mobile-menu a').forEach(function (a) {
    a.addEventListener('click', function () { d.body.classList.remove('menu-open'); });
  });

  // Header border + sticky CTA
  var header = d.querySelector('.site-header'), sticky = d.querySelector('.sticky-cta');
  var onScroll = function () {
    var y = window.scrollY;
    if (header) header.classList.toggle('scrolled', y > 8);
    if (sticky) {
      var nearEnd = (window.innerHeight + y) > (d.body.scrollHeight - 700);
      sticky.classList.toggle('show', y > 560 && !nearEnd);
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // Reveal on scroll
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    d.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
  } else d.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });

  // Lightbox
  var items = Array.prototype.slice.call(d.querySelectorAll('[data-full]'));
  if (items.length) {
    var lb = d.createElement('div'); lb.className = 'lightbox'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo viewer');
    lb.innerHTML = '<img alt=""><button class="lb-close" aria-label="Close">×</button><button class="lb-prev" aria-label="Previous">‹</button><button class="lb-next" aria-label="Next">›</button><div class="lb-caption"></div>';
    d.body.appendChild(lb);
    var img = lb.querySelector('img'), cap = lb.querySelector('.lb-caption'), idx = 0, last;
    var show = function (i) {
      idx = (i + items.length) % items.length;
      var el = items[idx]; img.src = el.getAttribute('data-full');
      img.alt = el.querySelector('img').alt; cap.textContent = img.alt;
    };
    var close = function () { lb.classList.remove('open'); d.body.style.overflow = ''; if (last) last.focus(); };
    items.forEach(function (el, i) {
      el.addEventListener('click', function () { last = el; show(i); lb.classList.add('open'); d.body.style.overflow = 'hidden'; lb.querySelector('.lb-close').focus(); });
    });
    lb.querySelector('.lb-close').onclick = close;
    lb.querySelector('.lb-prev').onclick = function () { show(idx - 1); };
    lb.querySelector('.lb-next').onclick = function () { show(idx + 1); };
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    d.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
    var sx = 0;
    lb.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      var dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
    });
  }

  // Enquiry form: compose an email (no backend needed on static hosting)
  var form = d.getElementById('enquiry');
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.reportValidity()) return;
    var f = new FormData(form), types = f.getAll('type').join(', ') || 'Not specified';
    var lines = [
      'Name: ' + f.get('name'),
      'Company: ' + (f.get('company') || '-'),
      'Email: ' + f.get('email'),
      'Phone: ' + (f.get('phone') || '-'),
      'Project type: ' + types,
      'Preferred date(s): ' + (f.get('date') || '-'),
      'People on camera / in session: ' + (f.get('people') || '-'),
      'Budget: ' + (f.get('budget') || '-'),
      '', f.get('message') || ''
    ];
    var subject = 'Studio enquiry: ' + types + (f.get('company') ? ' (' + f.get('company') + ')' : '');
    window.location.href = 'mailto:' + form.getAttribute('data-to') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n'));
    var ok = d.getElementById('form-ok'); if (ok) ok.hidden = false;
  });

  var yr = d.getElementById('yr'); if (yr) yr.textContent = new Date().getFullYear();
})();
