from wordle import Wordle, get_solutions, get_guesses, update_wordle

YELLOW = 'y'
GRAY = 'b'
GREEN = 'g'


def generate_answer_pattern(solution: str, guess: str) -> str:
    answer = ""
    for i, letter in enumerate(guess):
        if letter == solution[i]:
            answer += GREEN
        elif letter in solution:
            answer += YELLOW
        else:
            answer += GRAY
    return answer


if __name__ == "__main__":
    solutions, guesses = get_solutions('wordlist_solutions.txt'), get_guesses('wordlist_guesses.txt')
    with open('results.txt', 'r') as f:
        lines = f.readlines()
        num_processed = len(lines)
    for i, solution in enumerate(solutions[num_processed:]):
        wordl = Wordle(solutions=solutions, guesses=guesses)
        print(f"Processing {i+1+num_processed}/{len(solutions)}", end="\r")
        guess = 'roate'
        count = 1
        while guess != solution:
            result = generate_answer_pattern(solution, guess)
            update_wordle(wordl, guess, result)
            guess = wordl.get_optimal_guess_multiprocess()
            count += 1
        with open('results.txt', 'a') as f:
            f.write(f"{solution},{count}\n")
