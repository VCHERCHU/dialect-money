# Dialect Money — Problem Statement

*Product Thinking, Institute of Digital Government*

---

## The statement

> A 72-year-old Singaporean who speaks only Hokkien cannot tell whether the
> insurance rider, fixed-deposit promo or investment pitch in front of her is
> worth her money. Every trustworthy explanation — CPF, MAS, MoneySense — exists
> as English text on a website she will never read. So she nods along to the
> salesperson, or waits for a child to visit and decide for her.
>
> **How might we turn authoritative money guidance into spoken dialect she can
> understand on her own terms, and get it to her without asking her to use a
> website?**

Short form:

> **Dialect-only seniors are locked out of financial guidance that already
> exists — not because it is missing, but because it is written, in English, for
> someone else.**

---

## Who this is for

**Mdm Tan, 72.** Speaks Hokkien at home and with her friends at the coffee shop.
Understands some Mandarin on TV, reads almost no English. Retired; lives on CPF
LIFE payouts and savings. Owns a smartphone her daughter set up — she uses
WhatsApp voice notes and answers video calls, and does not browse, search or
install anything.

She is not the person who visits a website. She is the person a website has to
reach.

**Secondary users** — the people who actually operate anything digital on her
behalf: her adult daughter, a Silver Generation Office or CC volunteer, a
befriender. Any distribution plan runs through one of them.

**Dialects in scope for v1:** Hokkien, Teochew, Cantonese.

---

## The problem

The information is not missing. CPF, MAS, MoneySense, IRAS and MOF publish clear,
accurate, free guidance on exactly the questions Mdm Tan has. All of it is
**text**, nearly all of it in **English**, on **websites** designed for someone
who searches, reads and scrolls.

For Mdm Tan this is functionally identical to the information not existing.

The consequence is not confusion — it is **delegation**. Every money question
waits for someone else: a child who visits on Sunday, a relative with an opinion,
or the person selling her the product, who is the only one in the room who will
explain it in dialect. She has no independent way to check what she is being
told, so she nods.

Two specific failures follow:

1. **She misses what she is entitled to.** Schemes, top-ups and payouts pass by
   because the announcement never reached her in a form she could use.
2. **She cannot evaluate what is offered to her.** The only explanation she gets
   is the sales pitch.

---

## What success looks like

Not "she becomes financially literate." The realistic, valuable outcome is
narrower and more human:

> **She has enough understanding to ask a real question** — of the insurance
> agent, the bank teller, the CPF officer, or her own daughter — instead of
> nodding along.

That is the bar. She does not need to decide alone; she needs to stop being
excluded from the decision.

---

## Scope: what v1 does

**The wedge:** *"Is this worth my money?"* — the moment something is being sold
to her. Insurance riders, integrated shield plans, fixed-deposit promos, gold and
investment pitches.

**The form:** a website that **auto-publishes** short dialect video explainers on
a schedule. Nobody clicks "generate". The site crawls whitelisted sources,
drafts a script, produces AI dialect narration, and publishes to a browsable
library. Seniors or the people helping them watch or are sent a link.

**The guardrail:** the crawler reads **whitelisted sources only** — CPF, MAS,
MoneySense, IRAS, MOF, gov.sg. Never the open web. Every video cites and links
the page it came from.

---

## The tension at the centre of this product

The wedge and the guardrail pull against each other, and naming it honestly is
more useful than papering over it:

- *"Is this worth my money?"* is a question about **specific commercial offers** —
  this insurer's rider, that bank's promo rate.
- **Whitelisted government sources never mention specific commercial products.**
  MoneySense will explain how an integrated shield plan works. It will never tell
  you whether the one on the table is a good deal.

**Resolution:** v1 explains, it does not advise.

> *"Help me understand what is being sold to me"* — not *"tell me if this is a
> good deal."*

This is a deliberate choice, not a limitation discovered late. It is also
sufficient: understanding what a rider actually is, is precisely what lets Mdm
Tan ask the agent a question he has to answer. That is the stated outcome.

**Explicitly out of scope for v1:** product recommendations, personalised advice,
scam detection, and any figure not traceable to a whitelisted page.

---

## Assumptions, ranked by how badly they hurt if wrong

### 1. Distribution — the riskiest assumption in the product

Auto-publishing removes the generation UI. It does not remove the reach problem.
Someone still has to put a link in front of a senior who does not browse.

If no channel exists — a daughter, a volunteer, a CC screen, a WhatsApp group —
nothing else in this document matters. Every other assumption is downstream of
this one.

*How to test:* IMDA Digital Society Report data on senior smartphone and internet
use; then a real attempt to send one video to one senior through one person.

### 2. Dialect TTS is intelligible enough to be trusted

Hokkien and Teochew text-to-speech is markedly weaker than Cantonese. If the
voice is hard to follow — or obviously synthetic — the risk is not just
disengagement but **distrust**, which is fatal for financial content.

*How to test:* generate one sample in each dialect and play it to native
speakers. Do this before building anything.

### 3. Video is the right format

Video implies visuals that a low-literacy viewer may not need or use. Audio-first
with a static frame may perform as well at a fraction of the cost and complexity.

*How to test:* compare an audio-only and a video version of the same explainer
with the same listeners.

### 4. "Updated" is a real need

The word *updated* implies rapid change. In practice, MoneySense guidance on how
products work is fairly stable; it is Budget announcements and rates that move. A
continuous crawl may be solving a problem that is not there.

*How to test:* diff a handful of whitelisted pages over several weeks and see
what actually changes.

---

## Validation plan

Access to users is currently **secondary research only**. That is a stated
constraint, not a hidden one — every claim below is either sourced or marked
unvalidated.

**Secondary sources to draw on:**

| Source | What it establishes |
| --- | --- |
| SingStat / Census of Population | Literacy and language-most-frequently-spoken by age band — the real size of "dialect-only, 70+" |
| IMDA Digital Society Report | Smartphone and internet use among seniors — tests assumption 1 directly |
| MoneySense / MAS financial literacy surveys | Self-reported confidence in financial decisions by age |
| CPF / MOF published take-up figures | Evidence that eligible seniors miss what they are entitled to |

**The cheapest test that beats all of it:** generate **one** two-minute Hokkien
explainer from a single MoneySense page, using whatever TTS is reachable today.
Play it to two or three seniors — relatives, neighbours. Ask exactly two things:

1. Can you follow it?
2. Would you let your daughter send you another one?

That single artefact tests distribution, voice quality and format at once, costs
an afternoon, and converts "secondary research only" into real evidence without
needing an organisation to let you in.

---

## Measuring the outcome

The stated outcome — *confident enough to ask* — is not directly instrumentable.
Proxies, in order of honesty:

- **Leading:** completion rate of a video (did she watch to the end?), and
  forward rate (did the helper send another one?).
- **Lagging:** self-reported — "did you ask anyone a question about money this
  month?" — gathered in the few conversations available.
- **Counter-metric:** percentage of published videos whose every factual claim
  traces to a cited whitelisted page. This must be 100%. A single confidently
  narrated wrong figure in Hokkien does more damage than the product does good.

---

## Open questions

- Which single channel carries the first video to a real senior?
- Is there a usable Hokkien and Teochew TTS voice today, or is human recording
  the only credible route for v1?
- Should the library be organised by question ("what is a rider?") rather than by
  source or date?
- Does explaining without advising still feel useful to a senior, or does it read
  as evasive?
