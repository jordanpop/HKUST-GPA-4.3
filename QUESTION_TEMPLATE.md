# Question Template & Examples

Use this format when adding new quiz questions.

## Exact JSON Format
Copy this template for each question:
```javascript
{
  q: "Your question text here?",
  options: ["Option A", "Option B", "Option C", "Option D", "Option E"],
  answer: 0,  // change to 0-4 depending on correct option
  explain: "Why is this the right answer? Brief explanation.",
  topic: "short-topic-name",
  difficulty: "easy"  // or "medium" or "hard"
}
```

## Example Question (Easy)
```javascript
{
  q: "What is the primary hormone produced by the pancreatic beta cells?",
  options: ["Insulin", "Glucagon", "Somatostatin", "Adrenaline", "Cortisol"],
  answer: 0,
  explain: "Beta cells in the islets of Langerhans secrete insulin in response to high blood glucose.",
  topic: "pancreatic-hormones",
  difficulty: "easy"
}
```

## Example Question (Medium)
```javascript
{
  q: "Why does insulin promote glucose uptake in muscle cells while glucagon does not?",
  options: [
    "Muscle cells lack glucose transporters",
    "Insulin causes GLUT4 translocation to cell membrane; glucagon acts on different pathways",
    "Glucagon is only active in liver",
    "Muscle cells are insulin-resistant",
    "Insulin has higher molecular weight"
  ],
  answer: 1,
  explain: "Insulin binds its receptor, activating signaling that moves GLUT4 transporters to the cell surface. Glucagon primarily affects liver glycogenolysis, not muscle glucose uptake.",
  topic: "glucose-transport",
  difficulty: "medium"
}
```

## Example Question (Hard)
```javascript
{
  q: "A patient presents with fasting glucose of 180 mg/dL but normal HbA1c. Which scenario best explains this?",
  options: [
    "Type 1 diabetes with poor morning control",
    "Recent onset of stress-induced hyperglycemia (cortisol surge)",
    "Chronic hyperglycemia from insulin resistance",
    "Pancreatic beta cell exhaustion",
    "GLUT1 deficiency"
  ],
  answer: 1,
  explain: "HbA1c reflects 2-3 month glucose average. Normal HbA1c with high fasting glucose suggests acute hyperglycemia, not chronic diabetes. Stress-induced cortisol spike causes acute hyperglycemia without chronic elevation.",
  topic: "glucose-regulation",
  difficulty: "hard"
}
```

## Topic Names (Conventions)
Use lowercase with hyphens:
- `pancreatic-hormones`
- `glucose-transport`
- `insulin-signaling`
- `endocrine-axis`
- `hormone-metabolism`

## How to Add Questions to Files

### For 3040.html (LIFS3040)
1. Open 3040.html
2. Find: `const lectures = [`
3. Locate the lecture you want to add to (e.g., lecture 1)
4. Find that lecture's `questions: [` array
5. Place cursor at END of array (before the closing `]`)
6. Paste the question object (make sure to add comma if not the last item)

### For 2921.html (HUMA2921)
Same process, but lectures are 3, 4, 5 (not 1-5)

## Important Rules
✅ DO:
- Always append to END of questions array
- Keep exactly 5 options per question
- Answer should be 0-4 (0-indexed)
- Use proper JSON syntax (commas, quotes)

❌ DON'T:
- Delete existing questions
- Reorder questions
- Change question indices
- Modify already-added questions
- Add fewer than 5 options

These rules protect localStorage, which tracks progress by question index.
