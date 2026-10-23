# English AI-writing tells

For docs, READMEs, code comments, and fiction. Run `scan.py --lang en` or let it detect English.

## 1. Empty vocabulary

**Symptoms**

> seamless, robust, leverage, unlock, empower, elevate, delve, cutting-edge, game-changer, world-class, holistic, synergy.

**Why it fails**：These words signal intent to impress. They do not name an action or a result.

**Fix**：Name the action and its outcome.

> The importer reads 1,000 rows in 0.4 seconds.

**Rule**：`en-buzz`（warn）。

## 2. Significance inflation

**Symptoms**

> In today's fast-paced world, this marks a pivotal moment and ushers in a new era.

**Why it fails**：The claim has no evidence and reads the same for any product.

**Fix**：Start with a dated event, a number, or a scene.

> In March we cut the signup flow from five steps to three.

**Rule**：`en-grand-opening`（block）。

## 3. Chatbot closers

**Symptoms**

> I hope this helps. Let me know if you have any questions.

**Why it fails**：A chat artifact pasted into a deliverable.

**Fix**：Delete it. End on the content.

**Rule**：`en-chatbot`（block）。

## 4. Negative parallelism

**Symptoms**

> It's not just a tool, it's a paradigm shift.
>
> Not only fast, but also reliable.

**Why it fails**：The formula manufactures emphasis whether or not it is earned.

**Fix**：State the second half directly.

> The tool runs locally and works offline.

**Rule**：`en-negparallel`（warn）。

## 5. Rule of three

**Symptoms**

> fast, reliable, and scalable; innovation, inspiration, and insight.

**Why it fails**：A forced trio has one filler item.

**Fix**：Use the number of items the content requires.

**Rule**：No dedicated rule; check while editing.

## 6. Hedging

**Symptoms**

> It's worth noting that this may potentially improve outcomes.

**Why it fails**：Qualifiers stack and the claim disappears.

**Fix**：Give the scope or the number.

> This cuts p95 latency from 1.8s to 220ms.

**Rule**：`en-hedge`（warn）。

## 7. Announcements

**Symptoms**

> Let's dive in. Here's what you need to know. In this article, we'll explore.

**Why it fails**：The writer announces the text instead of writing it.

**Fix**：Delete the navigation and start with the content.

**Rule**：`en-signpost`（block）。

## 8. Vague sourcing

**Symptoms**

> Studies show that teams are 40% more productive.

**Why it fails**：The number borrows authority and avoids a citation.

**Fix**：Name the source, year, sample, and link. If you cannot, cut the number.

**Rule**：`en-transition` does not cover this; check manually. Use `zh-fake-source` only for Chinese.

## 9. Fake specificity

**Symptoms**

> Trusted by thousands of teams. "It changed our workflow." — Sarah Chen, VP Engineering.

**Why it fails**：An invented detail is worse than a vague claim because it looks checkable.

**Fix**：Use real names and numbers, or cut the claim.

**Rule**：Manual check.

## 10. Listification

**Symptoms**

> Every paragraph becomes a bullet list with a bold label.

**Why it fails**：Argument becomes a table of contents; causes and tradeoffs disappear.

**Fix**：Use lists for parallel steps only. Write reasoning as prose.

**Rule**：`metric-listification`（warn）。

## 11. Uniform rhythm

**Symptoms**

> Every sentence is 25 to 30 words. Every paragraph is four sentences.

**Why it fails**：The template decides the length, not the content.

**Fix**：Put the important point in a short sentence. Let a paragraph run long when it needs to.

**Rule**：`metric-uniform-rhythm`（warn）。

## 12. Em dashes

**Symptoms**

> The policy — announced without warning — affects thousands.

**Why it fails**：A cluster of em dashes is a machine tell. One is fine.

**Fix**：Use a period, comma, colon, or parentheses.

**Rule**：`en-emdash`（warn）。

## 13. Reassurance

**Symptoms**

> You're in control. Feel free to modify this. Don't worry.

**Why it fails**：It grants control the user already has and adds no information.

**Fix**：State what changed, what is risky, and how to undo it.

> Revert with `git revert <sha>`.

**Rule**：`en-reassurance`（block）、`en-comfort`（warn）。

## 14. Emotional value in technical docs

**Symptoms**

> Welcome to SuperTool! We're excited to have you here. Happy coding!

**Why it fails**：Technical readers want install steps, usage, limits, and errors.

**Fix**：Write the function, install, usage, and limitations.

**Rule**：`en-emotional-value`（warn）。

## 15. Technical comments as permission slips

**Symptoms**

> `# Feel free to modify this.`

**Why it fails**：A comment should state behavior, invariants, reasons, and pitfalls.

**Fix**：Write the invariant.

> `# Call inside a transaction; concurrent calls duplicate the charge.`

**Rule**：`en-reassurance`（block, in `--code` mode）。

## 16. Fiction: POV leaks

**Symptoms**

> He knew what she was thinking. Meanwhile, across town, someone was waiting.

**Why it fails**：The scene leaves the viewpoint character's knowledge.

**Fix**：Write what the POV can see, hear, and infer. Use a scene break for a new POV.

**Rule**：`fic-pov-internal`、`fic-pov-jump`（English fiction rules are not implemented yet; use the manual check）。

## 17. Fiction: stock similes

**Symptoms**

> Her eyes were like knives. The room was a tomb.

**Why it fails**：Safe, high-frequency comparisons that do not come from the character.

**Fix**：Use an association this character would make.

**Rule**：`zh-stock-simile` covers Chinese; for English, check manually.

## What not to flag

- One em dash, one however, one robust.
- Perfect grammar; the writer may have been edited.
- A single short sentence for emphasis.
- Unsourced claims; most of the web is unsourced.
- A voice sample from the user; match it.

`scan.py --list-rules` prints the full rule table.
