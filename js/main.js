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

  /* =======================
  // Light / dark theme
  //
  // The theme is already applied by the inline bootstrap in _includes/head.html
  // (before first paint, to avoid a flash). This only handles the toggle and
  // persists the choice.
  //
  // Light is the default on purpose: no prefers-color-scheme fallback, so a
  // visitor keeps the white site unless they explicitly ask for dark.
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


});
