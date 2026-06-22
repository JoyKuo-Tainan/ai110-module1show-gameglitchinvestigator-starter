import random
import streamlit as st

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    # FIX: attempts started at 1, so "Attempts left" was off by one on first
    # load and the player got one fewer guess than attempt_limit promised.
    # Initialize at 0 to match the New Game reset and give the full count.
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

st.info(
    f"Guess a number between 1 and 100. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

# FIX: the "Enter your guess" box never cleared after submitting a guess or
# starting a new game. Streamlit forbids modifying a widget's value via
# session_state after the widget is created in the same run, so clearing is done
# inside the buttons' on_click callbacks (which run before the rerun).
guess_input_key = f"guess_input_{difficulty}"


def handle_submit():
    # FIX: parse the guess and append it to history HERE, inside the callback,
    # so it happens before the script reruns. Because the Developer Debug Info
    # expander renders ABOVE this button, doing the append in the body (below)
    # left the debug info one guess behind. Running it in the callback means the
    # new guess shows up immediately after Submit is clicked. The rerun also
    # clears the previous hint before this insert, so the old hint never lingers
    # next to the new guess. The parse result is stashed for the body to finish
    # scoring/win-loss handling.
    raw = st.session_state.get(guess_input_key, "")
    st.session_state[guess_input_key] = ""

    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw)
    if ok:
        st.session_state.history.append(guess_int)
    else:
        st.session_state.history.append(raw)

    st.session_state.submit_result = (ok, guess_int, err)


def handle_new_game():
    st.session_state[guess_input_key] = ""


raw_guess = st.text_input(
    "Enter your guess:",
    key=guess_input_key
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀", on_click=handle_submit)
with col2:
    new_game = st.button("New Game 🔁", on_click=handle_new_game)
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # FIX: New Game only reset attempts and secret, so the old guess history
    # (and a finished "won"/"lost" status and score) carried over into the new
    # game. Now reset history/score/status too, and draw the new secret from the
    # current difficulty's range (low, high) instead of a hardcoded 1-100.
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.history = []
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    # FIX: attempts increment, guess parsing, and the history append all happen
    # in handle_submit now (so the debug info reflects the guess right away).
    # Here we just read the stashed parse result and finish scoring/win-loss.
    ok, guess_int, err = st.session_state.submit_result

    if not ok:
        st.error(err)
    # FIXME: Logic breaks here - guessing range fix
    elif guess_int < 1 or guess_int > 100:
        st.error("Guess must be between 1 and 100.")
    else:

        # FIXME: Logic breaks here — on even attempts the secret is cast to a
        # string, forcing check_guess into a lexicographic (text) comparison
        # that gives wrong HIGHER/LOWER hints.
        # if st.session_state.attempts % 2 == 0:
        #     secret = str(st.session_state.secret)
        # else:
        #     secret = st.session_state.secret
        #
        # outcome, message = check_guess(guess_int, secret)

        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
