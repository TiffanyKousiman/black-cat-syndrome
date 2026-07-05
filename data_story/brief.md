# Black Cat Syndrome — Scrollytelling Brief

## Goal

Tell a sharp, emotionally resonant data story that shows the measurable adoption penalty for black cats and connects it to cultural narratives, ending with a direct, personal call to action.

Headline: black-dog syndrome is a myth (the gap vanishes with controls); black-cat syndrome, in this data, is not.

## Audience Promise

You will feel the wait, understand the system, and see the animals behind the numbers.

## The Finding (real numbers)

- Median wait: black 23 days vs 20 for other colors — slowest of any color group.
- Adjusted +15–17% longer, controlling for age, breed, size, coat, state.
- Not age: black cats aren't older; the gap holds inside every age band.
- Pile-up: black cats are 28% of adopted but 33% of cats still waiting.
- Scale: ~19,000 cat-years of extra waiting in total.

## Scope (resolved)

- Cats only. Dogs appear only as the contrast (the debunked myth).
- Time window: adopted history 2020–2025 for the finding; adoptable snapshot for the pile-up and live gallery.

## Story Structure

- Referencing a hybrid of "Finding Forever Homes" + "Songwriters" Styles from The Pudding
- Use a strong narrative spine and a few bold visuals (Songwriters).
- Keep the analytical rigor + methods transparency (Finding Forever Homes).
- Alternate between intimate micro‑story and macro‑data to keep momentum.
- One visual, re‑posed: the same field of cats becomes the hero, the swarm, the filtered swarm, the grid, and the gallery.


## Act 1 — A Single, Lonely Journey (Hook)
Clear point: Not all paths to a forever home are the same length.
Driving question: What does the wait feel like for one overlooked cat?
Data needed:
- One real Petfinder black cat with a long wait.
- `published_at`, `status_changed_at`, photo, name, URL.

Analysis:
- Days waiting = `status_changed_at - published_at`.

Visual entry:
- Minimal white screen, a single animated black cat walking a timeline.
- Scroll advances the counter: Day 1 → Day N, with subtle seasonal cues.

## Act 2 — Quantifying the “Black Cat Tax” (Core finding)
Clear point: The longer wait time is systematic, not anecdotal.
Driving question: How many extra days do black cats wait, and where does the gap live?
Data needed:
- Adopted cats with `color_category`, `days_to_adopt`.
Analysis:
- Days to adopt per cat; Black vs Non‑Black (exclude `Unknown`).
Visual entry:
- The walking cat lands into a beeswarm — every cat an illustrated dot, placed by days waited.
- The swarm splits into two bands, Black vs Other; a bracket labels the gap.
- Show real days and “+15–17% adjusted” — a bar chart would hide the tail where the gap lives.

## Act 3 — The Ancient Roots of a Modern Bias (Why)

https://www.wikihow.com/Black-Cat-Superstition

https://www.britannica.com/topic/Why-Are-Black-Cats-Unlucky

https://www.youtube.com/watch?v=DmNR_rX1cvY

Clear point: The bias is a cultural echo with historical roots.

Driving question: Where did the association of black animals with bad luck come from?

Data needed:
- Curated, cited timeline of cultural touchpoints.
- Emphasize cultural disparity: Western bad‑luck framing vs. cultures that view black cats as good luck.
- Source anchor: Britannica’s summary of Western superstition vs. Japan’s good‑luck view.

Visual entry:
- The “Black” band shrinks into a timeline path.
- 4–5 illustrated stops with concise text and sources.
- A single “main character” black cat carries through each stop; only the background, setting, and costume shift by era.
- Most illustration-heavy act — treat era art as optional polish; data acts must stand without it.

Stops (draft):
1) Ancient Egypt: cats revered (Bastet) — positive counterpoint.
2) Japan: black cats as a good‑luck omen (e.g., luck in love for single women).
3) 1233 CE: Vox in Rama — black cats linked to Satan.
4) 1500s–1700s: witch trials, familiars, folklore.
5) 1800s–1900s: idioms and literature embed the myth.
6) Modern pop culture: Halloween imagery, guard‑dog tropes.

## Act 4 — Not Just a Breed Thing (Debunking)
Clear point: The penalty persists even within breed/age/size.

Driving question: Is this just about breed popularity or age?

Data needed:
- `breed`, `age`, `size`, `color`, `days_to_adopt`.

Analysis:
- Within‑group comparisons (e.g., black vs non‑black in same breed/age).

Visual entry:
- Filters re‑scope the same swarm; the gap won’t close. Color follows the cat, not the filter.
- Age is carried by the filter label, not by the icon (one age shown at a time).

## Act 5 — The Scale of the Wait (Systems impact)
Clear point: The aggregate cost is staggering.

Driving question: How many years are lost to waiting?

Data needed:
- Same dataset as Act 2.

Analysis:
- “Taxable days” per black cat = days_to_adopt - non‑black median.
- Sum and convert to years (~19,000 cat‑years).

Visual entry:
- A counter races upward while a grid of silhouettes fills in.

## Act 6 — Erasing the Tax (Call to action)
Clear point: The problem is systemic, but the solution is personal.

Driving question: Who is waiting right now, and how can I help?

Data needed:
- Recent adoptable black cats: photo, name, URL, `published_at`.

Analysis:
- Current days waiting = today − `published_at`.

Visual entry:
- Full‑bleed portrait gallery with names + “View profile”, longest‑waiting first.

## Visual System (icons)

- Every dot is an illustrated cat, colored like the real animal — not a plain dot.
- Match detail to size. Swarm (10–18px): only color reads, so keep to 3–4 buckets — Black vs the rest, maybe Orange and White. Black cats carry a gold rim.
- Large (48–96px): the full 8‑color cast (Black, Gray/Blue, Brown, Calico/Tortie, Orange, White/Cream, Special Patterns, Point) for the legend, lineup, and gallery.
- Age → one posture set (kitten/adult/senior) for the hero and legend only; no age × color combos.
- Not encoded: coat length, size (off‑story).
- Icons: SVG, shared baseline, theme‑switchable keyline (white on ivory, black on dark both readable). Walk cycle: side profile, loopable, 6–8 frames.
- Build: pre‑rasterize icons onto canvas for the swarm; reuse `Scrolly.svelte`; cleaned data in `src/data/`.

Style + Interaction Notes (Combined Aesthetic)
- Typography: bold display headers + crisp supporting text.
- Color: high‑contrast black/ivory with a single accent color for data.
- Motion: scroll‑driven reveals, purposeful transitions between acts.
- Visual rhythm: single idea per “scene”; avoid over‑dense steps.
- Methods: dedicated section at end, clear limitations and notes.

Open Questions
- Swarm sample size and rendering budget (how many cats before canvas is required).
- Do we show state‑level variation (map or small multiples)?
- Illustrator’s tooling → final walk‑cycle format.
