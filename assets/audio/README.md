# Background music

Nine tracks. The filename must match exactly — the page derives the URL from
the chapter id, so a rename breaks that chapter silently.

| file                       | plays during                                   |
|----------------------------|------------------------------------------------|
| `hero.mp3`                 | the opening "Here's a story" **and** the closing countdown |
| `2021-college.mp3`         | Where it started                                |
| `2022-two-cities.mp3`      | Two cities                                      |
| `2023-she-said-yes.mp3`    | She said yes                                    |
| `2024-long-way.mp3`        | The long way round                              |
| `2025-coming-home.mp3`     | Coming home                                     |
| `2026-yes.mp3`             | Both families said yes                          |
| `2026-engagement.mp3`      | The engagement                                  |
| `2026-reception.mp3`       | The reception (the empty frame)                 |

`hero.mp3` is used twice on purpose — the story opens and closes on the same
theme.

## How to cut them

**Length** — 30 to 45 seconds. Shorter loops start to feel repetitive while
someone reads a chapter; longer ones cost download for a part most guests
never reach.

**Cut on a bar line, and do not fade the file itself.** The page fades every
track in and out as you scroll, so a fade baked into the MP3 fades twice at
the start and then dips in the middle of every loop. Start the clip exactly on
a downbeat and end it exactly one bar before the same downbeat returns, so the
end runs straight back into the start with no gap and no click.

**Format** — MP3, **mono**, **96 kbps**, 44.1 kHz.

Mono is the important one. This is ambient music playing under a story, nobody
is listening in stereo, and it halves the file. At 96 kbps mono a 40-second
clip is about 480 KB; nine of those is roughly 4.3 MB.

For comparison the whole page is currently 2.1 MB, so the music would be twice
the weight of everything else combined. That is why the page only downloads a
track when its chapter is close — a guest who reads two chapters and leaves
never pays for the other seven.

If you want it lighter, 64 kbps mono is about 320 KB per track (~2.9 MB total)
and for soft instrumental beds the difference is very hard to hear on a phone.

Converting, once you have the cuts:

```
ffmpeg -i in.wav -ac 1 -b:a 96k -ar 44100 2021-college.mp3
```

## Keep the levels even

Master all nine to roughly the same loudness — around **-18 LUFS** — so the
crossfades don't jump. If one track is mastered louder than its neighbour, the
handover between chapters sounds like a mistake rather than a transition.

You can check and correct with:

```
ffmpeg -i 2021-college.mp3 -af loudnorm=I=-18:TP=-1.5:LRA=11 -ac 1 -b:a 96k out.mp3
```
