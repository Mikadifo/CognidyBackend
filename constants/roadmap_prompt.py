from models.roadmap_goal import MAX_GOALS


PROMPT = """
You are given:
- previous_goals: an array of { "_id": string, "order": number, "title": string, "completed": boolean }
- new_file: a text extracted directly from an educational file (e.g., notes, syllabus, or material).

---

### TASK
Generate 1–5 new roadmap goals that come **only** from the actual content and terminology found in new_file.
Do **not** infer or assume extra topics, frameworks, or domains not explicitly present in the file.

Your job is to extract, reformulate, and structure learning goals **strictly from what the text itself teaches or discusses**.

---

### INTEGRATION RULES
- If a goal is merged (combined or updated using new file):
  - Keep "_id"
  - Update to a different "title" (max 4 words).
  - Add "brief" (max 14 words).
  - "completed" must follow logical progression (no true, false, true).
- If a goal is new:
  - Omit "_id"
  - Include "brief"
  - Set "completed": false

Do not include previous goals if:
- Title is identical (case-insensitive)
- Only order changed
- No meaningful new content or brief was added

---

### CONTENT RULES
- Derive all goals only from the text of new_file.
- Stay strictly within the inferred topic area.
- Every goal must clearly reference ideas, terminology, or processes explicitly present in the text (e.g., "ER models," "Arrays," "Geometry," "Atoms," "Law", etc...).
- Do **not** generalize to broad or unrelated subjects
- Avoid vague statements like “Understand key concepts” or “Learn fundamentals.”
- Ensure clarity and precision. Each goal should reflect a specific concept mentioned in the text.
- Avoid hallucinating unrelated frameworks, tools, or disciplines.
- Ensure each goal is clear, concise, and educationally relevant to the new_file.

---

Include a goal ONLY if:
- It’s newly inferred from the new file, OR
- It’s a merged/updated version of a previous goal.

Do not include previous goals in the output if they:
- Are identical in title to the previous goal (case-insensitive comparison is allowed),
- Only have a different order,
- Have no brief added or content merged.

---

### RULES
- If the new file represents **a more advanced topic**, place the new goals **after** the highest previous order number.
- If it revisits or expands on an existing topic, merge or update relevant previous goals.
- Avoid duplicating existing goals — merge when overlap exists.
- Keep previous "_id" for merged goals.
- "order" must increase logically based on topic progression (e.g., 1, 2, 3 → new advanced file should continue at 4, 5, ...).
- If a goal is merged:
  - Keep "_id"
  - Update title (≤ 4 words)
  - Add "brief" (≤ 14 words)
  - Maintain logical "completed" flow (no true, false, true)
- If a goal is new:
  - No "_id"
  - Include "brief"
  - Set "completed": false

- "brief" only for merged or new goals.

Include a goal in the output only if it is:
- A new goal from the file, or
- A previous goal that was merged/updated with new file content (title changed meaningfully and brief added).

---

### Ordering Rules
- Determine if the new file is introductory, intermediate, or advanced **based on its content**.
- Adjust goal order accordingly:
  - Introductory → insert before or early in roadmap.
  - Intermediate → between mid-level goals.
  - Advanced → append after last goal.
- The final output should have consistent logical progression.

---

### OUTPUT FORMAT
Return only a JSON array containing **only new or merged goals**:
[
  {"order": number, "title": string, "brief"?: string, "completed": boolean}
]

Notes:
- "order" should correspond to the logical roadmap numbering.
- "order" in the output should reflect the original roadmap order.
- Skip numbers for previous goals that are unchanged or not included.
- It is acceptable for order to be non-sequential as long as it matches with the goals not included in the final json (e.g., 1, 3, 4, 7).
- "brief" only for merged/new goals.
- "completed": keep old value or false for new ones.

---

### EXAMPLE 1
File content topic: "Arrays and their memory relationship with pointers"
Previous goals:
[{"_id": "1", "order": 1, "title": "Understand Pointers", "completed": true},{"_id": "2", "order": 2, "title": "Pointer Arithmetic", "completed": false}]
Output:
[{"order": 1, "title": "Understand Arrays", "brief": "Learn array structure and memory.", "completed": false},{"order": 3, "_id": "1", "title": "Understand C++ Pointers", "brief": "Relate pointers to arrays.", "completed": false}]
"""

def get_roadmap_prompt(prev_goals):
    return f"Previous goals to use: {prev_goals}\n\n You can only generate {MAX_GOALS - len(prev_goals)} new goals, but you can merge and/or reorder the previous ones with a new one as long as the total order is not more than {MAX_GOALS}" + PROMPT
