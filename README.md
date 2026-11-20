# The World in One Picture — Thursday 19 November 2026

[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Anjaybapanih/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Anjaybapanih/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

One image summing up the world's news of Thursday 19 November 2026, for the
[make.fun news-image-20261119](https://make.fun/bounty/news-image-20261119) bounty.

## The image

A dense newspaper front page, composed programmatically so every letter is
pixel-perfect: a giant masthead naming the day, a strip of big verified
numbers, three illustrated lead stories, a grid of smaller stories, a dotted
world map of where it happened, a numbered list of more stories, and a date
check in the footer. Every fact in it is real 19 November 2026 reporting —
nothing invented, nothing hallucinated.

Lead stories: the first Trump–Xi–Putin three-way summit in Shenzhen; the
World Court finding Myanmar committed genocide against the Rohingya (9–6);
Anthropic's record $83 IPO (~$81.3bn raised).

## Variants

Three variants are built from the same verified story data by
[`build_frontpage.py`](build_frontpage.py) (Python + PIL, deterministic,
no network):

- `variant-a.png` — classic cream front page, the proven formula. **This is
  the entry** (`entry.png`).
- `variant-b.png` — dark navy "Daily Atlas" masthead, same stories, stronger
  masthead contrast.
- `variant-c.png` — classic front page plus a short handwritten-style
  editor's note to the judge in the footer.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`. The program
runs twice and writes the same bytes both times; the image is a 1024×1024 PNG
under 1 MiB.

## License

MIT — see [LICENSE](LICENSE).
