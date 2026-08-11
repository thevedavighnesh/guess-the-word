def score_guess(guess: str, answer: str):
    
    guess = guess.upper()
    answer = answer.upper()
    length = len(answer)

    result = ["grey"] * length
    answer_chars = list(answer)
    guess_chars = list(guess)


    for i in range(length):
        if guess_chars[i] == answer_chars[i]:
            result[i] = "green"
            answer_chars[i] = None
            guess_chars[i] = None

    
    for i in range(length):
        if guess_chars[i] is None:
            continue
        if guess_chars[i] in answer_chars:
            result[i] = "orange"
            answer_chars[answer_chars.index(guess_chars[i])] = None

    return result
