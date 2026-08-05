"""AXE v1 task bank — hand-written, contamination-screened problems.

Three categories, two tracks:
- AXE        standard suite (general / coding / reasoning)
- AXE-Pro    adversarial subset, deliberately outside the easy distribution

Every coding task ships with an exact expected output plus a list of inputs
that must appear in the submitted code; scoring extracts the last fenced
python block and executes it.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Task:
    prompt: str
    answer: str
    category: str  # general | coding | reasoning
    pro: bool = False
    kind: str = "exact"  # exact | contains | code
    code_checks: tuple[str, ...] = field(default=(), repr=False)
    aliases: tuple[str, ...] = ()
    test_call: str = ""  # coding tasks: expression evaluated against the submitted function


GENERAL = [
    Task("What is the capital of Australia?", "canberra", "general"),
    Task("Which planet in our solar system has the most confirmed moons?", "saturn", "general"),
    Task("Who wrote the novel 'One Hundred Years of Solitude'?", "gabriel garcia marquez", "general", aliases=("marquez",)),
    Task("What year did the Berlin Wall fall?", "1989", "general"),
    Task("Which metal is liquid at room temperature?", "mercury", "general"),
    Task("Who composed 'The Rite of Spring'?", "stravinsky", "general", aliases=("igor stravinsky",)),
    Task("What is the largest ocean on Earth?", "pacific", "general"),
    Task("Who painted 'The Persistence of Memory', the painting with the melting clocks?", "dali", "general", aliases=("salvador dali",)),
    Task("Which blood type is known as the universal donor?", "o negative", "general", aliases=("o-",)),
    Task("What year did the Titanic sink?", "1912", "general"),
    Task("Who wrote 'The Odyssey'?", "homer", "general"),
    Task("What is the chemical symbol for gold?", "au", "general"),
    Task("Which country has the most time zones, including its territories?", "france", "general"),
    Task("In what year did the Chernobyl disaster occur?", "1986", "general"),
    Task("Who discovered penicillin?", "fleming", "general", aliases=("alexander fleming",)),
    Task("What is the capital of Canada?", "ottawa", "general"),
    Task("Which gas makes up the majority of Earth's atmosphere?", "nitrogen", "general"),
    Task("Who composed the opera 'The Magic Flute'?", "mozart", "general", aliases=("wolfgang amadeus mozart",)),
    Task("What is the longest river in South America?", "amazon", "general"),
    Task("In Greek mythology, who flew too close to the sun?", "icarus", "general"),
    # Pro subset — deliberately obscure.
    Task("Who was the 13th President of the United States?", "millard fillmore", "general", pro=True),
    Task("Who wrote the ancient Sanskrit treatise 'Arthashastra'?", "kautilya", "general", pro=True, aliases=("chanakya", "vishnugupta")),
    Task("The Antikythera mechanism is believed to have originated in which ancient civilization?", "greek", "general", pro=True, aliases=("ancient greece", "greece")),
    Task("Which city served as the capital of the Byzantine Empire?", "constantinople", "general", pro=True),
    Task("What element has the atomic number 51?", "antimony", "general", pro=True),
    Task("Who wrote the novel 'Gravity's Rainbow'?", "thomas pynchon", "general", pro=True, aliases=("pynchon",)),
    Task("What treaty ended the Thirty Years' War in 1648?", "peace of westphalia", "general", pro=True, aliases=("westphalia",)),
    Task("Which mathematician proved that there are infinitely many prime numbers?", "euclid", "general", pro=True),
    Task("Which ancient civilization built the city of Great Zimbabwe?", "shona", "general", pro=True, aliases=("shona people")),
    Task("Who painted 'The Garden of Earthly Delights'?", "bosch", "general", pro=True, aliases=("hieronymus bosch")),
]

CODING = [
    Task(
        "Write a Python function `count_words(s)` that takes a string, splits on whitespace, and returns a dictionary mapping each lowercased word to its count. Include the function definition only, no example usage.",
        "{'the': 2, 'dog': 1, 'ran': 1}",
        "coding",
        code_checks=("def count_words",),
        test_call="count_words('the the dog ran')",
    ),
    Task(
        "Write a Python function `fizzbuzz(n)` that returns a list of strings for 1 through n: 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, 'FizzBuzz' for multiples of both, otherwise the number as a string. Function definition only.",
        "['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']",
        "coding",
        code_checks=("def fizzbuzz",),
        test_call="fizzbuzz(15)",
    ),
    Task(
        "Write a Python function `is_palindrome(s)` that returns True if the string s is a palindrome when considering only alphanumeric characters, ignoring case. Function definition only.",
        "True",
        "coding",
        code_checks=("def is_palindrome",),
        test_call="is_palindrome('A man, a plan, a canal: Panama')",
    ),
    Task(
        "Write a Python function `fib(n)` that returns the nth Fibonacci number, with fib(0)=0 and fib(1)=1. Function definition only.",
        "55",
        "coding",
        code_checks=("def fib",),
        test_call="fib(10)",
    ),
    Task(
        "Write a Python function `flatten(lst)` that flattens an arbitrarily nested list into a single list, preserving order. Function definition only.",
        "[1, 2, 3, 4, 5]",
        "coding",
        code_checks=("def flatten",),
        test_call="flatten([1, [2, [3]], 4, [5]])",
    ),
    Task(
        "Write a Python function `run_length(s)` that returns the run-length encoding of string s as a list of (character, count) tuples, in order of first appearance. Function definition only.",
        "[('a', 3), ('b', 1), ('a', 2)]",
        "coding",
        code_checks=("def run_length",),
        test_call="run_length('aaabaa')",
    ),
    Task(
        "Write a Python function `merge_dicts(a, b)` that merges two dictionaries, summing the values of keys that appear in both. Function definition only.",
        "{'a': 3, 'b': 7, 'c': 5}",
        "coding",
        code_checks=("def merge_dicts",),
        test_call="merge_dicts({'a': 3, 'b': 3}, {'b': 4, 'c': 5})",
    ),
    Task(
        "Write a Python function `reverse_words(s)` that reverses the order of words in a string while keeping each word intact, collapsing extra spaces. Function definition only.",
        "world hello",
        "coding",
        code_checks=("def reverse_words",),
        test_call="reverse_words('hello world')",
    ),
    Task(
        "Write a Python function `median(nums)` that returns the median of a non-empty list of numbers. Function definition only.",
        "3",
        "coding",
        code_checks=("def median",),
        test_call="median([1, 3, 5])",
    ),
    Task(
        "Write a Python function `title_case(s)` that capitalizes the first letter of every word in the string. Function definition only.",
        "Hello Brave New World",
        "coding",
        code_checks=("def title_case",),
        test_call="title_case('hello brave new world')",
    ),
    Task(
        "Write a Python function `chunk(lst, n)` that splits a list into chunks of size n, with the last chunk possibly smaller. Function definition only.",
        "[[1, 2], [3, 4], [5]]",
        "coding",
        code_checks=("def chunk",),
        test_call="chunk([1, 2, 3, 4, 5], 2)",
    ),
    Task(
        "Write a Python function `factorial(n)` that returns the factorial of n for n >= 0. Function definition only.",
        "120",
        "coding",
        code_checks=("def factorial",),
        test_call="factorial(5)",
    ),
    Task(
        "Write a Python function `most_common(lst)` that returns the element that appears most often in the list. Break ties however you like. Function definition only.",
        "2",
        "coding",
        code_checks=("def most_common",),
        test_call="most_common([1, 2, 2, 3])",
    ),
    Task(
        "Write a Python function `dedupe(lst)` that returns the list with duplicates removed, preserving the first occurrence order. Function definition only.",
        "[1, 2, 3, 4]",
        "coding",
        code_checks=("def dedupe",),
        test_call="dedupe([1, 2, 2, 3, 1, 4])",
    ),
    Task(
        "Write a Python function `gcd(a, b)` that returns the greatest common divisor of two positive integers using the Euclidean algorithm. Function definition only.",
        "6",
        "coding",
        code_checks=("def gcd",),
        test_call="gcd(12, 18)",
    ),
    # Pro subset — edge cases that punish pattern-matching.
    Task(
        "Write a Python function `dedupe(lst)` that returns the list with duplicates removed, preserving the first occurrence order. The list may contain unhashable items such as nested lists. Function definition only.",
        "[[1, 2], [3], [1, 2], [4]]",
        "coding",
        pro=True,
        code_checks=("def dedupe",),
        test_call="dedupe([[1, 2], [3], [1, 2], [4]])",
    ),
    Task(
        "Write a Python function `median(nums)` that returns the median of a list. The list may contain an even number of elements — return the lower median in that case. Function definition only.",
        "3",
        "coding",
        pro=True,
        code_checks=("def median",),
        test_call="median([4, 1, 3, 2, 5, 6])",
    ),
    Task(
        "Write a Python function `flatten(lst)` that flattens an arbitrarily nested list into a single list, preserving order. Nested lists can be empty and nesting can be deep. Function definition only.",
        "[1, 2, 3, 4]",
        "coding",
        pro=True,
        code_checks=("def flatten",),
        test_call="flatten([1, [], [2, [3, []]], 4])",
    ),
    Task(
        "Write a Python function `count_words(s)` that takes a string and returns a dictionary mapping each word to its count. Words are separated by whitespace; strip surrounding punctuation (.,!?;:) from each word before counting; treat empty results as absent. Function definition only.",
        "{'hello': 2, 'world': 1}",
        "coding",
        pro=True,
        code_checks=("def count_words",),
        test_call="count_words('hello, hello world!')",
    ),
    Task(
        "Write a Python function `run_length(s)` that returns the run-length encoding of string s as a list of (character, count) tuples. An empty string returns an empty list. Function definition only.",
        "[('a', 2), ('b', 2), ('c', 1)]",
        "coding",
        pro=True,
        code_checks=("def run_length",),
        test_call="run_length('aabbc')",
    ),
]

REASONING = [
    Task("What is 17 times 23? Answer with just the number.", "391", "reasoning"),
    Task("A shirt costs $40 and is discounted by 25%. What is the sale price in dollars? Answer with just the number.", "30", "reasoning"),
    Task("Solve for x: 3x + 5 = 20. Answer with just the number.", "5", "reasoning"),
    Task("How many seconds are in one day? Answer with just the number.", "86400", "reasoning"),
    Task("What is the sum of the first 10 positive integers? Answer with just the number.", "55", "reasoning"),
    Task("If today is Monday, what day of the week is it exactly 100 days from now? Answer with just the day name.", "wednesday", "reasoning"),
    Task("How many days are in a leap year? Answer with just the number.", "366", "reasoning"),
    Task("A train travels at 60 miles per hour for 2.5 hours. How far does it go in miles? Answer with just the number.", "150", "reasoning"),
    Task("What is 2 to the power of 10? Answer with just the number.", "1024", "reasoning"),
    Task("What is the next number in the sequence 2, 6, 18, 54, ...? Answer with just the number.", "162", "reasoning"),
    Task("What is the square root of 144? Answer with just the number.", "12", "reasoning"),
    Task("If 5 machines take 5 minutes to make 5 widgets, how many minutes do 100 machines take to make 100 widgets? Answer with just the number.", "5", "reasoning"),
    Task("What is 15% of 200? Answer with just the number.", "30", "reasoning"),
    Task("The average of four numbers is 12. Three of them are 10, 14, and 16. What is the fourth number? Answer with just the number.", "8", "reasoning"),
    Task("How many minutes are in one week? Answer with just the number.", "10080", "reasoning"),
    # Pro subset — multi-step traps.
    Task("If 3 cats catch 3 mice in 3 minutes, how many cats are needed to catch 100 mice in 100 minutes? Answer with just the number.", "3", "reasoning", pro=True),
    Task("A clock strikes 6 times at 6 o'clock. The interval between strikes is uniform, and 6 strikes take 10 seconds from first to last. How many seconds do 12 strikes take? Answer with just the number.", "22", "reasoning", pro=True),
    Task("What is the sum of all odd numbers from 1 to 19 inclusive? Answer with just the number.", "100", "reasoning", pro=True),
    Task("If you fold a standard sheet of paper in half 6 times, how many layers thick is it? Answer with just the number.", "64", "reasoning", pro=True),
    Task("A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How many cents does the ball cost? Answer with just the number.", "5", "reasoning", pro=True),
]

TASKS = GENERAL + CODING + REASONING


def select(category: str | None = None, pro: bool | None = None) -> list[Task]:
    out = []
    for task in TASKS:
        if category and task.category != category:
            continue
        if pro is not None and task.pro != pro:
            continue
        out.append(task)
    return out
