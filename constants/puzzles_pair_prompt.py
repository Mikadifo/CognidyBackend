from models.puzzle_pairs import MAX_PUZZLES


PROMPT = """
You are given:
- previous_puzzles: an array of JSON objects like { "_id": string, "pairs": [{ "left": string, "right": string }] }
- new_file: a text extracted directly from an educational file (e.g., notes, syllabus, or material).

---

### TASK
Generate 1–5 new match-the-pair puzzles that come **only** from the actual content and terminology found in new_file.
Do **not** infer or assume extra topics, frameworks, or domains not explicitly present in the file.

Your job is to extract, reformulate, and structure puzzles **strictly from what the text itself teaches or discusses**.

Each puzzles must have a "pair" array with exactly 4 pairs, where in each pair:
- left = exactly one word (a key term from the file)
- right = a short descriptive phrase (max 6 words) explaining that term, derived from the file content

---

### INTEGRATION RULES
- If a puzzle is merged (combined or updated using new file):
  - Keep "_id"
  - Update to different "pairs", relevant to the new question.
- If a puzzle is new:
  - Omit "_id"

Do not include previous puzzles if:
- Pairs object is identical (case-insensitive)
- No meaningful new content was added

---

### CONTENT RULES
- Derive all puzzles only from the text of new_file.
- Stay strictly within the inferred topic area.
- Every puzzle must clearly reference ideas, terminology, or processes explicitly present in the text (e.g., "ER models," "Arrays," "Geometry," "Atoms," "Law", etc...).
- Do **not** generalize to broad or unrelated subjects
- Avoid vague statements like “Understand key concepts” or “Learn fundamentals.”
- Ensure clarity and precision. Each puzzle should reflect a specific concept mentioned in the text.
- Avoid hallucinating unrelated frameworks, tools, or disciplines.
- Ensure each puzzle is clear, concise, and educationally relevant to the new_file.

---

Include a puzzle ONLY if:
- It’s newly inferred from the new file, OR
- It’s a merged/updated version of a previous puzzle.

Do not include previous puzzles in the output if they:
- Are identical in pairs to the previous puzzle (case-insensitive comparison is allowed),
- Have no content merged.

---

### RULES
- If it revisits or expands on an existing topic, merge or update relevant previous puzzles.
- Avoid duplicating existing puzzles — merge only when overlap exists.
- Keep previous "_id" for merged puzzles.
- If a puzzle is merged:
  - Keep "_id"
  - Update pairs
- If a puzzle is new:
  - No "_id"

Include a puzzle in the output only if it is:
- A new puzzle from the file, or
- A previous puzzle that was merged/updated with new file content (question and options changed meaningfully and correct added).

---

### OUTPUT FORMAT
Return only a JSON array containing **only new or merged puzzles**:
[
  { "pairs": [{ "left": string, "right": string }] }
]

---

### EXAMPLE
Previous puzzles:
[
  { 
    "_id": "p1",
    "pairs": [
      { "left": "Planet", "right": "Body orbiting a star" },
      { "left": "Star", "right": "Mass of gas producing light and heat" },
      { "left": "Moon", "right": "Natural satellite orbiting a planet" },
      { "left": "Asteroid", "right": "Small rocky object orbiting the Sun" }
    ]
  },
  { 
    "_id": "p2",
    "pairs": [
      { "left": "Galaxy", "right": "Collection of billions of stars" },
      { "left": "Nebula", "right": "Cloud of gas and dust in space" },
      { "left": "Quasar", "right": "Extremely luminous active galactic nucleus" },
      { "left": "BlackHole", "right": "Region in space with gravity so strong nothing escapes" }
    ]
  }
]

Output:
[
  { 
    "_id": "p2",
    "pairs": [
      { "left": "Galaxy", "right": "Massive collection of stars and matter" },
      { "left": "Nebula", "right": "Cloud of gas and dust in space" },
      { "left": "Quasar", "right": "Extremely luminous active galactic nucleus" },
      { "left": "BlackHole", "right": "Region with gravity so strong that nothing can escape" }
    ]
  },
  {
    "pairs": [
      { "left": "Comet", "right": "Icy body that develops a tail near the Sun" },
      { "left": "Meteor", "right": "Space rock entering Earth's atmosphere" },
      { "left": "Satellite", "right": "Object orbiting a planet or moon" },
      { "left": "SpaceStation", "right": "Habitable artificial satellite in orbit" }
    ]
  }
]
"""

def get_puzzles_prompt(prev_puzzles):
    return f"Previous puzzles to use: {prev_puzzles}\n\n You can only generate {MAX_PUZZLES - len(prev_puzzles)} new goals, but you can merge and/or reorder the previous ones with a new one as long as the total order is not more than {MAX_PUZZLES}" + PROMPT
