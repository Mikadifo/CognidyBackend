from models.quizzes import MAX_QUIZZES


PROMPT = """
You are given:
- previous_quizzes: an array of JSON objects like { "_id": string, "question": string, "options": [string] }
- new_file: a text extracted directly from an educational file (e.g., notes, syllabus, or material).

---

### TASK
Generate 1–5 new quizzes that come **only** from the actual content and terminology found in new_file.
Do **not** infer or assume extra topics, frameworks, or domains not explicitly present in the file.

Your job is to extract, reformulate, and structure quizzes **strictly from what the text itself teaches or discusses**.

---

### INTEGRATION RULES
- If a quizz is merged (combined or updated using new file):
  - Keep "_id"
  - Update to a different "question".
  - Update to different "options", relevant to the new question.
  - Add "correct" field, which is the index of the correct anwser in the new options array.
- If a quizz is new:
  - Omit "_id"
  - Include "correct" field, index of the correct anwser in the options array

Do not include previous quizzes if:
- Question is identical (case-insensitive)
- No meaningful new content was added

---

### CONTENT RULES
- Derive all quizzes only from the text of new_file.
- Stay strictly within the inferred topic area.
- Every quizz must clearly reference ideas, terminology, or processes explicitly present in the text (e.g., "ER models," "Arrays," "Geometry," "Atoms," "Law", etc...).
- Do **not** generalize to broad or unrelated subjects
- Avoid vague statements like “Understand key concepts” or “Learn fundamentals.”
- Ensure clarity and precision. Each quizz should reflect a specific concept mentioned in the text.
- Avoid hallucinating unrelated frameworks, tools, or disciplines.
- Ensure each quizz is clear, concise, and educationally relevant to the new_file.

---

Include a quizz ONLY if:
- It’s newly inferred from the new file, OR
- It’s a merged/updated version of a previous quizz.

Do not include previous quizzes in the output if they:
- Are identical in question to the previous quizz (case-insensitive comparison is allowed),
- Have no content merged.

---

### RULES
- If it revisits or expands on an existing topic, merge or update relevant previous quizzes.
- Avoid duplicating existing quizzes — merge only when overlap exists.
- Keep previous "_id" for merged quizzes.
- If a quizz is merged:
  - Keep "_id"
  - Update question
  - Update options
  - Add "correct" field (index of correct option in the options array)
- If a quizz is new:
  - No "_id"
  - Include "correct"

Include a quizz in the output only if it is:
- A new quizz from the file, or
- A previous quizz that was merged/updated with new file content (question and options changed meaningfully and correct added).

---

### OUTPUT FORMAT
Return only a JSON array containing **only new or merged quizzes**:
[
  {"question": string, "options": [string], "correct": number}
]

---

### EXAMPLE 1
File content topic: "The Solar System and its planets"

Previous quizzes:
[
  {
    "_id": "1",
    "question": "Which planet is known as the Red Planet?",
    "options": ["Earth", "Mars", "Jupiter", "Venus"],
    "correct": 1
  },
  {
    "_id": "2",
    "question": "The Sun is a star that produces its own light.",
    "options": ["True", "False"],
    "correct": 0
  }
]

Output:
[
  {
    "question": "What is the largest planet in our solar system?",
    "options": ["Earth", "Saturn", "Jupiter", "Neptune"],
    "correct": 2
  },
  {
    "_id": "1",
    "question": "Which planet appears red due to iron oxide on its surface?",
    "options": ["Mars", "Venus", "Mercury", "Uranus"],
    "correct": 0
  }
]
"""

def get_quizzes_prompt(prev_quizzes):
    return f"Previous quizzes to use: {prev_quizzes}\n\n You can only generate {MAX_QUIZZES - len(prev_quizzes)} new goals, but you can merge and/or reorder the previous ones with a new one as long as the total order is not more than {MAX_QUIZZES}" + PROMPT
