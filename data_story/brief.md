# Black Cat Syndrome — Scrollytelling Brief

> **Status:** Analysis complete; front-end not started. This is the authoritative narrative spec — read before editing story components. Numbers below are from the full dataset (Petfinder v2, ~728k adopted cats, 2020–2025); see `EDA/ANALYSIS_FINDINGS.md` for the methods and robustness checks.
>
> **Reference prototypes:** an interactive scrollytelling mockup ("every cat is a dot") and an illustration brief for the cat icons were produced during planning — use them as the visual north star for the build.

## Goal

Tell a sharp, emotionally resonant data story that shows the **measurable, robust** adoption penalty for black cats and connects it to cultural narratives, ending with a direct, personal call to action.

**The differentiated headline:** The Pudding showed *black-**dog** syndrome is a myth* — the gap vanishes once you control for age and breed. In this data, the *black-**cat** penalty is real*: it survives every control and even grows slightly. That contrast is the spine of the story — we are not repeating a myth, we are documenting a measurable one.

## Audience Promise

You will feel the wait, understand the system, and see the animals behind the numbers.

## The finding in numbers (for reference in the copy)

- **+3 median days** to adoption for black cats: **23 days vs 20** for every other colour — the **slowest of any colour group** (next slowest ~21; point colours adopt fastest at ~13).
- **+6 days on the mean** (~56 vs ~50) — the gap is larger in the long tail.
- **+15–17% longer, adjusted** for age, size, coat, breed-mix, spay/neuter, state, and list-year. The coefficient does *not* shrink with controls; adding age *increases* it.
- **Not age:** black cats are not older (near-identical age mix, if anything younger). The penalty persists inside every age band (+3 to +5 days).
- **The pile-up:** black cats are **27.8% of adopted** cats but **33.1% of cats still waiting** today — overrepresented among those left behind, independent of the days model.
- **The scale:** summing each black cat's days beyond the non-black median ≈ **19,000 cat-years** of extra waiting.

## Scope decisions (resolved)

- **Cats only.** The collected dataset and every finding above are cats. Dogs appear only as the *contrast* (the debunked myth), not as data we visualise.
- **Time window:** adopted history (2020–2025) drives the core finding (Acts 1–5); the adoptable snapshot drives the pile-up stat and the live gallery (Act 6).
- **State-level variation:** optional. If used, as a small-multiple or map aside in the methods section — not a main act.

## Story Structure

- A hybrid of "Finding Forever Homes" + "Songwriters" styles from The Pudding: a strong narrative spine with a few bold visuals (Songwriters), plus analytical rigour and methods transparency (Finding Forever Homes).
- Alternate between intimate micro-story and macro-data to keep momentum.
- **One reusable visual, re-posed across acts** (see Visual System): the same field of cats becomes the hero, the swarm, the filtered swarm, the grid, and the gallery — so the reader never loses the single cat from Act 1 as we scale to hundreds of thousands.

---

## Act 1 — A Single, Lonely Journey (Hook)
**Clear point:** Not all paths to a forever home are the same length.
**Driving question:** What does the wait feel like for one overlooked cat?

**Data:** one real Petfinder black cat with a long wait — `published_at`, `status_changed_at`, photo, name, URL. Days waiting = `status_changed_at − published_at`.

**Visual:** minimal screen, a single **animated black cat walking** a timeline (not a static dot). Scroll advances the day counter Day 1 → Day N with subtle seasonal cues. This is the one moment that needs a hand-animated walk cycle (side profile, loopable); the black hero carries a gold highlight rim that also marks black cats in the swarm to come.

## Act 2 — Quantifying the "Black Cat Tax" (Core finding)
**Clear point:** The longer wait is systematic, not anecdotal.
**Driving question:** How many extra days do black cats wait — and where does the gap actually live?

**Data:** adopted cats with `color_category`, `days_to_adopt`. Group Black vs every other known colour (exclude `Unknown`).

**Visual (revised — beeswarm, not a bar chart):** the walking cat lands into a **beeswarm where every cat is an illustrated dot**, placed left→right by `days_to_adopt`. The swarm then splits into two bands — Black vs the rest — with median ticks and a bracket labelling the gap. A bar chart hides the story: the median gap is modest (+3d); the drama is the **right-skewed tail** and the black cats piling up in it. Show the real-day magnitude *and* the "+15–17% adjusted" figure so the modest median reads as honest, not weak.

*Corroborating beat:* a paired bar — "who gets adopted" (27.8% black) vs "who's still waiting" (33.1% black) — the model-independent pile-up.

## Act 3 — The Ancient Roots of a Modern Bias (Why)
**Clear point:** The bias is a cultural echo with historical roots — and a *Western* one.
**Driving question:** Where did the association of black animals with bad luck come from?

Sources: [Britannica — Why Are Black Cats Unlucky](https://www.britannica.com/topic/Why-Are-Black-Cats-Unlucky) · [wikiHow — Black Cat Superstition](https://www.wikihow.com/Black-Cat-Superstition) · [video](https://www.youtube.com/watch?v=DmNR_rX1cvY)

**Data:** curated, cited timeline. Emphasise the cultural disparity — Western bad-luck framing vs. cultures (Japan, ancient Egypt) that read black cats as good luck.

**Visual:** the "Black" band flows into a timeline path. 4–5 illustrated stops; a single "main character" black cat carries through each — only background, setting, and costume shift by era. Consider a good-luck ↔ bad-luck divergence axis (cultures above/below a line) to make "the curse is a Western construction" visible.

Stops (draft):
1) Ancient Egypt: cats revered (Bastet) — positive counterpoint.
2) Japan: black cats as a good-luck omen (luck in love for single women).
3) 1233 CE: *Vox in Rama* — black cats linked to Satan.
4) 1500s–1700s: witch trials, familiars, folklore.
5) 1800s–1900s: idioms and literature embed the myth.
6) Modern pop culture: Halloween imagery, guard-dog tropes.

> **Illustration load:** this act needs the most custom art. De-risk it — it's the likeliest place for the build to stall. Treat the era illustrations as optional polish; the data acts must stand without them.

## Act 4 — Not Just a Breed or Age Thing (Debunking)
**Clear point:** The penalty persists inside breed, age, and size.
**Driving question:** Is this just breed popularity or age?

**Data:** `age`, `size`, `coat`, `breeds_mixed`, `color_category`, `days_to_adopt`. Within-group comparisons (black vs non-black in the same band).

**Visual (revised — re-filter the same swarm):** reuse the Act 2 beeswarm; interactive filters (age → size → breed-mix) **re-scope the same dots** and the gap refuses to close. Because the story shows *one band at a time*, age is carried by the filter label, not by the cat icon. Colour must follow the cat, never the filter — survivors don't repaint. Optionally, small-multiple panels (Baby/Young/Adult/Senior) each showing the split, to make "it never goes away" land without clicking.

## Act 5 — The Scale of the Wait (Systems impact)
**Clear point:** The aggregate cost is staggering.
**Driving question:** How many years are lost to waiting?

**Data:** same as Act 2. "Taxable days" per black cat = `days_to_adopt − non-black median`; sum and convert to years (**≈ 19,000 cat-years**).

**Visual:** the dots pack into a grid/waffle that fills as a counter races upward — each cell a block of cat-days, making the abstract number physical.

## Act 6 — Erasing the Tax (Call to action)
**Clear point:** The problem is systemic, but the solution is personal.
**Driving question:** Who is waiting right now, and how can I help?

**Data:** recent **adoptable** black cats — photo, name, URL, `published_at`. Current wait = today − `published_at`.

**Visual:** the dots resolve into a full-bleed **portrait gallery** — real Petfinder photos, names, and "View profile", sorted longest-waiting first.

---

## Visual System

**One component, re-posed.** Every act is the same field of illustrated cats in a new arrangement: hero (n=1, walking) → beeswarm → filtered beeswarm → grid → gallery. Build the "cat dot" once and reuse it — this is the whole engineering plan.

**Cats are illustrated icons, coloured like the real animal** — not generic dots. The primary encoding is the cat's coat colour/pattern.

**The legibility rule (drives the whole icon set):** match detail to display size.
- **Swarm scale (10–18 px):** the reader sees only overall colour/lightness — patterns (calico, tabby, point) blur to a muddy medium; white vanishes on ivory. So the dense swarm carries only **3–4 readable buckets** — keep it **Black vs the rest**, optionally pulling out Orange and White/Cream. Black cats get a gold highlight rim (also the "subject" marker + the secondary encoding that keeps identity off colour alone).
- **Large scale (48–96 px):** the **full 8-colour cast** (Black, Gray/Blue/Silver, Brown/Chocolate, Calico/Tortie, Orange/Red, White/Cream, Special Patterns, Point Colors) earns its keep — legend, "meet the colours" lineup, hover cards, gallery.
- **Age** → one posture set (kitten / adult / senior) for the hero and legend only. Do **not** commission age × colour combinations; they never read small and the story shows one age at a time.
- **Not encoded:** coat length and size (off-story; ~85% short-coat, mostly medium).

**Icon delivery spec** (for the illustrator): SVG, square `viewBox 0 0 100 100`, feet on a shared baseline, identical bounding box and weight across colours; flat, 2–3 colours + a theme-switchable keyline (dark on ivory, light on near-black) so white-on-ivory and black-on-dark both read; patterns baked into finished files. Walk cycle: side profile, loopable, 6–8 frames — final format (SVG frames / sprite sheet / Lottie) depends on the illustrator's tools.

**Build note:** render the swarm as pre-rasterised icon images on canvas — hundreds of live SVG nodes will stutter. Reuse `Scrolly.svelte`; cleaned browser-facing data (a stratified sample for the swarm + summary stats + the Act 1 / Act 6 real cats) goes in `src/data/`.

## Style + Interaction Notes

- **Typography:** heavy sans display headers + a serif for reading body (an editorial inversion of the usual pairing).
- **Colour:** high-contrast ivory / near-black with a single **gold** accent for data and annotation (the gold also nods to Act 3's maneki-neko good-luck framing). Design both light and dark themes.
- **Motion:** scroll-driven reveals; purposeful transitions between acts (dots lerp to new targets, not hard cuts). Respect `prefers-reduced-motion`.
- **Rhythm:** one idea per scene; avoid over-dense steps.
- **Methods:** dedicated section at the end — the regression table, the survivorship caveat (`days_to_adopt` exists only for adopted cats, so the penalty is likely *understated*), the `photo_count` collider caveat, and the `days_to_adopt == 0` spike (an `Unknown`-color artifact, excluded).

## Open Questions (remaining)

- Exact swarm sample size and rendering budget (how many illustrated cats on screen before canvas is required).
- Whether to show state-level variation at all, and if so where (methods aside vs. a cut act).
- Illustrator's tooling → final walk-cycle format.
