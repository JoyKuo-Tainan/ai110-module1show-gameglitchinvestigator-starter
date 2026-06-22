from logic_utils import check_guess, get_range_for_difficulty


def test_difficulty_range_grows_with_difficulty():
    # Bug (from reflection.md): get_range_for_difficulty() had Normal at 1-100
    # and Hard at 1-50, so "Hard" was actually easier than "Normal". After the
    # fix the range must grow with difficulty: Easy < Normal < Hard.
    easy_low, easy_high = get_range_for_difficulty("Easy")
    normal_low, normal_high = get_range_for_difficulty("Normal")
    hard_low, hard_high = get_range_for_difficulty("Hard")

    # Concrete fixed values.
    assert (easy_low, easy_high) == (1, 20)
    assert (normal_low, normal_high) == (1, 50)
    assert (hard_low, hard_high) == (1, 100)

    # The defining property of the bug: Hard must NOT be easier than Normal.
    # Width = high - low; a harder difficulty has a wider range.
    easy_width = easy_high - easy_low
    normal_width = normal_high - normal_low
    hard_width = hard_high - hard_low
    assert easy_width < normal_width < hard_width


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result[0] == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result[0] == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result[0] == "Too Low"
