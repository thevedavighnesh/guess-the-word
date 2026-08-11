def score_guess(guess: str, answer: str):
    """
    Compare a guess against the answer, both 5-letter uppercase strings.
    Returns a list of 5 strings: 'green', 'orange', or 'grey'.

    - green:  letter is correct and in the correct position
    - orange: letter is in the word but in the wrong position
    - grey:   letter is not in the word (accounting for letters already
              matched by earlier green/orange matches, so duplicate
              letters are scored correctly)
    """
    guess = guess.upper()
    answer = answer.upper()
    length = len(answer)

    result = ["grey"] * length
    answer_chars = list(answer)
    guess_chars = list(guess)

    # First pass: exact position matches (green). Consume matched letters
    # from answer_chars so they aren't reused for orange matches.
    for i in range(length):
        if guess_chars[i] == answer_chars[i]:
            result[i] = "green"
            answer_chars[i] = None
            guess_chars[i] = None

    # Second pass: right letter, wrong position (orange).
    for i in range(length):
        if guess_chars[i] is None:
            continue
        if guess_chars[i] in answer_chars:
            result[i] = "orange"
            answer_chars[answer_chars.index(guess_chars[i])] = None

    return result
