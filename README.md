# Setup
- Requires python version 3.5^
- Run `pip3 install -r requirements.txt` to install python requirements
# To run the solver
This bot comes with a solver implementation that you can use "out of the box".
```sh
python3 wordle.py
```
Use the hardmode flag to solve using hard mode
```sh
python3 wordle.py --hardmode
```
## Instructions
The solver starts by asking you for a first guess.

`Input your first guess: raise`

Then it will ask you for the result pattern that you see.

`Input the result pattern (e.g. ybgbb): yybyb`

y => yellow, b => gray, g => green

Then, the solver will give you the optimal next guess.

`Your next guess should be clapt`

Repeat this process until the solver comes up with the solution.

```sh
Input your first guess: raise
Input the result pattern (e.g. ybgbb): yybyb
Your next guess should be clapt
Input the result pattern (e.g. ybgbb): ybybb        
The answer is scram
```

# To use the bot directly
```python
# Import the wordle class into your code to use the bot.
from wordle import Wordle

# Initialize lists of strings which represent possible solutions and guesses
solutions, guesses = [], [] # Init custom solutions and guesses

# To use solutions and guesses used by main wordle site, you can use functions from wordle.py
from wordle import get_solutions, get_guesses
solutions = get_solutions('wordlist_solutions.txt')
guesses = get_guesses('wordlist_guesses.txt')

# Create an instance of the wordle bot by providing possible solutions and guesses
bot = Wordle(solutions=solutions, guesses=guesses, hard_mode=False)

# After you have made a guess, enter the pattern into the wordle bot
# Example: "raise" entered, result pattern: gray, yellow, gray, gray, green
bot.add_gray('r')
# Add the index of the yellow letter, followed by the letter
bot.add_yellow(1, 'a')
bot.add_gray('i')
bot.add_gray('s')
# Add the index of the green letter, followed by the letter
bot.add_green(4, 'e')

# Get the remaining possible solutions
remaining_solutions = bot.get_filtered_solutions()

# Get the next optimal guess
optimal_guess = bot.get_optimal_guess()

# You can make this function run faster by using multiple cores
optimal_guess = bot.get_optimal_guess_multiprocess(cores=10)
```