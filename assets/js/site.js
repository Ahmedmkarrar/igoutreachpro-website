/* IG Outreach Pro — site interactions. No dependencies. */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------- Nav ---------------- */
  var nav = document.getElementById('nav');
  var burger = document.getElementById('burger');

  if (nav) {
    var onScroll = function () {
      nav.classList.toggle('stuck', window.scrollY > 12);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('.nav-links a').forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------------- Reveal on scroll ---------------- */
  var revealables = document.querySelectorAll('.rv');
  if (reduce || !('IntersectionObserver' in window)) {
    revealables.forEach(function (el) { el.classList.add('in'); });
  } else {
    var rvIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('in');
        rvIO.unobserve(e.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px' });
    revealables.forEach(function (el) { rvIO.observe(el); });
  }

  /* ---------------- YouTube facade: click a poster, load the real player ---------------- */
  document.querySelectorAll('.player[data-yt]').forEach(function (player) {
    function load() {
      if (player.classList.contains('playing')) return;
      var id = player.dataset.yt;
      var frame = document.createElement('iframe');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + id +
        '?autoplay=1&rel=0&modestbranding=1&playsinline=1';
      frame.title = player.getAttribute('aria-label') || 'IG Outreach Pro video';
      frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      frame.allowFullscreen = true;
      frame.loading = 'lazy';
      player.classList.add('playing');
      player.appendChild(frame);
      player.removeAttribute('role');
      player.removeAttribute('tabindex');
    }

    player.addEventListener('click', load);
    player.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        load();
      }
    });

    // Warm the connection on hover so playback starts faster.
    player.addEventListener('mouseenter', function warm() {
      player.removeEventListener('mouseenter', warm);
      [
        'https://www.youtube-nocookie.com',
        'https://www.google.com',
        'https://googlevideo.com',
        'https://static.doubleclick.net'
      ].forEach(function (host) {
        var l = document.createElement('link');
        l.rel = 'preconnect';
        l.href = host;
        l.crossOrigin = '';
        document.head.appendChild(l);
      });
    }, { once: true });
  });

  /* ---------------- Product tour tabs ---------------- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tour-tab'));
  if (tabs.length) {
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.dataset.panel);
        if (panel) {
          if (on) panel.setAttribute('data-on', '');
          else panel.removeAttribute('data-on');
        }
      });
      if (focus) tab.focus();
    }

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () { select(tab); });
      tab.addEventListener('keydown', function (e) {
        var i = tabs.indexOf(tab);
        var next = null;
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
        else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
        else if (e.key === 'Home') next = tabs[0];
        else if (e.key === 'End') next = tabs[tabs.length - 1];
        if (next) {
          e.preventDefault();
          select(next, true);
        }
      });
    });
  }

  /* ---------------- Savings calculator ---------------- */
  var slider = document.getElementById('vaSlider');
  if (slider) {
    var PRO_PER_YEAR = 29.99 * 12; // 359.88
    var money = function (n) {
      return '$' + Math.round(n).toLocaleString('en-US');
    };
    var out = {
      monthly: document.getElementById('vaMonthly'),
      year: document.getElementById('vaYear'),
      keep: document.getElementById('youKeep'),
      inline: document.getElementById('keepInline')
    };

    function update() {
      var m = +slider.value;
      var year = m * 12;
      var keep = year - PRO_PER_YEAR;
      var pct = ((m - slider.min) / (slider.max - slider.min)) * 100;
      slider.style.setProperty('--fill', pct + '%');
      if (out.monthly) out.monthly.textContent = money(m);
      if (out.year) out.year.textContent = money(year);
      if (out.keep) out.keep.textContent = money(keep);
      if (out.inline) out.inline.textContent = money(keep);
    }

    slider.addEventListener('input', update);
    update();
  }

  /* ---------------- Footer year ---------------- */
  var yr = document.getElementById('yr');
  if (yr) yr.textContent = String(new Date().getFullYear());
})();
