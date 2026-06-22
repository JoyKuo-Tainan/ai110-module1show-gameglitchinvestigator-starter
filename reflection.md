# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
The history was clean when the first time I ran it, and I could submit my guess, getting wrong hint sometimes. The number of attempts left was not accurate.
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
  - I cannot restart the game, and it never cleans the history.
  - Hint is not correct. When I guessed 9 and the target was 5, it asks me to go higher. 
  - able to guess numbers that are out of the range
  - attempts was 1 initially

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|0|ask me guess another number|the hint asks me go lower|none|
|6|Hint shows go higher since the secret is 54|asks me go lower |none |
|101|ask me guess another number|he hint asks me go higher|none|
|Hard|Hard should be harder than normal|normal range is 1 to 100 but hard is 1 to 50||
|New Game|clear the history and start a new game|Don't let me insert new numbers|none|

**Fixes Applied**

- Difficulty range bug: in `get_range_for_difficulty()`, Normal was 1–100 and Hard was 1–50, so Hard was actually easier than Normal. Swapped them to Normal 1–50 and Hard 1–100 so the range grows with difficulty (Easy 19 < Normal 49 < Hard 99). Marked the change with a `# FIX:` comment.

- New Game bug: the `if new_game:` handler only reset `attempts` and `secret`, so the old guess `history` (and a finished `"won"`/`"lost"` status and `score`) carried over into the next game — the history never cleared and a finished game stayed stuck. Added resets for `history`, `score`, and `status`, and changed the new secret to draw from the current difficulty's range (`random.randint(low, high)`) instead of a hardcoded `1-100`. Marked the change with a `# FIX:` comment.

- Attempts off-by-one bug: on first page load `attempts` was initialized to `1` instead of `0`, while the New Game handler reset it to `0`. Since "Attempts left" is computed as `attempt_limit - attempts`, the count displayed one fewer attempt on a fresh game and the player effectively lost a guess (the loss check `attempts >= attempt_limit` triggered one turn early). Changed the initial value to `0` so it matches the New Game path and gives the full attempt count. Marked the change with a `# FIX:` comment.

- Guess box not clearing bug: the "Enter your guess" text box never cleared after submitting a guess or starting a new game, so the previous guess stayed in the box. Streamlit forbids modifying a widget's value through `session_state` after that widget is created in the same run, so I added `on_click` callbacks to the Submit and New Game buttons (callbacks run before the rerun, where modifying widget state is allowed). The New Game callback (`handle_new_game`) clears the box. Marked the changes with `# FIX:` comments.

- Debug info one guess behind / hint lingering: the Developer Debug Info expander renders *above* the buttons, but the guess was being appended to history in the `if submit:` block *below* them, so the debug info only showed the new guess on the next interaction. I moved the attempts increment, guess parsing, and the `history.append` into the `handle_submit` callback (which runs before the rerun), so the new guess shows in the debug info immediately after Submit is clicked. The `if submit:` block now reads a stashed parse result (`submit_result`) and only finishes scoring/win-loss handling. Because each rerun starts fresh, the previous hint is already cleared before the new guess is inserted into history, so an old hint never lingers next to the new guess. Verified the win/loss messages still display by leaving the status change in the body (after the `status != "playing"` stop-check). Marked the changes with `# FIX:` comments.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
  - I'd check a function's actual return type before writing assertions against it. When I wrote tests for `check_guess`, I asserted `result == "Win"`, but `check_guess` actually returns a tuple `(outcome, message)` like `("Win", "🎉 Correct!")`, so the tests failed even though the game logic was correct. The fix was to assert on `result[0]` (the outcome) instead of the whole tuple. Next time I'll read the function signature/return value first so my tests check the right thing.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
