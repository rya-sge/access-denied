# Generates a landing page for any category that does not already have one.
#
# IMPORTANT — this plugin was dormant for years: GitHub Pages' classic build runs
# Jekyll in safe mode, which ignores _plugins/ entirely. That is why the 20 pages
# under _pages/category/ were written by hand, and why the `oracle` category
# silently ended up with no page at all (see site_improvement.md 1.2).
#
# Building through GitHub Actions instead means this file now actually executes.
# Without the guard below it would emit `category/<slug>/index.html` for EVERY
# category, colliding with all 20 checked-in pages and producing "conflicting
# output file" warnings, with one silently overwriting the other.
#
# So its role is now a safety net rather than a duplicate: the curated pages under
# _pages/category/ stay the source of truth (they carry a display `title` that may
# differ from the category key, e.g. "ISO 20022" vs `ISO20022`), and this only
# fills in a category that has no page yet.

require 'set'

module Jekyll
  class CategoryPage < Page
    def initialize(site, base, dir, category)
      @site = site
      @base = base
      @dir  = dir
      @name = 'index.html'

      process(@name)
      read_yaml(File.join(base, '_layouts'), 'category-page.html')
      data['category'] = category
      data['title']    = category
    end
  end

  class CategoryPageGenerator < Generator
    safe true

    def generate(site)
      return unless site.layouts.key?('category-page')

      dir = site.config['category_dir'] || 'category'

      # URLs already claimed by a checked-in page, normalised without the trailing
      # slash so "/category/zkp/" and "/category/zkp" compare equal.
      taken = Set.new
      site.pages.each do |page|
        permalink = page.data['permalink']
        taken << permalink.to_s.chomp('/') unless permalink.nil?
      end

      site.categories.each_key do |category|
        category_dir = File.join(dir, Utils.slugify(category))
        next if taken.include?("/#{category_dir}")

        Jekyll.logger.info 'CategoryPage:', "generating missing page for '#{category}'"
        site.pages << CategoryPage.new(site, site.source, category_dir, category)
      end
    end
  end
end
