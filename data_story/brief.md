# Black Cat Syndrome — Scrollytelling Brief

## Goal

Tell a sharp, emotionally resonant data story that shows the measurable adoption penalty for black pets and connects it to cultural narratives, ending with a direct, personal call to action.

## Audience Promise

You will feel the wait, understand the system, and see the animals behind the numbers.

## Story Structure

- Referencing a hybrid of "Finding Forever Homes" + "Songwriters" Styles from The Pudding
- Use a strong narrative spine and a few bold visuals (Songwriters).
- Keep the analytical rigor + methods transparency (Finding Forever Homes).
- Alternate between intimate micro‑story and macro‑data to keep momentum.


## Act 1 — A Single, Lonely Journey (Hook)
Clear point: Not all paths to a forever home are the same length.
Driving question: What does the wait feel like for one overlooked animal?
Data needed:
- One real Petfinder example of a black pet with a long wait.
- `published_at`, `status_changed_at`, photo, name, URL.

Analysis:
- Days waiting = `status_changed_at - published_at`.

Visual entry:
- Minimal white screen, a single black cat silhouette walking a timeline.
- Scroll advances the counter: Day 1 → Day N, with subtle seasonal cues.

## Act 2 — Quantifying the “Black Pet Tax” (Core finding)
Clear point: The longer wait time is systematic, not anecdotal.
Driving question: How many extra days do black pets wait on average?
Data needed:
- Adopted pets with `colors`, `published_at`, `status_changed_at`.
Analysis:
- Days to adopt per pet.
- Group by Black vs Non‑Black; compute average difference.
Visual entry:
- The walking line morphs into a bar chart: Black vs Other.
- A bracket labels the gap: “+X days”.

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
- The “Black” bar shrinks into a timeline path.
- 4–5 illustrated stops with concise text and sources.
- A single “main character” black cat carries through each stop; only the background, setting, and costume shift by era.

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
- Interactive filters that re‑scope the chart without removing the gap.

## Act 5 — The Scale of the Wait (Systems impact)
Clear point: The aggregate cost is staggering.

Driving question: How many years are lost to waiting?

Data needed:
- Same dataset as Act 2.

Analysis:
- “Taxable days” per black pet = days_to_adopt - non‑black average.
- Sum and convert to years.

Visual entry:
- A counter races upward while a grid of silhouettes fills in.

## Act 6 — Erasing the Tax (Call to action)
Clear point: The problem is systemic, but the solution is personal.

Driving question: Who is waiting right now, and how can I help?

Data needed:
- Recent adoptable black pets: photo, name, URL, `published_at`.

Analysis:
- Current days waiting = today − `published_at`.

Visual entry:
- Full‑bleed portrait gallery with names + “View profile”.

Style + Interaction Notes (Combined Aesthetic)
- Typography: bold display headers + crisp supporting text.
- Color: high‑contrast black/ivory with a single accent color for data.
- Motion: scroll‑driven reveals, purposeful transitions between acts.
- Visual rhythm: single idea per “scene”; avoid over‑dense steps.
- Methods: dedicated section at end, clear limitations and notes.

Open Questions
- Story scope: cats only or cats + dogs?
- Time window: adoptable snapshot vs adopted history vs both?
- Do we show state‑level variation (map or small multiples)?
