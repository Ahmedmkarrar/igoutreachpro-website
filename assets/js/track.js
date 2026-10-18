/* Product analytics: PostHog pageviews plus the clicks that matter for the funnel. */
(function () {
  if (!window.posthog) return;
  function where(el) {
    var sec = el.closest('section[id], header, footer, .mcta');
    if (!sec) return 'page';
    return sec.id || (sec.classList.contains('mcta') ? 'mobile-bar' : sec.tagName.toLowerCase());
  }
  document.addEventListener('click', function (e) {
    var el = e.target.closest('a, button');
    if (!el) return;
    var href = el.getAttribute('href') || '';
    var props = { location: where(el), label: (el.textContent || '').trim().slice(0, 60) };
    if (href.indexOf('chromewebstore.google.com') !== -1 || href === '/install') {
      posthog.capture('install_clicked', props);
    } else if (el.classList.contains('tpl-copy') || el.id === 'copyTpl') {
      posthog.capture('template_copied', props);
    } else if (el.classList.contains('tpl-try')) {
      posthog.capture('template_previewed', props);
    } else if (el.dataset.video) {
      posthog.capture('testimonial_played', { video: el.dataset.video, location: props.location });
    } else if (/^\/(alternatives|guides|instagram-dm-templates)\//.test(href)) {
      posthog.capture('content_link_clicked', { to: href, location: props.location });
    }
  }, true);
})();
