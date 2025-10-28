PROMPT = """
You are given:
- previous_goals: an array of { "_id": string, "order": number, "title": string, "completed": boolean }
- new_file: e.g., notes, syllabus, or course material

Task:
Generate 1–5 new roadmap goals from new_file_content and integrate them with previous_goals.

Integration rules:
- If a goal is merged (combined or updated using new file):
  - Keep "_id"
  - Update to a different "title" (max 4 words).
  - Add "brief" (max 14 words).
  - "completed" must follow logical progression (no true, false, true).
- If a goal is new: no "_id", include "brief", set "completed": false.

Do not include previous goals in the output if they:
- Are identical in title to the previous goal (case-insensitive comparison is allowed),
- Only have a different order,
- Have no brief added or content merged.

Output format:
Return only a JSON array (with only the new goals or merged goals):
[{"order": number, "title": string, "brief"?: string, "completed": boolean}]

- "order" in the output should reflect the original roadmap order.
- Skip numbers for previous goals that are unchanged or not included.
- It is acceptable for order to be non-sequential as long as it matches with the goals not included in the final json (e.g., 1, 3, 4, 7).


Rules:
- "order" starts at 1 sequentially.
- "brief" only for merged or new goals.
- "completed": keep previous values or false for new ones.

Include a goal in the output only if it is:
- A new goal from the file, or
- A previous goal that was merged/updated with new file content (title changed meaningfully and brief added).

Example:
Previous goals:
[{"_id": "1", "order": 1, "title": "Understand Pointers", "completed": true},{"_id": "2", "order": 2, "title": "Pointer Arithmetic", "completed": false}]
New file content: "Arrays and their memory relationship with pointers."
Output:
[{"order": 1, "title": "Understand Arrays", "brief": "Learn array structure and memory.", "completed": false},{"order": 3, "_id": "1", "title": "Understand C++ Pointers", "brief": "Relate pointers to arrays.", "completed": false}]
"""

def get_roadmap_prompt(prev_goals):
    return f"Previous goals: {prev_goals}" + PROMPT
