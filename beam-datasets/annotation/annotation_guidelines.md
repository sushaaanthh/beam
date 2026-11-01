# B.E.A.M. Annotation Guidelines

Version: 1.0.0  
Status: Ratified  
Audience: Human annotators  

These guidelines govern how human annotators should classify Reddit posts
and comments using the B.E.A.M. emotion taxonomy.

The guidelines are normative. When in doubt, annotators should refer to the
taxonomy definitions and the example annotations in `examples.jsonl`.

---

## 1. Core Principles

### 1.1 Classify Expressed Emotion, Not Inferred Emotion

Annotate the emotion the **author is expressing**, not the emotion an
outsider would infer from the situation.

- "My house burned down" → the author may express shock, numbness, or
  resilience. Classify the **expressed** state, not the **situational**
  expectation.

### 1.2 Context Over Keywords

No single word or phrase determines an emotion label. Annotators must
evaluate the full text and its pragmatic context.

- "kill me, this exam was brutal" — hyperbolic stress, **not** literal
  self-harm intent.
- "I'm so happy for my friend" — positive affect directed toward another,
  not the author's own achievement.

### 1.3 The Author Is the Reference Frame

When the text discusses another person's emotions, the annotation refers
to the author's emotional state in relation to that discussion, not the
third party's state.

- "My brother is depressed" — if the author expresses concern, the primary
  may be APPREHENSION_ANXIETY or SADNESS_DEJECTION. If the author is
  reporting analytically, the primary may be NEUTRAL_ANALYTICAL.

### 1.4 When in Doubt, Use NEUTRAL_ANALYTICAL

If no emotion is clearly dominant, or if the author is reporting facts
without emotional coloring, use NEUTRAL_ANALYTICAL. Do not force a
non-neutral label.

---

## 2. Label Structure

### 2.1 Primary Emotion

Every record must have exactly one primary emotion label, chosen from the
ten-class taxonomy.

The primary emotion is the **dominant** emotional state expressed by the
author. If multiple emotions are clearly present, choose the one that most
pervades the text or that the author seems most invested in expressing.

### 2.2 Secondary Emotion

A secondary emotion may be recorded when a second emotion materially
contributes to the interpretation of the text.

- The secondary emotion must be from the ten-class taxonomy.
- The secondary emotion must be distinct from the primary.
- If no second emotion is clearly present, `secondary_emotion` must be
  `null`.

Do not force a secondary emotion.

### 2.3 Intensity

Intensity reflects the **strength of emotional expression**, not clinical
severity.

| Value | Label | Guidance |
|-------|-------|----------|
| 1 | Very Low | Emotion is barely perceptible; text is mostly neutral with subtle emotional coloring. |
| 2 | Low | Emotion is present but muted; author may be downplaying or the context tempers it. |
| 3 | Moderate | Emotion is clearly present and stable; typical everyday expression. |
| 4 | High | Emotion is strong; author is invested and the affect is unmistakable. |
| 5 | Very High | Emotion is overwhelming; author is in crisis, ecstatic, or profoundly moved. |

Examples:
- "It was okay, I guess." → JOY_FULFILLMENT, intensity 1 or 2
- "I'm pretty happy with how things went." → JOY_FULFILLMENT, intensity 3
- "I'm over the moon right now!!!" → JOY_FULFILLMENT, intensity 5
- "I'm a bit worried about the results." → APPREHENSION_ANXIETY, intensity 2
- "I can't breathe, I'm so anxious." → APPREHENSION_ANXIETY, intensity 5

### 2.4 Confidence

Confidence reflects the **annotator's certainty**, not the emotion's intensity.

| Value | Label | Guidance |
|-------|-------|----------|
| 1 | Uncertain | Genuinely ambiguous; annotator is guessing. |
| 2 | Somewhat Confident | Most likely label, but rival interpretations exist. |
| 3 | Confident | Clear dominant emotion; annotator is sure of the label. |

If confidence is 1, annotators should record notes explaining the
ambiguity.

---

## 3. Context Flags

Context flags capture pragmatic, situational, or stylistic information that
affects interpretation without replacing the emotion label.

The flag set is **closed**. Annotators must choose from the allowed values.

| Flag | Meaning |
|------|---------|
| PERSONAL_EXPERIENCE | The author is describing their own direct experience. |
| THIRD_PARTY_EXPERIENCE | The author is describing another person's experience or emotions. |
| HYPOTHETICAL | The author is describing a hypothetical, imagined, or counterfactual scenario. |
| FICTIONAL | The author is discussing fictional events, characters, or media. |
| QUOTED_TEXT | The author is quoting someone else's words. |
| NEWS_OR_REPORTING | The author is reporting factual events without personal involvement. |
| HUMOR | The author is being genuinely humorous; the primary purpose is comedy. |
| SARCASM | The author is using sarcasm, irony, or mockery. |
| NOSTALGIA | The author is reflecting on the past with longing or bittersweet affect. |
| ADVICE_SEEKING | The author is explicitly asking for guidance, help, or opinions. |
| ADVICE_GIVING | The author is giving guidance, help, or opinions. |
| ACHIEVEMENT | The text centers on a personal achievement, milestone, or completion. |
| LOSS | The text centers on loss, grief, or separation. |
| RELATIONSHIP | The text centers on romantic, familial, or platonic relationship dynamics. |
| ACADEMIC | The text centers on school, university, studying, or research. |
| WORK | The text centers on employment, career, or professional life. |
| FAMILY | The text centers on family dynamics, parenting, or family members. |
| HEALTH | The text centers on physical or mental health, illness, or treatment. |
| FINANCIAL | The text centers on money, bills, debt, or financial stress. |
| SOCIAL_CONFLICT | The text centers on interpersonal tension, arguments, or exclusion. |

### 3.1 Flag Combinations

Multiple flags may be applied to a single record.

Examples:
- A post about a childhood memory with fondness → `NOSTALGIA`, `PERSONAL_EXPERIENCE`
- A comment on a news article expressing concern → `NEWS_OR_REPORTING`, `THIRD_PARTY_EXPERIENCE`
- A vent about a toxic workplace → `WORK`, `SOCIAL_CONFLICT`, `PERSONAL_EXPERIENCE`

---

## 4. Special Cases

### 4.1 Mixed Emotions

When two emotions are both clearly present and roughly equal in strength:

- Assign the **more central or pervasive** emotion as primary.
- Assign the other as **secondary**.
- Lower the intensity of both by approximately one level compared to a
  single-emotion text of the same apparent strength.

Example:
- "I'm proud I got the job, but I'm terrified I'll mess up." →
  Primary: APPREHENSION_ANXIETY (intensity 3), Secondary: PRIDE_ACCOMPLISHMENT (intensity 2)
  OR Primary: PRIDE_ACCOMPLISHMENT (intensity 3), Secondary: APPREHENSION_ANXIETY
  (annotator judgment based on what the author seems more focused on).

### 4.2 Ambiguous Cases

If the text genuinely supports two rival interpretations with similar
plausibility:

- Choose the label that best fits the **majority of the text**.
- Set `confidence: 1` or `2`.
- Add a note explaining the ambiguity.

Do not skip ambiguous records. Record them with low confidence rather than
guessing.

### 4.3 Neutral / Analytical Content

Use NEUTRAL_ANALYTICAL when:

- The author is sharing information, asking practical questions, or
  reporting events.
- The author describes another person's emotions without expressing their
  own strong affect.
- The text is technical, instructional, or procedural.
- The author is making an argument without strong emotional investment.

Do **not** use NEUTRAL_ANALYTICAL to avoid difficult classifications.
If an emotion is clearly present, assign it.

### 4.4 Sarcasm

Sarcasm changes the pragmatic meaning of text.

- If the author is **sincerely** expressing an emotion through sarcasm,
  classify the **sincere underlying emotion**.
- If the text is purely ironic with no genuine emotional content,
  classify as NEUTRAL_ANALYTICAL.

Examples:
- "Oh great, another meeting that could have been an email" →
  Primary: FRUSTRATION_FRICTION (the author is genuinely frustrated,
  using sarcasm to express it).
- "Wow, what a brilliant idea" (with no other context suggesting sincerity)
  → NEUTRAL_ANALYTICAL (pure irony, no expressed emotion).

### 4.5 Humor

If the author is genuinely amused or joyful **and** the text is primarily
comedic:

- Primary: JOY_FULFILLMENT (if the author is expressing their own amusement)
- Flag: HUMOR
- Intensity reflects the strength of amusement.

If the humor is primarily ironic or mocking without genuine joy:

- Use the underlying emotion label, or NEUTRAL_ANALYTICAL if none is present.
- Flag: SARCASM if appropriate.

### 4.6 Nostalgia

Nostalgia is a **context flag**, not an emotion label.

Nostalgic texts should be classified by their **dominant expressed emotion**,
which may be:

- JOY_FULFILLMENT (if fond and positive)
- SADNESS_DEJECTION (if bittersweet or loss-oriented)
- CALM_SERENITY (if peaceful reflection)

Always flag nostalgic content with `NOSTALGIA`.

### 4.7 Personal Storytelling

First-person personal narratives are common. The annotation principle
remains: classify the **author's expressed emotion**, not the events
themselves.

A story about a difficult event may express resilience, sadness, or
neutrality depending on how the author frames it.

### 4.8 Hypothetical Statements

Hypothetical or "what if" statements should be classified based on the
**emotional stance** the author takes toward the hypothetical scenario.

- "What if I fail my exam?" with anxiety → APPREHENSION_ANXIETY
- "What if I won the lottery?" with excitement → JOY_FULFILLMENT or HOPE_OPTIMISM
- "What if everything went wrong?" with worry → APPREHENSION_ANXIETY
- "What if we could eliminate all disease?" with curiosity → CURIOSITY_FOCUS or HOPE_OPTIMISM

Always flag hypothetical content with `HYPOTHETICAL`.

### 4.9 Quoted Speech

When the author quotes another person's words:

- Classify the **author's emotion** in relation to the quote, not the
  emotion of the quoted speaker.
- If the author is sharing the quote neutrally, use NEUTRAL_ANALYTICAL.
- If the author is expressing their own reaction to the quote, classify
  that reaction.
- Flag: `QUOTED_TEXT`

Example:
- "My therapist always says: 'You can't pour from an empty cup.'" →
  If the author is reflecting on this insight with calm acceptance:
  Primary: CALM_SERENITY, Flag: QUOTED_TEXT

### 4.10 Discussions About Another Person's Emotions

When the author describes another person's emotional state:

- Classify the **author's emotional stance** toward that information.
- If the author is concerned → APPREHENSION_ANXIETY or SADNESS_DEJECTION
- If the author is happy for the other person → JOY_FULFILLMENT
- If the author is reporting analytically → NEUTRAL_ANALYTICAL
- Flag: `THIRD_PARTY_EXPERIENCE`

### 4.11 Discussions of Fictional Events

Discussions of books, movies, games, or other fictional content follow
the same rules:

- Classify the **author's expressed emotion** about the fictional content.
- Flag: `FICTIONAL`
- Do not confuse the emotions of fictional characters with the author's emotions.

Examples:
- "That movie ending destroyed me. I cried for an hour." →
  Primary: SADNESS_DEJECTION, Flag: FICTIONAL
- "I love how the protagonist finally stands up for herself." →
  Primary: JOY_FULFILLMENT, Flag: FICTIONAL

### 4.12 Threat-Related Language

B.E.A.M. is **not** a clinical diagnostic system and is **not** a threat
detection system.

When text contains aggressive, violent, or threatening language:

- Determine whether the author is expressing **their own hostile intent** or
  **reporting/describing** external threat.
- If the author is venting frustration with aggression but has no actual
  violent intent, the primary label is FRUSTRATION_FRICTION.
- If the author is **reporting** a threat from another source, the primary
  label depends on the author's emotional stance (fear, analytical concern,
  etc.).
- If the text contains genuine violent intent toward others, this is outside
  the scope of the B.E.A.M. taxonomy. Do not force an emotion label. Record
  with confidence 1 and add a note.

Flag: `THREAT_REFERENCE` when the text references violence or threats
regardless of the author's role.

### 4.13 Self-Harm / Suicide-Related Language

B.E.A.M. is **not** a clinical risk-assessment tool.

When text contains self-harm or suicide references:

- Determine whether the language is **literal** or **figurative/hyperbolic**.
- Figurative language (e.g., "kill me, this exam was brutal", "I want to
  die of embarrassment") is **not** literal self-harm intent.
- If the text is genuinely expressing self-harm ideation, this is outside
  the scope of the B.E.A.M. taxonomy. Do not force an emotion label.
  Record with confidence 1 and add a note.

Flag: `SELF_HARM_REFERENCE` when the text references self-harm regardless
of intent, to support downstream review.

### 4.14 Mental-Health Terminology

Mental health diagnoses, medication references, and therapy discussions
do **not** automatically determine an emotion label.

- "I have generalized anxiety disorder" — if reported analytically:
  NEUTRAL_ANALYTICAL
- "My anxiety has been unbearable this week" — if the author is expressing
  distress: APPREHENSION_ANXIETY
- "My therapist helped me reframe my thinking" — if the author expresses
  relief or progress: CALM_SERENITY or JOY_FULFILLMENT

Flag: `HEALTH` for all mental health-related content.

### 4.15 Profanity

Profanity does not determine an emotion label. It is a stylistic marker.

- Profanity may co-occur with FRUSTRATION_FRICTION, JOY_FULFILLMENT, or
  any other label depending on context.
- Do not use profanity density as a proxy for emotion.

### 4.16 Political / Social Arguments

Political or social arguments may express strong emotion or may be purely
analytical.

- If the author is passionately advocating or opposing a position:
  FRUSTRATION_FRICTION, APPREHENSION_ANXIETY, or JOY_FULFILLMENT depending
  on affect.
- If the author is reporting or discussing analytically: NEUTRAL_ANALYTICAL
- Flag: `SOCIAL_CONFLICT` if relevant

### 4.17 Very Short or Context-Poor Text

Short text (e.g., "me too", "this", "lol", emoji-only comments) is
common on Reddit.

- If the text has no discernible emotional content: NEUTRAL_ANALYTICAL
- If the text is clearly positive or negative based on community convention
  (e.g., "lol" in a humor thread), use JOY_FULFILLMENT with low intensity
  and low confidence.
- Do not over-interpret. Set confidence accordingly.

---

## 5. Edge Cases and Decision Tree

When unsure, annotators should work through this decision sequence:

1. **Is the author expressing a clear emotion?**
   - No → NEUTRAL_ANALYTICAL
   - Yes → continue

2. **Is the text primarily humorous or sarcastic with no genuine affect?**
   - Yes → NEUTRAL_ANALYTICAL (Flag: HUMOR or SARCASM)
   - No → continue

3. **Is the emotion directed at a third party's experience?**
   - Yes → classify the author's stance (concern, happiness, neutrality)
   - No → continue

4. **Are multiple emotions clearly present?**
   - Yes → assign the more central as primary, the other as secondary
   - No → continue

5. **Which of the ten labels best captures the dominant expressed emotion?**
   - Use the taxonomy definitions and examples as guidance.

6. **What is the intensity?**
   - Consider the strength of expression, not the severity of the situation.

7. **How confident are you?**
   - If ambiguous, set low confidence and add a note.

---

## 6. Prohibited Classifications

Annotators must **never**:

- Assign a label based on a keyword without context.
- Infer emotions from the author's demographic or posting history.
- Diagnose mental health conditions from text.
- Assign emotion labels to quoted speech without considering the author's stance.
- Force a secondary emotion where none is clearly present.
- Use emotion labels as clinical risk indicators.
- Include personal identifying information (usernames, subreddit names are
  acceptable metadata but not in the annotation notes).

---

## 7. Annotation Record Requirements

Every annotation record must contain:

- `record_id`: stable identifier from the source dataset
- `text`: the text being annotated (verbatim or cleaned, as specified)
- `primary_emotion`: one of the ten taxonomy IDs
- `secondary_emotion`: one of the ten taxonomy IDs or `null`
- `intensity`: integer 1–5
- `confidence`: integer 1–3
- `context_flags`: array of allowed flag strings (may be empty)
- `annotator_id`: stable anonymous identifier for the annotator
- `annotation_timestamp`: ISO-8601 timestamp
- `notes`: string or `null`; free-text explanation for ambiguous or
  difficult cases

The machine-readable schema is defined in `schema.json`.

---

## 8. Quality Expectations

Before submitting annotations, annotators should verify:

- [ ] `primary_emotion` is one of the ten allowed IDs.
- [ ] `secondary_emotion` is either `null` or a valid ID distinct from `primary_emotion`.
- [ ] `intensity` is an integer between 1 and 5.
- [ ] `confidence` is an integer between 1 and 3.
- [ ] All `context_flags` are from the allowed flag set.
- [ ] `notes` is provided when `confidence` is 1 or when the case is
      ambiguous.
- [ ] No personal identifying information appears in `notes`.
- [ ] No Reddit usernames appear in any field.

---

## 9. Examples

See `examples.jsonl` for a diverse set of annotated examples illustrating
the guidelines in practice. The examples cover:

- Primary-only annotations
- Primary + secondary annotations
- Mixed emotions
- Ambiguous cases with low confidence
- Sarcasm and humor
- Third-party emotional discussion
- Hypothetical language
- Self-harm references (figurative)
- Threat-reporting language
- Mental health terminology
- Short or context-poor text

These examples are for annotation training only. They are **not** training
data for the emotion model unless explicitly labeled and validated through
the quality protocol.
