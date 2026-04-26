# Mes que un AI

> *"Més que un club"* — more than a club. This is more than a language app.

---

## Overview

**Mes que un AI** is a Spanish learning project built around one core conviction: you don't learn a language by memorizing it — you *absorb* it. No grammar tables. No flashcard drills. No conjugation charts stared at until your eyes blur.

Instead, this project is built on the principle of **Comprehensible Input** — the idea that language acquisition happens naturally when you encounter real language in context you mostly understand, on topics you actually care about. For this project, that means Spanish as it lives in the world of soccer: match commentary, transfer rumors, player interviews, post-game reactions, social media, and the culture around clubs like FC Barcelona.

The goal isn't fluency by Friday. It's building a Spanish-absorbing lifestyle — one where the language shows up in things you'd be reading and listening to anyway, and over time, you just... know it.

This document is the foundation. Everything built on top of it — tools, features, pipelines — serves this philosophy.

---

## What is Comprehensible Input?

Comprehensible Input is a theory of language acquisition developed by linguist Stephen Krashen in the 1980s. The central claim is simple but radical: **we acquire language when we understand messages, not when we study rules.**

Krashen's shorthand for this is **i+1** — you need input that is slightly above your current level (*i*), but not so far above that meaning breaks down. That gap is where acquisition happens. You understand most of it, context fills the rest, and the new language quietly wires itself in.

The key distinction Krashen draws is between **acquisition** (subconscious, natural, like a child picking up their first language) and **learning** (conscious study of rules and forms). His argument — backed by decades of research and a lot of debate — is that only acquisition produces real, fluent, automatic language use. Learned rules can help at the margins, but they don't become fluent speech or reading on their own.

The practical implications are significant:

- **Meaning over form.** You should be focused on what is being communicated, not how it's being said grammatically. When you're genuinely trying to understand a message, grammar is absorbed as a byproduct.
- **Low anxiety, high engagement.** Krashen talks about the "affective filter" — stress, boredom, and self-consciousness block input from sticking. You need to be engaged, relaxed, and genuinely curious about the content.
- **Massive quantities.** There's no shortcut. Hours of real exposure to real language is what moves the needle. The input has to be comprehensible, but it also has to be abundant.
- **Output comes later.** Speaking and writing are the result of acquisition, not the engine of it. You can't force fluency by speaking before you've absorbed enough — you'll just be producing noise and reinforcing errors.

### How it has already worked — personally

The honest truth is that the most Spanish I've ever internalized didn't come from a class or an app. It came from being deeply invested in La Liga.

Years of following FC Barcelona on Twitter, reading match reactions, seeing the same phrases repeat across different contexts — *"Golazo de Pedri"*, *"partido intenso"*, *"el mejor del mundo"* — and gradually, without sitting down to study anything, a vocabulary started to form. Not from a list. From repetition in context, in moments of genuine engagement.

Music worked the same way. A lyric lands emotionally, you want to know what it means, you look it up, and that word or phrase sticks in a way that no flashcard would have produced. The emotion is the glue.

Soccer Twitter specifically is a near-perfect natural i+1 environment: short sentences, visual context (a clip, a photo, a scoreline), high-frequency football vocabulary that repeats constantly, and — crucially — it's content worth caring about. No one is reading transfer gossip ironically. The engagement is real, and real engagement is what the affective filter theory says makes input stick.

This project exists to systematize what has already been working, build tools around it, and extend it — while keeping the thing that makes it work in the first place: genuine interest.

---

## Techniques Worth Building On

These are three approaches from the broader language acquisition world that align tightly with how this project is built. They're not gimmicks — they all have research backing and are used by serious learners. The question for each is: how does it show up specifically in a soccer-content context?

---

### 1. Sentence Mining + Spaced Repetition

**What it is:** Instead of drilling vocabulary from a list, you pull real sentences from content you're already consuming — a match report, a tweet, a headline — and when something is unfamiliar, you save that sentence as a flashcard. The word gets reviewed in its original context, not in isolation. Spaced repetition software (Anki is the standard) then resurfaces it at optimal intervals based on how well you remembered it last time.

**Why it works:** The brain consolidates memory through effortful retrieval at spaced intervals, not through massed repetition. A word encountered 10 times across 10 different real sentences over 10 days sticks far better than 10 repetitions in one sitting. Context matters too — a sentence that carries actual meaning encodes more richly than a bare translation pair.

**In this project:** Every piece of content — article, tweet, clip — should have a "save this phrase" action. When you tap a sentence you don't fully know, it gets added to your personal deck with the full context intact: source, date, the player or match it was about. The emotional connection to the original moment is part of why it sticks. Anki export is also worth supporting for users who already have a review workflow.

**The soccer advantage:** High-frequency football vocabulary (*remate, despejar, fuera de juego, en propia puerta*) repeats constantly across sources. You don't need to mine every sentence — the language comes to you through volume.

---

### 2. Narrow Reading

**What it is:** Deliberately restricting your reading to a single domain — in this case, soccer — rather than consuming unrelated mixed content. The research finding is that reading multiple texts on the same topic dramatically increases how often you encounter the same words in different contexts, which is what drives vocabulary acquisition.

**Why it works:** Narrow reading produces far more high-frequency word recycling than unrelated texts. When you read five match reports about the same game from different journalists, you're not just getting more input — you're getting the same concepts expressed in different ways, which forces your brain to extract meaning from pattern rather than memorizing a single phrasing. This is exactly how native-language vocabulary deepens.

**In this project:** The entire content strategy is narrow reading by design. Every source — Marca, AS, Sport, Mundo Deportivo — covers the same matches from different angles. A Barça win generates 6 different articles using the same core vocabulary but with different sentence structures, quotes, and emphasis. That repetition-with-variation is the engine. The app should lean into this deliberately: show content about the same event from multiple sources and make it easy to move between them.

**The soccer advantage:** The domain is inherently narrow and naturally recurring. Transfer windows, matchday previews, match reports, post-game reactions — the same vocabulary keeps surfacing week after week across the season.

---

### 3. TPRS-Style Micro-Narratives

**What it is:** TPRS (Teaching Proficiency through Reading and Storytelling) is a classroom method where a teacher first tells a simple story using new vocabulary in present tense, checks comprehension, then presents the same events as a reading. The learner encounters the new language in narrative context first — where stakes and plot create genuine engagement — then in real text.

**Why it works:** Stories activate far more of the brain than isolated facts do. Language that arrives with narrative context — characters, tension, resolution — encodes through emotion and motor imagination, not just verbal processing. Crucially, hearing the simple version first makes the more complex real text comprehensible (i+1 in practice).

**In this project:** A natural adaptation: for any significant match event, generate a simplified Spanish micro-narrative first (*"Hoy, el Barcelona jugaba contra el Madrid. Lewandowski tenía el balón cerca del área. Disparó. ¡Gol!"*) before surfacing the actual Marca match report. The learner arrives at the real article already knowing what happened — which is exactly the context that makes it comprehensible. The app doesn't need to teach grammar to do this. It just needs to scaffold the entry point.

---

## Content Sources

### Spanish Sports Sites

All six major Spanish sports publications provide RSS feeds — the clean, ToS-compliant way to pull article headlines, summaries, and links programmatically. No scraping required for the feed layer.

| Publication | Focus | RSS |
|---|---|---|
| Marca | Nationwide, Real Madrid lean | `e00-marca.uecdn.es/rss/` (60+ category feeds) |
| AS | Nationwide, Madrid/Atleti lean | Available, pattern TBC |
| Sport | Catalan, Barça-focused | Available |
| Mundo Deportivo | Catalan, Barça-focused | `mundodeportivo.com/feed/rss/` |
| La Vanguardia | Catalan broadsheet, sports desk | `lavanguardia.com/rss/deporte` |
| El País Deportes | National broadsheet, sports desk | `feeds.elpais.com` |

**Implementation:** `feedparser` in Python handles all of these with minimal code. RSS gives you title, summary, publication time, and a link to the full article. Full article text requires fetching the page, which is where bot detection may come into play — but for the MVP, headlines and summaries from RSS alone are a rich input source (short, punchy, high-frequency vocabulary).

**Fallback aggregator:** NewsData.io offers 200 free credits/day and indexes Spanish-language sports news across sources. Useful as a supplement or for discovery beyond the six core sites.

---

### Twitter / X

The straightforward answer: **the free tier is gone.** As of early 2026, X discontinued free API access for new developers. Reading tweets from a user's timeline was never available on the free tier anyway.

Current options:

- **Pay-per-use:** $0.005 per tweet read. For pulling 10–20 tweets from a handful of accounts a few times a day, the monthly cost would be roughly $20–60. Technically viable but a real cost for a personal project.
- **Basic tier:** $200/month — clearly not worth it at this scale.

**Practical stance for now:** Twitter/X is expensive for what it offers at this scale. The organic use case — following accounts yourself, reading tweets in the app, absorbing the language naturally — should continue exactly as it has. The project doesn't need to replicate your timeline programmatically to deliver value.

If Twitter content is ever worth pulling into the app, the two realistic paths are: pay-per-use API with careful rate limiting, or explore third-party data providers that resell X data at lower cost. Neither is a priority until the core RSS pipeline is proven.

---

## The Three Domains

Language ability isn't one thing. It splits into at least three distinct skills that develop at different rates and require different kinds of input. For this project, they're ordered by accessibility — not importance:

**Reading/Writing → Listening → Speaking**

Reading is the easiest entry point because you control the pace. You can pause, re-read, look something up. Listening is harder because the signal is fast and disappears. Speaking is the hardest because it requires everything the other two require, plus real-time production under social pressure.

The important caveat from acquisition science: these skills are not cleanly separable, and they don't develop independently. Reading builds vocabulary that makes listening easier. Listening builds phonological patterns that make speaking more natural. None of it is wasted — but the balance matters. If the app only feeds one domain, the others stagnate.

### Reading / Writing

This is where the project starts strongest. RSS feeds, article headlines, match reports, tweet text — all of it is reading input. Writing is the productive counterpart: composing match reactions, responding to prompts, even just translating a headline into your own words.

What to build toward:
- Graded article reading (difficulty filtering on RSS content)
- Inline lookups with sentence context saved, not just word definitions
- Short writing prompts tied to real match events (*"Describe last night's goal in two sentences"*)
- The micro-narrative scaffold from TPRS — read the simple version, then the real article

### Listening

This is the gap most text-heavy apps leave. Reading Spanish builds a reading-Spanish brain; it doesn't automatically translate to understanding spoken Spanish, which sounds nothing like its written form at full conversational speed.

What to build toward:
- Audio clips from commentators, post-match pressers, player interviews tied to content already in the feed
- High-variability exposure — different commentators, regions (Castilian vs. Latin American), emotional registers (calm analysis vs. goal celebration chaos)
- Listen-first mode: audio plays before the transcript appears, forcing the ear to do the work
- Gradual transcript reveal — listen once cold, then with highlighted key phrases, then with full text

The soccer domain is ideal here because the emotional stakes make repetitive listening feel natural. You'd rewatch a great goal 10 times anyway. Each rewatch with attention on the commentary is listening practice.

### Speaking

The hardest domain, and the one this project deliberately deprioritizes in early stages — not because it doesn't matter, but because acquisition science is clear: premature speaking before sufficient input is absorbed produces anxiety and reinforces errors. The input has to come first.

That said, speaking shouldn't be absent. The goal is to introduce it at the right time and in the right form — low-stakes, repetition-based, tied to content you already know.

What to build toward:
- Shadowing: listen to a short clip, then repeat it back. Not translation, not production — mimicry. Used by polyglots to wire pronunciation before speaking freely.
- Prompted reactions: after reading/watching a match event, a simple spoken prompt in Spanish (*"¿Quién fue el mejor jugador?"*) with no wrong answer, no grading
- Match commentary imitation: pick a goal clip, mute the commentator, try to call it yourself. Ridiculous, effective, and genuinely fun if you care about the sport.

### Keeping the Balance

The risk with a text-first, RSS-driven app is that it becomes a reading app and nothing else. Every feature decision should be checked against all three domains:

| Feature | Reading | Listening | Speaking |
|---|:---:|:---:|:---:|
| RSS article feed | ✓ | | |
| Article + audio clip pairing | ✓ | ✓ | |
| Listen-first mode | | ✓ | |
| Sentence mining / SRS | ✓ | ✓ (with audio) | |
| TPRS micro-narratives | ✓ | ✓ (narrated) | |
| Shadowing tool | | ✓ | ✓ |
| Writing prompts | ✓ | | |
| Spoken reaction prompts | | | ✓ |

The pattern to avoid: building features that are satisfying to use but only reinforce what you can already do. Reading practice feels productive. Speaking practice feels uncomfortable. The discomfort is usually the signal that it's the domain that needs the work.

---

*More sections to come: features, architecture, tools.*
