# Waiting for the Moon｜小兔子等月亮 — V1 pilot script

**Audience:** roughly ages 4–7, with a parent or caregiver. **Purpose:** a
gentle bedtime read-aloud, not a timed video edit. The English narration is
the spoken source; Chinese is a meaning-matched subtitle translation. The
cover title is separate from the body. The seven story pages contain 91
English words (counted from `story.json` by the contract test). No page
seconds or total running time are assigned before an approved voice recording.
The 50–70-second range is a planning suggestion only.

## Story and emotion structure

- **Cause / expectation:** Rabbit climbs the hill hoping to see the moon.
- **Development:** Dusk comes; the moon is absent, then a cloud hides it.
- **Low point:** Rabbit's ears droop and it feels lonely.
- **Turn:** Stars appear and keep the rabbit company; it can wait calmly.
- **Resolution:** Cloud moves, moon appears; rabbit feels safe and sleeps.

The emotion moves **hope → uncertainty → small sadness → companionship →
patience → relief → rest**. The stars cause a change in how the rabbit feels;
they are not idle sparkle filler. The moon reveal answers the opening hope.

| Page | English read-aloud | Chinese subtitle | Direction and visible event |
| --- | --- | --- | --- |
| 00 | Waiting for the Moon. | 小兔子等月亮。 | Optional quiet title, no forced narration slot. Cover: rabbit on hill at dusk. |
| 01 | One evening, a little rabbit climbed a hill to see the moon. | 一天傍晚，小兔子爬上山坡，想看看月亮。 | Warm invitation. Rabbit arrives and settles, looking skyward. |
| 02 | The sky turned dark, but the moon did not come. The rabbit waited. | 天色渐渐暗了，月亮却没有出现。小兔子继续等着。 | A small pause after “dark”; curiosity becomes uncertainty. Sky changes, moon absent. |
| 03 | A cloud hid the moon. The rabbit's ears drooped. It felt lonely. | 云朵挡住了月亮。小兔子的耳朵垂下来，心里有点孤单。 | Gently lower energy on “lonely”; no melodrama. Cloud masks moon, ears drop. |
| 04 | One small star blinked. Another followed. Soon, the stars kept the rabbit company. | 一颗小星星亮了，又亮起一颗。很快，星星们陪着小兔子。 | Separate the two star arrivals with a natural pause. Stars appear in sequence; rabbit notices. |
| 05 | The rabbit smiled. It took a slow breath and waited with its new friends. | 小兔子笑了，慢慢吸了一口气，和新朋友们一起等。 | Breath is part of delivery, never inserted mechanically. Rabbit relaxes and smiles. |
| 06 | At last, the cloud drifted away. The round moon lit the hill softly. | 终于，云朵飘走了。圆圆的月亮柔柔地照亮山坡。 | Gentle relief at “At last,” then soften. Cloud clears; moon is revealed, no camera push. |
| 07 | “Good night, Moon,” whispered the rabbit. It curled up, feeling safe, and fell asleep. | “晚安，月亮。”小兔子轻声说着，安心地蜷起来睡着了。 | “Good night” almost whispered, last sentence settles. Rabbit curls up; hold the sleeping pose naturally. |

## Read-Aloud Director's audition brief

Try the previously selected natural English female voice first, but audition
the *new* script before accepting it. Record at least two raw, unprocessed
short selections spanning the sad turn and the comforting ending. Listen for
pronunciation of “drooped,” “drifted,” “whispered,” natural sentence pauses,
smooth emotion and no clipped final word. Save engine, voice ID, model source,
license, settings, WAV hashes and named listening notes. Then record all
lines at natural speed. The Storyboard Director measures those approved WAVs
and only then assigns page holds and turns. Do not stretch the former R4
33.333-second timeline to fit these new sentences.

## Pilot state

Story and reading drafts are ready for review. No new narration has been
generated or heard, no measured time windows exist, and no new animation or
video is authorized by this draft alone. The machine-readable
[`acceptance.json`](acceptance.json) leaves `READ_ALOUD_PASS=BLOCKED`.
