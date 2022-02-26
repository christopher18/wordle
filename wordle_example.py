import wordle
from wordle import Wordle
import datetime

if __name__ == "__main__":
    solutions, guesses = wordle.get_solutions('wordlist_solutions.txt'), wordle.get_guesses('wordlist_guesses.txt')
    wordle = Wordle(solutions=solutions, guesses=guesses)
    wordle.add_gray('r')
    wordle.add_yellow(1, 'a')
    wordle.add_gray('i')
    wordle.add_gray('s')
    wordle.add_green(4, 'e')

    print(wordle.get_optimal_guess_multiprocess(10))

    wordle.add_green(0, 'b')
    wordle.add_green(1, 'l')
    wordle.add_green(2, 'a')
    wordle.add_gray('c')
    wordle.add_gray('k')

    print(wordle.get_optimal_guess_multiprocess(10))

    wordle.add_yellow(0, 'm')
    wordle.add_gray('o')
    wordle.add_gray('d')
    wordle.add_yellow(3, 'e')
    wordle.add_yellow(4, 'l')

    print(wordle.get_optimal_guess_multiprocess(10))