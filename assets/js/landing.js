/* IG Outreach Pro — landing interactions. No dependencies. */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;

  /* ---------------- Nav ---------------- */
  var nav = document.getElementById('nav');
  var burger = document.getElementById('burger');

  function onScroll() { nav.classList.toggle('stuck', window.scrollY > 12); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  function closeMenu() {
    nav.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
  }
  burger.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    burger.setAttribute('aria-expanded', String(open));
  });
  nav.querySelectorAll('.nav-links a').forEach(function (a) { a.addEventListener('click', closeMenu); });

  /* ---------------- Reveal on scroll ---------------- */
  var revealables = document.querySelectorAll('.rv, .hub');
  if (reduce || !hasIO) {
    revealables.forEach(function (el) { el.classList.add('in'); });
  } else {
    var rvIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('in');
        rvIO.unobserve(e.target);
      });
    }, { threshold: 0, rootMargin: '0px 0px -40px 0px' });
    revealables.forEach(function (el) { rvIO.observe(el); });
  }

  /* ---------------- Hero: typed target examples ---------------- */
  var typer = document.getElementById('typer');
  var targets = [
    'followers of @yourcompetitor',
    'people posting #onlinecoach',
    'accounts @industryleader follows',
    'your imported lead list',
    'people posting #realestateagent'
  ];
  var ti = 0, ci = targets[0].length, deleting = true;
  if (typer && !reduce) {
    var tick = function () {
      ci += deleting ? -1 : 1;
      if (deleting && ci <= 0) {
        deleting = false;
        ti = (ti + 1) % targets.length;
      }
      typer.textContent = targets[ti].slice(0, ci) || '\u00a0';
      if (!deleting && ci >= targets[ti].length) {
        deleting = true;
        return setTimeout(tick, 2200);
      }
      setTimeout(tick, deleting ? 28 : 55);
    };
    setTimeout(tick, 2600);
  }

  /* ---------------- YouTube facade (hero walkthrough) ---------------- */
  function ytSrc(id) {
    return 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&modestbranding=1&playsinline=1';
  }
  function makeFrame(id, title) {
    var f = document.createElement('iframe');
    f.src = ytSrc(id);
    f.title = title;
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.allowFullscreen = true;
    return f;
  }

  document.querySelectorAll('.player[data-yt]').forEach(function (player) {
    function load() {
      if (player.classList.contains('playing')) return;
      player.classList.add('playing');
      player.appendChild(makeFrame(player.dataset.yt, player.getAttribute('aria-label') || 'IG Outreach Pro video'));
      player.removeAttribute('role');
      player.removeAttribute('tabindex');
    }
    player.addEventListener('click', load);
    player.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      e.preventDefault();
      load();
    });
  });

  /* ---------------- Testimonial video modal with a play-all playlist ---------------- */
  var PLAYLIST = ['4QfbFwU-nrU', 'V023sIzUbjE', 'X1p0nB10GHw', 'KKrw2d9_rZk', 'UbSb2e4Ebhs'];
  var modal = document.getElementById('vmodal');
  var frameBox = document.getElementById('vmFrame');
  var vmCount = document.getElementById('vmCount');
  var lastFocus = null, current = 0;

  function showVideo(i) {
    current = (i + PLAYLIST.length) % PLAYLIST.length;
    frameBox.innerHTML = '';
    frameBox.appendChild(makeFrame(PLAYLIST[current], 'Customer testimonial video'));
    if (vmCount) vmCount.textContent = 'Customer ' + (current + 1) + ' of ' + PLAYLIST.length;
  }
  function openVideo(id) {
    lastFocus = document.activeElement;
    var i = PLAYLIST.indexOf(id);
    showVideo(i < 0 ? 0 : i);
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    modal.querySelector('.vm-x').focus();
  }
  function closeVideo() {
    modal.hidden = true;
    frameBox.innerHTML = '';
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-video]');
    if (btn && modal) openVideo(btn.dataset.video);
  });
  if (modal) {
    modal.querySelectorAll('[data-close]').forEach(function (el) { el.addEventListener('click', closeVideo); });
    var prev = document.getElementById('vmPrev'), next = document.getElementById('vmNext');
    if (prev) prev.addEventListener('click', function () { showVideo(current - 1); });
    if (next) next.addEventListener('click', function () { showVideo(current + 1); });
  }
  document.addEventListener('keydown', function (e) {
    if (!modal || modal.hidden) return;
    if (e.key === 'Escape') closeVideo();
    else if (e.key === 'ArrowRight') showVideo(current + 1);
    else if (e.key === 'ArrowLeft') showVideo(current - 1);
  });

  /* ---------------- Silent preview loops: load and play only while on screen ---------------- */
  var loops = document.querySelectorAll('video.vw-loop');
  if (loops.length && hasIO && !reduce) {
    var lIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) {
          if (!v.src) v.src = v.dataset.src;
          var p = v.play();
          if (p && p.catch) p.catch(function () {});
          v.addEventListener('playing', function () { v.classList.add('on'); }, { once: true });
        } else if (!v.paused) {
          v.pause();
        }
      });
    }, { threshold: 0.25 });
    loops.forEach(function (v) { lIO.observe(v); });
  }

  /* ---------------- Marquee: duplicate cards for a seamless loop ---------------- */
  var track = document.querySelector('.mq-track');
  if (track) {
    var originals = Array.prototype.slice.call(track.children);
    for (var r = 0; r < 3; r++) {
      originals.forEach(function (card) {
        var clone = card.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        clone.querySelectorAll('a, button').forEach(function (el) { el.tabIndex = -1; });
        track.appendChild(clone);
      });
    }
  }

  /* ---------------- Feature carousel: tap to open on touch ---------------- */
  document.querySelectorAll('.fcard').forEach(function (card) {
    card.addEventListener('click', function () {
      document.querySelectorAll('.fcard.open').forEach(function (c) { if (c !== card) c.classList.remove('open'); });
      card.classList.toggle('open');
    });
  });

  /* ---------------- Counters ---------------- */
  function runCounter(el) {
    var to = parseFloat(el.dataset.to);
    var pre = el.dataset.prefix || '';
    var suf = el.dataset.suffix || '';
    if (reduce) { el.textContent = pre + to + suf; return; }
    var start = null, dur = 1400;
    function step(t) {
      if (start === null) start = t;
      var p = Math.min((t - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = pre + Math.round(to * eased) + suf;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var counters = document.querySelectorAll('.counter');
  if (hasIO) {
    var cIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        runCounter(e.target);
        cIO.unobserve(e.target);
      });
    }, { threshold: 0 });
    counters.forEach(function (c) { cIO.observe(c); });
  } else {
    counters.forEach(runCounter);
  }

  /* ---------------- How-it-works: highlight current step ---------------- */
  var stepLinks = document.querySelectorAll('.how-nav a');
  if (hasIO && stepLinks.length) {
    var sIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var n = e.target.dataset.step;
        stepLinks.forEach(function (a) { a.classList.toggle('on', a.dataset.step === n); });
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    document.querySelectorAll('.how-step').forEach(function (s) { sIO.observe(s); });
  }


  /* ================================================================
     Niches: drive the hero typer, the playground and the templates.
     Placeholder + spintax syntax matches the extension exactly
     ({firstname} {fullname} {username}, nested {a|b}).
     ================================================================ */
  var NICHES = window.NICHES || {};
  var pageNiche = document.body.dataset.niche;
  var niche = pageNiche && NICHES[pageNiche] ? pageNiche : 'coaches';

  /* ---------------- Spintax engine (ported from the extension) ---------------- */
  function spin(text) {
    var s = text.replace(/\{username\}/gi, '\u0001').replace(/\{firstname\}/gi, '\u0002').replace(/\{fullname\}/gi, '\u0003');
    var re = /\{([^{}]*\|[^{}]*)\}/, m, guard = 0;
    while ((m = re.exec(s)) && guard++ < 500) {
      var parts = m[1].split('|');
      s = s.slice(0, m.index) + parts[Math.floor(Math.random() * parts.length)] + s.slice(m.index + m[0].length);
    }
    return s.replace(/\u0001/g, '{username}').replace(/\u0002/g, '{firstname}').replace(/\u0003/g, '{fullname}');
  }
  function fill(text, person) {
    var first = person[1].split(' ')[0];
    return spin(text).replace(/\{username\}/gi, person[0]).replace(/\{firstname\}/gi, first).replace(/\{fullname\}/gi, person[1]);
  }
  // Count unique outputs: resolve innermost groups first, multiplying option counts.
  function countVariants(text) {
    var s = text.replace(/\{(username|firstname|fullname)\}/gi, '');
    var total = 1, re = /\{([^{}]*\|[^{}]*)\}/, m, guard = 0;
    while ((m = re.exec(s)) && guard++ < 500) {
      total *= m[1].split('|').length;
      s = s.slice(0, m.index) + 'x' + s.slice(m.index + m[0].length);
    }
    return total;
  }
  function esc(t) { return t.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function highlight(t) {
    return esc(t)
      .replace(/\{(firstname|fullname|username)\}/gi, '<span class="p">{$1}</span>')
      .replace(/\{([^{}]*\|[^{}]*)\}/g, '<span class="s">{$1}</span>');
  }

  /* ---------------- Toast + copy ---------------- */
  var toastEl = document.getElementById('toast'), toastT;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('on');
    clearTimeout(toastT);
    toastT = setTimeout(function () { toastEl.classList.remove('on'); }, 2200);
  }
  function copy(text) {
    var done = function () { toast('Copied. Paste it into IG Outreach Pro →'); };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else {
      fallback();
    }
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { toast('Select the text and copy it manually'); }
      ta.remove();
    }
  }

  /* ---------------- Playground ---------------- */
  var tpl = document.getElementById('tpl');
  var pvBody = document.getElementById('pvBody');
  var pvUser = document.getElementById('pvUser');
  var pvAv = document.getElementById('pvAv');
  var varCount = document.getElementById('varCount');
  var personIdx = 0;

  function renderPreview() {
    if (!tpl) return;
    var n = NICHES[niche];
    var person = n.people[personIdx % n.people.length];
    pvUser.textContent = person[0];
    pvAv.style.setProperty('--h', person[2]);
    var msg = fill(tpl.value || '', person).trim() || '…';
    pvBody.innerHTML = '<span class="stamp">Today 10:4' + (personIdx % 10) + ' AM</span>' +
      '<div class="bubble out">' + esc(msg) + '</div>' +
      '<div class="bubble in">' + esc(n.reply) + '</div>';
    var c = countVariants(tpl.value || '');
    varCount.textContent = c.toLocaleString();
  }
  if (tpl) {
    tpl.addEventListener('input', function () {
      var c = countVariants(tpl.value || '');
      varCount.textContent = c.toLocaleString();
      clearTimeout(tpl._t);
      tpl._t = setTimeout(renderPreview, 250);
    });
    document.getElementById('shuffle').addEventListener('click', function () { personIdx++; renderPreview(); });
    document.getElementById('copyTpl').addEventListener('click', function () { copy(tpl.value); });
    document.querySelectorAll('.play-ins button').forEach(function (b) {
      b.addEventListener('click', function () {
        var ins = b.dataset.insert, st = tpl.selectionStart, en = tpl.selectionEnd;
        tpl.value = tpl.value.slice(0, st) + ins + tpl.value.slice(en);
        tpl.focus();
        tpl.selectionStart = tpl.selectionEnd = st + ins.length;
        renderPreview();
      });
    });
  }

  /* ---------------- Template library ---------------- */
  var tabsEl = document.getElementById('tplTabs');
  var gridEl = document.getElementById('tplGrid');
  var tplMore = document.getElementById('tplMore');
  function renderTemplates() {
    if (!gridEl) return;
    if (tplMore && NICHES[niche].slug) {
      tplMore.href = '/instagram-dm-templates/' + NICHES[niche].slug;
      tplMore.textContent = 'More tips + templates for ' + NICHES[niche].crumb.toLowerCase() + ' →';
    }
    if (tabsEl) tabsEl.innerHTML = Object.keys(NICHES).map(function (k) {
      return '<button role="tab" aria-selected="' + (k === niche) + '" data-niche="' + k + '">' + esc(NICHES[k].label) + '</button>';
    }).join('');
    gridEl.innerHTML = NICHES[niche].templates.map(function (t, i) {
      return '<article class="tpl-card brk"><h3>' + esc(t.name) + '</h3><p class="when">' + esc(t.when) +
        ' · ' + countVariants(t.text).toLocaleString() + ' versions</p><pre>' + highlight(t.text) + '</pre>' +
        '<div class="tpl-foot"><button class="tpl-copy" data-i="' + i + '">Copy</button><button class="tpl-try" data-i="' + i + '">Edit &amp; preview</button></div></article>';
    }).join('');
  }
  if (tabsEl) {
    tabsEl.addEventListener('click', function (e) {
      var b = e.target.closest('[data-niche]');
      if (b) setNiche(b.dataset.niche, true);
    });
  }
  if (gridEl) {
    gridEl.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-i]');
      if (!b) return;
      var t = NICHES[niche].templates[+b.dataset.i];
      if (b.classList.contains('tpl-copy')) return copy(t.text);
      if (!tpl) return copy(t.text);
      tpl.value = t.text;
      renderPreview();
      document.getElementById('try').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
    });
  }

  /* ---------------- Niche switching ---------------- */
  var nicheChips = document.querySelectorAll('.niche-chip');
  function setNiche(k, keepTemplate) {
    if (!NICHES[k]) return;
    niche = k;
    nicheChips.forEach(function (c) { c.setAttribute('aria-checked', String(c.dataset.niche === k)); });
    targets = NICHES[k].targets;
    ti = 0; ci = 0; deleting = false;
    if (typer && reduce) typer.textContent = targets[0];
    if (tpl && !keepTemplate) tpl.value = NICHES[k].templates[0].text;
    personIdx = 0;
    renderPreview();
    renderTemplates();
    if (!pageNiche) { try { localStorage.setItem('igop-niche', k); } catch (e) {} }
  }
  nicheChips.forEach(function (c) { c.addEventListener('click', function () { setNiche(c.dataset.niche); }); });
  var saved = null;
  if (!pageNiche) { try { saved = localStorage.getItem('igop-niche'); } catch (e) {} }
  if (tpl) tpl.value = NICHES[saved && NICHES[saved] ? saved : niche].templates[0].text;
  setNiche(saved && NICHES[saved] ? saved : niche, true);
  if (typer && Object.keys(NICHES).length) { typer.textContent = targets[0]; ci = targets[0].length; deleting = true; }

  /* ---------------- Savings calculator ---------------- */
  var PRO_YEAR = 29.99 * 12;
  var mode = 'setter';
  function money(n) { return '$' + Math.round(n).toLocaleString(); }
  function $(id) { return document.getElementById(id); }
  function calc() {
    if (!$('calcBig')) return;
    var yearly;
    if (mode === 'setter') {
      var cost = +$('setterCost').value, n = +$('setters').value;
      $('vSetterCost').textContent = money(cost);
      $('vSetters').textContent = n;
      yearly = cost * n * 12;
      $('calcLabel').textContent = 'What your setters cost per year';
      $('calcWinLabel').textContent = 'You keep';
    } else {
      var h = +$('hours').value, r = +$('rate').value;
      $('vHours').textContent = h + 'h';
      $('vRate').textContent = money(r);
      yearly = h * r * 5 * 52;
      $('calcLabel').textContent = 'What your DM time is worth per year';
      $('calcWinLabel').textContent = 'Back in your pocket';
    }
    $('calcBig').textContent = money(yearly);
    $('calcKeep').textContent = money(Math.max(yearly - PRO_YEAR, 0));
  }
  ['setterCost', 'setters', 'hours', 'rate'].forEach(function (id) { if ($(id)) $(id).addEventListener('input', calc); });
  document.querySelectorAll('.seg button').forEach(function (b) {
    b.addEventListener('click', function () {
      mode = b.dataset.mode;
      document.querySelectorAll('.seg button').forEach(function (x) { x.setAttribute('aria-selected', String(x === b)); });
      document.querySelectorAll('.calc-fields').forEach(function (f) { f.hidden = f.dataset.for !== mode; });
      calc();
    });
  });
  calc();

  /* ---------------- Sticky mobile CTA ---------------- */
  var mcta = document.getElementById('mcta');
  var heroEl = document.getElementById('top');
  var finalEl = document.querySelector('.final');
  if (mcta && hasIO && heroEl && finalEl) {
    var heroVisible = true, finalVisible = false;
    var upd = function () { mcta.classList.toggle('on', !heroVisible && !finalVisible); };
    new IntersectionObserver(function (es) { heroVisible = es[0].isIntersecting; upd(); }, { rootMargin: '-60% 0px 0px 0px' }).observe(heroEl);
    new IntersectionObserver(function (es) { finalVisible = es[0].isIntersecting; upd(); }).observe(finalEl);
  }

  /* ---------------- Install attribution: tag every Web Store link with where it was clicked ---------------- */
  document.querySelectorAll('a[href*="chromewebstore.google.com"]').forEach(function (a) {
    var sec = a.closest('section[id], header, footer, .mcta');
    var where = a.classList.contains('mcta') ? 'sticky-mobile' : sec ? (sec.id || sec.tagName.toLowerCase()) : 'page';
    try {
      var u = new URL(a.href);
      u.searchParams.set('utm_source', 'igoutreachpro.com');
      u.searchParams.set('utm_medium', 'landing');
      u.searchParams.set('utm_campaign', where);
      a.href = u.toString();
    } catch (e) {}
  });

  /* ---------------- Footer year ---------------- */
  var yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
})();
