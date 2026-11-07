# Up Top Studios: website redesign

Static, dependency-free site. It needs nothing beyond Python 3 to build.

- `src/pages/*.html`: page content (edit copy here)
- `src/assets/`: CSS, JS, optimised WebP images
- `build.py`: layout, SEO meta, JSON-LD schema, sitemap

```sh
python3 build.py          # preview build -> docs/ (noindex; served by GitHub Pages)
python3 build.py --prod   # production build -> dist/ (indexable, upload to live host)
```

The preview is deliberately `noindex` so it can't compete with uptopstudios.co.uk in Google.
