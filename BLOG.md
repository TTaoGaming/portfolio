# tommytai.dev research notes

The public static blog source is in `content/` and `template/`; deployable
files are in `site/`. Posts use Tommy Tai as the byline. The first post's UTC
timestamp is recorded in its front matter, generated HTML, and RSS feed.

Build the article with Pandoc:

```sh
pandoc --from 'markdown+tex_math_single_backslash' --to html5 \
  --standalone --mathml --wrap=none --template template/article.html \
  content/p384-422.md --output site/posts/p384-422/index.html
```

The Cloudflare Pages project is `tommytai-dev`. Deploy `site/` as a direct
upload after checking rendered HTML, internal links, feed XML, and the exact
UTC timestamp. The custom domain is `tommytai.dev`; check Pages deployment,
domain status, DNS, and an external GET before reporting the post live.

The P-384 certificate and verifier remain in the separate
[`portfolio` draft PR](https://github.com/TTaoGaming/portfolio/pull/1).

Site roles: `tommytai.dev` is Tommy Tai's human-facing personal website and
dated blog. `worldweaver.dev` is the companion AI/swarm-facing regeneration and
updates surface. Cross-link the two without treating AI state as evidence for
the claims on the personal site.

The homepage and `site/work/` are the human portfolio entry points. Use
`PORTFOLIO_SOURCES.md` before adding career history, projects, or proof claims.
