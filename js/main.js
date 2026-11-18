$(document).ready(function () {

  'use strict';

  /* =========================================================
  // Configuration injected by Jekyll (_includes/javascripts.html)
  //
  // Paths and UI strings are NOT hardcoded here: they depend on
  // site.baseurl and on the page language. The fallbacks below only
  // apply if the script is loaded without the config block.
  ========================================================= */

  var config = window.siteConfig || {};
  var paths = {
    searchJson: config.searchJson || '/search.json',
    page: config.pagePath || '/page/'
  };
  var strings = config.i18n || {};
  var textNoResults = strings.noResults || 'No results found';
  var textLoading = strings.loading || 'Loading...';
  var textHeadingLink = strings.headingLink || 'Link to this section';
  var textTocTitle = strings.tocTitle || 'Contents';

  /* =======================
  // Light / dark theme
  //
  // The theme is already applied by the inline bootstrap in _includes/head.html
  // (before first paint, to avoid a flash). This only handles the toggle and
  // persists the choice.
  //
  // Without a stored choice the bootstrap follows the system setting
  // (prefers-color-scheme); a click here stores an explicit choice.
  ======================= */

  var $themeToggle = $('#js-theme-toggle');

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    $themeToggle.attr('aria-pressed', theme === 'dark' ? 'true' : 'false');
  }

  // Sync the button state with whatever the bootstrap script decided.
  applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');

  $themeToggle.on('click', function () {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try {
      localStorage.setItem('theme', next);
    } catch (e) { /* storage unavailable: the choice just will not persist */ }
  });

  /* =======================
  // Simple Search Settings
  ======================= */

  /*
  https://github.com/christian-fei/Simple-Jekyll-Search/issues/140
  https://github.com/christian-fei/Simple-Jekyll-Search/issues/132
  https://github.com/lynn9388/light-blog/blob/f43172f7aae9f18c09c9c1a24f948e7929bff522/_includes/modules/search-box.html
   */
  SimpleJekyllSearch({
    searchInput: document.getElementById('js-search-input'),
    resultsContainer: document.getElementById('js-results-container'),
    json: paths.searchJson,
    searchResultTemplate: '<li><a href="{url}">{title}</a></li>',
    noResultsText: '<li>' + textNoResults + '</li>'
  })

  /* =======================
  // Responsive videos
  ======================= */

  $('.c-wrap-content').fitVids({
    'customSelector': ['iframe[src*="ted.com"]']
  });

  /* =======================
  // Open diagrams full size
  ======================= */

  // Mindmaps and PlantUML diagrams are scaled down to the column, which makes
  // their labels hard to read. Each article image that is not already a link
  // now opens the full-size file in a new tab.
  $('.c-wrap-content img').each(function () {
    if ($(this).closest('a').length) return;
    $(this).wrap($('<a>', {
      href: this.currentSrc || this.src,
      target: '_blank',
      rel: 'noopener',
      'class': 'c-zoomable'
    }));
  });

  /* =======================================
  // Switching between posts and categories
  ======================================= */

  // The tabs are <button data-target="posts|categories"> inside the <li>s, so they
  // are keyboard-reachable. Selecting by data-target instead of :last-child also
  // means the behaviour no longer depends on the order of the markup.
  $('.c-nav__list .c-nav__item').on('click', function () {
    var showCategories = $(this).data('target') === 'categories';

    $('.c-nav__list .c-nav__item').removeClass('is-active').attr('aria-selected', 'false');
    $(this).addClass('is-active').attr('aria-selected', 'true');

    if (showCategories) {
      $('.c-posts').css('display', 'none').removeClass('o-opacity');
      $('.c-load-more').css('display', 'none');
      $('.c-categories').css('display', '').addClass('o-opacity');
    } else {
      $('.c-posts').css('display', '').addClass('o-opacity');
      $('.c-load-more').css('display', '');
      $('.c-categories').css('display', 'none').removeClass('o-opacity');
    }
  });

  /* =======================
  // Adding ajax pagination
  ======================= */

  $(".c-load-more").click(loadMorePosts);

  function loadMorePosts() {
    var _this = this;
    var $postsContainer = $('.c-posts');
    var nextPage = parseInt($postsContainer.attr('data-page')) + 1;
    var totalPages = parseInt($postsContainer.attr('data-totalPages'));

    $(this).addClass('is-loading').text(textLoading);

    $.get(paths.page + nextPage, function (data) {
      var htmlData = $.parseHTML(data);
      var $articles = $(htmlData).find('article');

      $postsContainer.attr('data-page', nextPage).append($articles);

      if ($postsContainer.attr('data-totalPages') == nextPage) {
        $('.c-load-more').remove();
      }

      $(_this).removeClass('is-loading');
    });
  }

  /* ==============================
  // Smooth scroll to the tags page
  ============================== */

  $('.c-tag__list a').on('click', function (e) {
    e.preventDefault();

    var currentTag = $(this).attr('href'),
      currentTagOffset = $(currentTag).offset().top;

    $('html, body').animate({
      scrollTop: currentTagOffset - 10
    }, 400);

  });

  /* =======================
  // Scroll to top
  ======================= */

  $('.c-top').click(function () {
    $('html, body').stop().animate({ scrollTop: 0 }, 'slow', 'swing');
  });
  $(window).scroll(function () {
    if ($(this).scrollTop() > $(window).height()) {
      $('.c-top').addClass("c-top--active");
    } else {
      $('.c-top').removeClass("c-top--active");
    };
  });

  /* =======================
  // Article reading aids
  //
  // Only on article pages (.c-wrap-content is rendered by _layouts/post.html).
  // All three are progressive: without JavaScript the article reads as before.
  ======================= */

  var article = document.querySelector('.c-wrap-content');
  if (article) {

    // Heading anchors: a "#" after each section heading, so a reader can copy
    // a link to the section. Kramdown already gives every heading an id.
    $(article).find('h2[id], h3[id]').each(function () {
      $('<a>', {
        'class': 'c-heading-anchor',
        href: '#' + this.id,
        'aria-label': textHeadingLink,
        title: textHeadingLink,
        text: '#'
      }).appendTo(this);
    });

    // Reading progress: a thin bar at the top of the window, filled as the
    // reader moves from the start to the end of the article body.
    var $progress = $('<div class="c-reading-progress" aria-hidden="true"><span></span></div>').appendTo('body');
    var progressBar = $progress.children()[0];
    var progressPending = false;
    function updateProgress() {
      progressPending = false;
      var rect = article.getBoundingClientRect();
      var total = rect.height - window.innerHeight;
      var done = total > 0 ? Math.min(1, Math.max(0, -rect.top / total)) : 1;
      progressBar.style.transform = 'scaleX(' + done + ')';
    }
    $(window).on('scroll resize', function () {
      if (!progressPending) {
        progressPending = true;
        window.requestAnimationFrame(updateProgress);
      }
    });
    updateProgress();

    // Sticky table of contents. On a wide screen the space right of the card
    // is empty; when it is wide enough, a copy of the article's TOC is fixed
    // there and the section being read is highlighted. The inline TOC stays
    // in the article for narrower screens, no-JS readers and crawlers.
    var tocList = article.querySelector('.c-toc__list');
    if (tocList && 'IntersectionObserver' in window) {
      var $rail = $('<nav class="c-toc-rail"></nav>').attr('aria-label', textTocTitle)
        .append($('<p class="c-toc__title"></p>').text(textTocTitle))
        .append($(tocList).clone().removeClass('c-toc__list').addClass('c-toc-rail__list'))
        .appendTo('body');
      // When the rail is hidden (narrow screen) its links leave the tab order,
      // so keyboard users do not land on invisible links.
      var RAIL_MIN = 220;
      var placeRail = function () {
        var cardRight = article.getBoundingClientRect().right;
        var space = window.innerWidth - cardRight - 48;
        if (space >= RAIL_MIN) {
          $rail.css({ left: (cardRight + 24) + 'px', width: Math.min(300, space) + 'px' })
            .addClass('is-visible').find('a').removeAttr('tabindex');
        } else {
          $rail.removeClass('is-visible').find('a').attr('tabindex', '-1');
        }
      };
      $(window).on('resize', placeRail);
      placeRail();

      var railLinks = {};
      $rail.find('a[href^="#"]').each(function () {
        railLinks[decodeURIComponent(this.getAttribute('href').slice(1))] = this;
      });
      var headings = $(article).find('h2[id], h3[id]').toArray().filter(function (h) {
        return railLinks[h.id];
      });
      var observer = new IntersectionObserver(function () {
        // The current section is the last heading above the middle of the screen.
        var current = null;
        headings.forEach(function (h) {
          if (h.getBoundingClientRect().top < window.innerHeight / 2) current = h.id;
        });
        $rail.find('a.is-active').removeClass('is-active');
        if (current && railLinks[current]) railLinks[current].classList.add('is-active');
      }, { rootMargin: '0px 0px -50% 0px' });
      headings.forEach(function (h) { observer.observe(h); });
    }
  }


});
