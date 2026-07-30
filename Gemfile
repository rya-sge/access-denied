source "https://rubygems.org"

# Pinned to the exact version set GitHub Pages builds with today — the build log
# reports `github-pages v232 / jekyll v3.10.0`. Pinning it means a local preview,
# CI, and production all resolve to the same gems, so the site cannot render one
# way locally and another way live.
#
# The `github-pages` gem also brings in the plugins declared in _config.yml
# (jekyll-paginate, jekyll-feed, jekyll-seo-tag, jekyll-sitemap), so those must
# NOT be listed separately here or their versions would fight with this pin.
#
# NOTE: building through GitHub Actions (.github/workflows/pages.yml) runs Jekyll
# WITHOUT safe mode, so unlike the classic Pages build, _plugins/ is executed.
gem "github-pages", "~> 232", group: :jekyll_plugins

# Faraday v2 moved the retry middleware into a separate gem; required by the
# GitHub metadata tooling to silence the "install faraday-retry" warning.
gem "faraday-retry"

# Ruby 3.0 removed webrick from the standard library, and Jekyll 3.x still needs
# it for `jekyll serve`. Not used by `jekyll build`.
gem "webrick", "~> 1.8"

# Windows and JRuby do not ship zoneinfo files, so bundle them.
gem "tzinfo-data", platforms: [:mingw, :mswin, :x64_mingw, :jruby]
