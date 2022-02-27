from absl import flags
from absl import app

from collections import defaultdict, namedtuple
import copy
import multiprocessing as mp

YELLOW = 'y'
GRAY = 'b'
GREEN = 'g'


class Wordle:
    """Representation of wordle puzzle state and solution functionality."""

    # all possible solutions
    solutions = []

    # all possible guesses
    guesses = []

    def __init__(self, solutions: list[str] = None, guesses: list[str] = None, greens: list[str] = None, 
                 greens_not: dict[int, list[str]] = None, yellows: set[str] = None, grays: set[str] = None, hard_mode: bool = False):
        # list of 5 positions with either the correct letter or empty str
        if greens is None:
            self.greens = ['', '', '', '', '']
        else:
            self.greens = greens

        # map from position indices to letters we know are not there
        if greens_not is None:
            self.greens_not = defaultdict(list)
        else:
            self.greens_not = greens_not

        # letters that are confirmed to be in word
        if yellows is None:
            self.yellows = set()
        else: 
            self.yellows = yellows

        # letters that are confirmed not to be in word
        if grays is None:
            self.grays = set()
        else:
            self.grays = grays

        if solutions is not None:
            self.solutions = solutions
        if guesses is not None:
            self.guesses = guesses
        
        self.hard_mode = hard_mode
    

    def add_green(self, pos: int, c: str) -> None:
        # store info that letter c is at index pos
        self.greens[pos] = c
    

    def add_yellow(self, pos: int, c: str) -> None:
        # store info that letter c is in word
        self.yellows.add(c)
        # store info that letter c is not in position pos
        self.greens_not[pos].append(c)


    def add_gray(self, c: str) -> None:
        # store information that letter c is not in word
        self.grays.add(c)


    def add_grays(self, grays: list[str]) -> None:
        for gray in grays:
            self.grays.add(gray)


    def init_solutions(self, solutions: list[str]) -> None:
        self.solutions = solutions
    

    def init_guesses(self, guesses: list[str]) -> None:
        self.guesses = guesses
    

    def get_filtered_solutions(self) -> list[str]:
        words = []
        for solution in self.solutions:
            if self.greens_check(solution) and self.yellows_check(solution) and self.grays_check(solution) and self.greens_not_check(solution):
                words.append(solution)
        return words
    
    def get_guesses(self) -> list[str]:
        if not self.hard_mode:
            return self.guesses
        guesses: list[str] = []
        for guess in self.guesses:
            if self.greens_check(guess) and self.yellows_check(guess) and self.grays_check(guess) and self.greens_not_check(guess):
                guesses.append(guess)
        return guesses
    

    def greens_check(self, word: str) -> bool:
        for i, c in enumerate(self.greens):
            if c != '' and c != word[i]:
                return False
        return True


    def yellows_check(self, word: str) -> bool:
        for c in self.yellows:
            if c not in word:
                return False
        return True


    def grays_check(self, word: str) -> bool:
        for c in word:
            if c in self.grays and c not in self.yellows:
                return False
        return True


    def greens_not_check(self, word: str) -> bool:
        for i, c in enumerate(word):
            if c in self.greens_not[i]:
                return False
        return True
    

    def get_optimal_guess_process(self, process_id: int, solutions: list[str], filtered_solutions: list[str], return_dict: dict) -> None:
        """
        Process to run as a part of multiprocess optimal word search.
        """
        # dict from each guess to how many solutions it would leave remaining on average if guessed
        guess_to_rem = defaultdict(int)
        for i, sol in enumerate(solutions):
            for guess in self.get_guesses():
                    greens, greens_not, yellows, grays = self.greens.copy(), copy.deepcopy(self.greens_not), self.yellows.copy(), self.grays.copy()
                    sol_dict = dict()
                    for c in sol:
                        sol_dict[c] = True
                    for j, c in enumerate(guess):
                        # test for greens
                        if c == sol[j]:
                            greens[j] = c
                        else:
                            if c in sol_dict:
                                yellows.add(c)
                                greens_not[j].append(c)
                            else:
                                grays.add(c)
                        
                    test_wordle = Wordle(solutions=filtered_solutions, guesses=self.guesses, greens=greens, greens_not=greens_not, yellows=yellows, grays=grays)
                    # number of solutions that would remain if this guess were guessed and sol were the solution
                    num_sol_rem = len(test_wordle.get_filtered_solutions())
                    delta, weight = num_sol_rem - guess_to_rem[guess], i+1
                    # apply running average to guess dict
                    guess_to_rem[guess] += delta/weight
        return_dict[process_id] = guess_to_rem


    def get_optimal_guess_multiprocess(self, cores: int = 10) -> str:
        """
        Return the guess that eliminates the most solutions.
        Inputs:
            cores: the number of cores to use
        """
        filtered_solutions = self.get_filtered_solutions()
        if len(filtered_solutions) < 3:
            return filtered_solutions[0]
        
        group_size = len(filtered_solutions)//cores
        if group_size < 1:
            group_size = 1
        solution_sets = [filtered_solutions[i:i+group_size] for i in range(0, len(filtered_solutions), group_size)]
        set_weights = [len(sol_set)/len(filtered_solutions) for sol_set in solution_sets]

        processes: list[mp.Process] = []

        guess_to_rem = defaultdict(int)

        with mp.Manager() as manager:
            return_dict = manager.dict()
            for process_id, solution_set in enumerate(solution_sets):
                process = mp.Process(target=self.get_optimal_guess_process, args=(process_id, solution_set, filtered_solutions, return_dict))
                processes.append(process)
                process.start()
        
            for process in processes:
                process.join()

            for group_id, guess_to_rem_frag in return_dict.items():
                for guess, rem in guess_to_rem_frag.items():
                    guess_to_rem[guess] += rem * set_weights[group_id]
            
        # merge dictionary from each 
        # retrieve guess with minimum rem value
        min_rem = len(self.solutions)
        min_guess = self.guesses[0]
        for guess, rem in guess_to_rem.items():
            if rem < min_rem:
                min_guess, min_rem = guess, rem
        return min_guess


    def get_optimal_guess(self) -> str:
        """
        Return the guess that eliminates the most solutions.
        """
        filtered_solutions = self.get_filtered_solutions()
        if len(filtered_solutions) < 3:
            return filtered_solutions[0]
        # dict from each guess to how many solutions it would leave remaining on average if guessed
        guess_to_rem = defaultdict(int)
        
        for i, sol in enumerate(filtered_solutions):
            for guess in self.get_guesses:
                greens, greens_not, yellows, grays = self.greens.copy(), copy.deepcopy(self.greens_not), self.yellows.copy(), self.grays.copy()
                sol_dict = dict()
                for c in sol:
                    sol_dict[c] = True
                for j, c in enumerate(guess):
                    # test for greens
                    if c == sol[j]:
                        greens[j] = c
                    else:
                        if c in sol_dict:
                            yellows.add(c)
                            greens_not[j].append(c)
                        else:
                            grays.add(c)
                    
                test_wordle = Wordle(solutions=filtered_solutions, guesses=self.guesses, greens=greens, greens_not=greens_not, yellows=yellows, grays=grays)
                # number of solutions that would remain if this guess were guessed and sol were the solution
                num_sol_rem = len(test_wordle.get_filtered_solutions())
                delta, weight = num_sol_rem - guess_to_rem[guess], i+1
                # apply running average to guess dict
                guess_to_rem[guess] += delta/weight
        # retrieve guess with minimum rem value
        min_rem = len(self.solutions)
        min_guess = self.guesses[0]
        for guess, rem in guess_to_rem.items():
            if rem < min_rem:
                min_guess, min_rem = guess, rem
        return min_guess


def get_solutions(filename: str) -> list[str]:
    solutions = []
    with open(filename, 'r') as f:
        for line in f:
            word = line.replace('\n', '').strip().lower()
            solutions.append(word)
    return solutions


def get_guesses(filename: str) -> list[str]:
    guesses = []
    with open(filename, 'r') as f:
        for line in f:
            word = line.replace('\n', '').strip().lower()
            guesses.append(word)
    return guesses


def check_guess_error(guesses: list[str], guess: str) -> tuple[bool, str]:
    '''Returns True if there is error in guess.'''
    if len(guess) != 5:
        return True, "Guess needs to be of length 5."
    if guess not in guesses:
        return True, "This guess is not a valid word"
    return False, ''


def check_result_error(result: str) -> tuple[bool, str]:
    '''Returns True if there is error in result format.'''
    if len(result) != 5:
        return True, "Result needs to be of length 5."
    for c in result:
        if c not in ['y', 'b', 'g']:
            return True, "Only y, b, and g are valid inputs."
    return False, ''


def update_wordle(wordle: Wordle, word: str, result: str) -> None:
    # letter to color dict
    for i, letter in enumerate(word):
        color = result[i]
        if color == GREEN:
            wordle.add_green(i, letter)
        elif color == YELLOW:
            wordle.add_yellow(i, letter)
        else:
            wordle.add_gray(letter)


FLAGS = flags.FLAGS
flags.DEFINE_boolean('hardmode', False, 'Whether to run using hard mode.')

def main(_):
    solutions, guesses = get_solutions('wordlist_solutions.txt'), get_guesses('wordlist_guesses.txt')
    wordle = Wordle(solutions=solutions, guesses=guesses, hard_mode=FLAGS.hardmode)

    err = True
    while err:
        # Optimal first guesses: roate, raise
        first_guess = input('Input your first guess: ')
        err, explanation = check_guess_error(guesses, first_guess)
        if err:
            print(explanation)
    
    err = True
    while err:
        result = input('Input the result pattern (e.g. ybgbb): ')
        err, explanation = check_result_error(result)
        if err:
            print(explanation)

    update_wordle(wordle, first_guess, result)
    
    while len(wordle.get_filtered_solutions()) > 1:
        # guess = wordle.get_optimal_guess()
        guess = wordle.get_optimal_guess_multiprocess()
        print(f"Your next guess should be {guess}")
        err = True
        while err:
            result = input('Input the result pattern (e.g. ybgbb): ')
            err, explanation = check_result_error(result)
            if err:
                print(explanation)

        update_wordle(wordle, guess, result)
    print(f"The answer is {wordle.get_filtered_solutions()[0]}")
    
if __name__ == "__main__":
    app.run(main)
