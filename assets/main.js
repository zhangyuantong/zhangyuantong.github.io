/* Small, dependency-free behaviours for the site. */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- hero: split the name into characters so they can stagger in ---- */

  var heroTitle = document.querySelector('.hero h1');

  if (heroTitle && !reduceMotion) {
    var text = heroTitle.textContent;
    var frag = document.createDocumentFragment();

    for (var i = 0; i < text.length; i++) {
      var span = document.createElement('span');
      span.className = 'ch';
      span.style.setProperty('--i', i);
      span.textContent = text[i];
      frag.appendChild(span);
    }

    heroTitle.textContent = '';
    heroTitle.appendChild(frag);
  }

  /* ---- header: solid background once the page has scrolled ---- */

  var header = document.querySelector('.site-header');

  function onScroll() {
    if (header) {
      header.classList.toggle('is-scrolled', window.scrollY > 12);
    }

    var bar = document.querySelector('.reading-progress');
    if (bar) {
      var scrollable = document.documentElement.scrollHeight - window.innerHeight;
      var ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
      bar.style.transform = 'scaleX(' + Math.min(ratio, 1) + ')';
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- pointer spotlight ---- */

  if (!reduceMotion && window.matchMedia('(hover: hover)').matches) {
    var pending = false;
    var x = 0;
    var y = 0;

    window.addEventListener('pointermove', function (event) {
      x = event.clientX;
      y = event.clientY;

      if (!pending) {
        pending = true;
        requestAnimationFrame(function () {
          document.documentElement.style.setProperty('--mx', x + 'px');
          document.documentElement.style.setProperty('--my', y + 'px');
          document.body.classList.add('has-pointer');
          pending = false;
        });
      }
    }, { passive: true });
  }

  /* ---- reveal blocks as they enter the viewport ---- */

  var revealables = document.querySelectorAll('.reveal');

  if (!('IntersectionObserver' in window) || reduceMotion) {
    revealables.forEach(function (el) { el.classList.add('in'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.1 });

    revealables.forEach(function (el) { observer.observe(el); });
  }

  /* ---- math: render $...$ and $$...$$ with the bundled KaTeX ---- */

  if (window.renderMathInElement) {
    window.renderMathInElement(document.body, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '\\[', right: '\\]', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false }
      ],
      ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
      throwOnError: false
    });
  }

  /* ---- footer year ---- */

  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
