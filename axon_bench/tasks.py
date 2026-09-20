"""Hand-written task bank for AXE and AXE-Pro.

170 contamination-screened tasks (65 general, 56 coding,
49 reasoning), of which 43 form the AXE-Pro adversarial subset.
Coding prompts ask for a single function (or, for TypeScript/SQL, a
self-contained snippet) so the harness can execute or construct-check the
submission — there is no prose to argue with.  `SOLUTIONS` holds the
reference implementation for every executable coding task; the self-check
in test_axe.py runs each `test_call` against it, so expected answers
cannot drift from reality.
"""

from __future__ import annotations

from dataclasses import dataclass, field

CATEGORIES = ("general", "coding", "reasoning")


@dataclass(frozen=True)
class Task:
    """One benchmark item.

    prompt — shown to the model; never leaks the answer.
    answer — canonical expected result: lowercase for text tasks, repr() of
        the test call's output for executed coding tasks, an illustrative
        string for construct-checked TypeScript/SQL tasks.
    category — general | coding | reasoning.
    pro — belongs to the adversarial AXE-Pro track.
    kind — exact | contains | code.  Text tasks default to exact whole-token
        matching; `code` tasks are executed or construct-checked.
    code_checks — substrings the submitted code must contain (matched
        case-insensitively by the runner).
    aliases — extra acceptable exact-match answers.
    test_call — expression evaluated against the submitted function; the
        task passes iff repr() of its result equals `answer`.
    """

    prompt: str
    answer: str
    category: str
    pro: bool = False
    kind: str = "exact"  # exact | contains | code
    code_checks: tuple[str, ...] = field(default=(), repr=False)
    aliases: tuple[str, ...] = ()
    test_call: str = ""


GENERAL = (
    # ---- general knowledge ---
    # ---- standard -----------------------------------------
    Task('What is the capital of Australia?', 'canberra', 'general'),
    Task('Which planet in our solar system has the most confirmed moons?', 'saturn', 'general'),
    Task("Who wrote the novel 'One Hundred Years of Solitude'?", 'gabriel garcia marquez', 'general', aliases=('marquez',)),
    Task('What year did the Berlin Wall fall?', '1989', 'general'),
    Task('Which metal is liquid at room temperature?', 'mercury', 'general'),
    Task("Who composed 'The Rite of Spring'?", 'stravinsky', 'general', aliases=('igor stravinsky',)),
    Task('What is the largest ocean on Earth?', 'pacific', 'general'),
    Task("Who painted 'The Persistence of Memory', the painting with the melting clocks?", 'dali', 'general', aliases=('salvador dali',)),
    Task('Which blood type is known as the universal donor?', 'o negative', 'general', aliases=('o-',)),
    Task('What year did the Titanic sink?', '1912', 'general'),
    Task("Who wrote 'The Odyssey'?", 'homer', 'general'),
    Task('What is the chemical symbol for gold?', 'au', 'general'),
    Task('Which country has the most time zones, including its territories?', 'france', 'general'),
    Task('In what year did the Chernobyl disaster occur?', '1986', 'general'),
    Task('Who discovered penicillin?', 'fleming', 'general', aliases=('alexander fleming',)),
    Task('What is the capital of Canada?', 'ottawa', 'general'),
    Task("Which gas makes up the majority of Earth's atmosphere?", 'nitrogen', 'general'),
    Task("Who composed the opera 'The Magic Flute'?", 'mozart', 'general', aliases=('wolfgang amadeus mozart',)),
    Task('What is the longest river in South America?', 'amazon', 'general'),
    Task('In Greek mythology, who flew too close to the sun?', 'icarus', 'general'),
    Task('Which country gifted the Statue of Liberty to the United States?', 'france', 'general'),
    Task('What is the smallest country in the world by land area?', 'vatican city', 'general', aliases=('vatican', 'holy see')),
    Task('In which modern city would you find the Hagia Sophia?', 'istanbul', 'general'),
    Task('What is the hardest naturally occurring mineral?', 'diamond', 'general'),
    Task('How many strings does a standard violin have?', '4', 'general', aliases=('four',)),
    Task('Which vitamin does human skin synthesise when exposed to sunlight?', 'vitamin d', 'general'),
    Task('Which planet is nicknamed the Red Planet?', 'mars', 'general'),
    Task('What is the official currency of Japan?', 'yen', 'general', aliases=('japanese yen',)),
    Task('Mount Kilimanjaro rises in which country?', 'tanzania', 'general'),
    Task("Who wrote the 1879 play 'A Doll's House'?", 'ibsen', 'general', aliases=('henrik ibsen',)),
    Task('Including cold deserts, what is the largest desert on Earth?', 'antarctica', 'general', aliases=('antarctic desert', 'the antarctic desert')),
    Task('The Dead Sea borders Israel and which other country?', 'jordan', 'general'),
    Task('How many keys does a standard full-size piano have?', '88', 'general'),
    Task('Which astronomer published laws of planetary motion in 1609?', 'kepler', 'general', aliases=('johannes kepler',)),
    Task('Which gas do plants absorb from the air for photosynthesis?', 'carbon dioxide', 'general', aliases=('co2',)),
    Task('In which year was the first human heart transplant performed?', '1967', 'general'),
    Task('Which is the only mammal capable of true, sustained flight?', 'bat', 'general'),
    Task('What is the capital of Brazil?', 'brasilia', 'general'),
    Task('Which language has the most native speakers in the world?', 'mandarin', 'general', aliases=('mandarin chinese', 'standard chinese', 'chinese')),
    Task('What is the scientific study of earthquakes called?', 'seismology', 'general'),
    Task('Who was the first woman to win a Nobel Prize?', 'marie curie', 'general', aliases=('curie', 'madame curie')),
    Task('The Great Barrier Reef lies off the coast of which country?', 'australia', 'general'),
    Task('What is the second-tallest mountain on Earth?', 'k2', 'general', aliases=('mount godwin austen', 'qogir')),
    Task('Which country spans both Europe and Asia across the Bosphorus?', 'turkey', 'general', aliases=('turkiye',)),
    Task('Which planet rotates on its side, with an axial tilt near 98 degrees?', 'uranus', 'general'),
    Task('Which bird is famous for being able to fly backwards?', 'hummingbird', 'general'),
    # ---- AXE-Pro ------------------------------------------
    Task('Who was the 13th President of the United States?', 'millard fillmore', 'general', pro=True),
    Task("Who wrote the ancient Sanskrit treatise 'Arthashastra'?", 'kautilya', 'general', pro=True, aliases=('chanakya', 'vishnugupta')),
    Task('The Antikythera mechanism is believed to have originated in which ancient civilization?', 'greek', 'general', pro=True, aliases=('ancient greece', 'greece')),
    Task('Which city served as the capital of the Byzantine Empire?', 'constantinople', 'general', pro=True),
    Task('What element has the atomic number 51?', 'antimony', 'general', pro=True),
    Task("Who wrote the novel 'Gravity's Rainbow'?", 'thomas pynchon', 'general', pro=True, aliases=('pynchon',)),
    Task("What treaty ended the Thirty Years' War in 1648?", 'peace of westphalia', 'general', pro=True, aliases=('westphalia',)),
    Task('Which mathematician proved that there are infinitely many prime numbers?', 'euclid', 'general', pro=True),
    Task('Which ancient civilization built the city of Great Zimbabwe?', 'shona', 'general', pro=True, aliases=('shona people',)),
    Task("Who painted 'The Garden of Earthly Delights'?", 'bosch', 'general', pro=True, aliases=('hieronymus bosch',)),
    Task("Which chemical element takes its name from the Greek word for 'lazy', because it hardly reacts?", 'argon', 'general', pro=True),
    Task('Who received the first Turing Award, in 1966?', 'alan perlis', 'general', pro=True, aliases=('perlis', 'alan j perlis')),
    Task("Which 14th-century Moroccan traveller wrote the 'Rihla' after journeying some 120,000 km?", 'ibn battuta', 'general', pro=True, aliases=('battuta',)),
    Task("What is the deepest known point in Earth's oceans called?", 'challenger deep', 'general', pro=True, aliases=('mariana trench', 'marianas trench')),
    Task('Which letter of the English alphabet appears in no US state name?', 'q', 'general', pro=True),
    Task('Which of the seven ancient wonders stood in the harbour of Alexandria?', 'lighthouse of alexandria', 'general', pro=True, aliases=('pharos', 'pharos of alexandria', 'lighthouse at alexandria')),
    Task('In Norse mythology, what is the rainbow bridge between Earth and Asgard called?', 'bifrost', 'general', pro=True, aliases=('bifrost bridge',)),
    Task('What is the only US state whose name has just one syllable?', 'maine', 'general', pro=True),
    Task("Which country's national flag is the world's only non-quadrilateral flag?", 'nepal', 'general', pro=True),
)

CODING = (
    # ---- coding ---
    # ---- standard -----------------------------------------
    Task('Write a Python function `count_words(s)` that takes a string, splits on whitespace, and returns a dictionary mapping each lowercased word to its count. Include the function definition only, no example usage.', "{'the': 2, 'dog': 1, 'ran': 1}", 'coding', code_checks=('def count_words',), test_call="count_words('the the dog ran')"),
    Task("Write a Python function `fizzbuzz(n)` that returns a list of strings for 1 through n: 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, 'FizzBuzz' for multiples of both, otherwise the number as a string. Function definition only.", "['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']", 'coding', code_checks=('def fizzbuzz',), test_call='fizzbuzz(15)'),
    Task('Write a Python function `is_palindrome(s)` that returns True if the string s is a palindrome when considering only alphanumeric characters, ignoring case. Function definition only.', 'True', 'coding', code_checks=('def is_palindrome',), test_call="is_palindrome('A man, a plan, a canal: Panama')"),
    Task('Write a Python function `fib(n)` that returns the nth Fibonacci number, with fib(0)=0 and fib(1)=1. Function definition only.', '55', 'coding', code_checks=('def fib',), test_call='fib(10)'),
    Task('Write a Python function `flatten(lst)` that flattens an arbitrarily nested list into a single list, preserving order. Function definition only.', '[1, 2, 3, 4, 5]', 'coding', code_checks=('def flatten',), test_call='flatten([1, [2, [3]], 4, [5]])'),
    Task('Write a Python function `run_length(s)` that returns the run-length encoding of string s as a list of (character, count) tuples, in order of first appearance. Function definition only.', "[('a', 3), ('b', 1), ('a', 2)]", 'coding', code_checks=('def run_length',), test_call="run_length('aaabaa')"),
    Task('Write a Python function `merge_dicts(a, b)` that merges two dictionaries, summing the values of keys that appear in both. Function definition only.', "{'a': 3, 'b': 7, 'c': 5}", 'coding', code_checks=('def merge_dicts',), test_call="merge_dicts({'a': 3, 'b': 3}, {'b': 4, 'c': 5})"),
    Task('Write a Python function `reverse_words(s)` that reverses the order of words in a string while keeping each word intact, collapsing extra spaces. Function definition only.', "'world hello'", 'coding', code_checks=('def reverse_words',), test_call="reverse_words('hello world')"),
    Task('Write a Python function `median(nums)` that returns the median of a non-empty list of numbers. Function definition only.', '3', 'coding', code_checks=('def median',), test_call='median([1, 3, 5])'),
    Task('Write a Python function `title_case(s)` that capitalizes the first letter of every word in the string. Function definition only.', "'Hello Brave New World'", 'coding', code_checks=('def title_case',), test_call="title_case('hello brave new world')"),
    Task('Write a Python function `chunk(lst, n)` that splits a list into chunks of size n, with the last chunk possibly smaller. Function definition only.', '[[1, 2], [3, 4], [5]]', 'coding', code_checks=('def chunk',), test_call='chunk([1, 2, 3, 4, 5], 2)'),
    Task('Write a Python function `factorial(n)` that returns the factorial of n for n >= 0. Function definition only.', '120', 'coding', code_checks=('def factorial',), test_call='factorial(5)'),
    Task('Write a Python function `most_common(lst)` that returns the element that appears most often in the list. Break ties however you like. Function definition only.', '2', 'coding', code_checks=('def most_common',), test_call='most_common([1, 2, 2, 3])'),
    Task('Write a Python function `dedupe(lst)` that returns the list with duplicates removed, preserving the first occurrence order. Function definition only.', '[1, 2, 3, 4]', 'coding', code_checks=('def dedupe',), test_call='dedupe([1, 2, 2, 3, 1, 4])'),
    Task('Write a Python function `gcd(a, b)` that returns the greatest common divisor of two positive integers using the Euclidean algorithm. Function definition only.', '6', 'coding', code_checks=('def gcd',), test_call='gcd(12, 18)'),
    Task("Write a Python function `slugify(text)` that lowercases text and replaces every run of non-alphanumeric characters with a single hyphen, stripping leading and trailing hyphens. Call it like `slugify('Hello, World! 2024')`.", "'hello-world-2024'", 'coding', kind='code', code_checks=('def slugify',), test_call="slugify('Hello, World! 2024')"),
    Task('Write a Python function `roman(n)` that converts an integer between 1 and 3999 into its Roman numeral string. Call it like `roman(1994)`.', "'MCMXCIV'", 'coding', kind='code', code_checks=('def roman',), test_call='roman(1994)'),
    Task("Write a Python function `parse_ranges(spec)` that expands a string like '1-3,5' into the list of all integers it covers. Call it like `parse_ranges('1-3,5')`.", '[1, 2, 3, 5]', 'coding', kind='code', code_checks=('def parse_ranges',), test_call="parse_ranges('1-3,5')"),
    Task("Write a Python function `is_anagram(a, b)` returning True when the two strings contain exactly the same letters, ignoring case, spaces and punctuation. Call it like `is_anagram('Listen', 'Silent')`.", 'True', 'coding', kind='code', code_checks=('def is_anagram',), test_call="is_anagram('Listen', 'Silent')"),
    Task('Write a Python function `transpose(matrix)` that returns the transpose of a rectangular matrix. Call it like `transpose([[1, 2], [3, 4]])`.', '[[1, 3], [2, 4]]', 'coding', kind='code', code_checks=('def transpose',), test_call='transpose([[1, 2], [3, 4]])'),
    Task("Write a Python function `caesar_shift(text, k)` that shifts every letter k positions through the alphabet, preserving case and leaving other characters alone. Call it like `caesar_shift('Abc', 1)`.", "'Bcd'", 'coding', kind='code', code_checks=('def caesar_shift',), test_call="caesar_shift('Abc', 1)"),
    Task('Write a Python function `binary_search_index(items, target)` returning the index of target in a sorted list, or -1 if absent. Call it like `binary_search_index([1, 3, 5, 7], 5)`.', '2', 'coding', kind='code', code_checks=('def binary_search_index',), test_call='binary_search_index([1, 3, 5, 7], 5)'),
    Task("Write a Python function `pascal_row(n)` returning row n (0-indexed) of Pascal's triangle. Call it like `pascal_row(4)`.", '[1, 4, 6, 4, 1]', 'coding', kind='code', code_checks=('def pascal_row',), test_call='pascal_row(4)'),
    Task('Write a Python function `dot(a, b)` returning the dot product of two equal-length vectors. Call it like `dot([1, 2, 3], [4, 5, 6])`.', '32', 'coding', kind='code', code_checks=('def dot',), test_call='dot([1, 2, 3], [4, 5, 6])'),
    Task("Write a Python function `balanced(text)` returning True when the brackets (), [] and {} in the string are correctly matched and nested. Call it like `balanced('([{}])')`.", 'True', 'coding', kind='code', code_checks=('def balanced',), test_call="balanced('([{}])')"),
    Task('Write a Python function `top_k(items, k)` returning the k largest values in descending order. Call it like `top_k([4, 1, 7, 3], 2)`.', '[7, 4]', 'coding', kind='code', code_checks=('def top_k',), test_call='top_k([4, 1, 7, 3], 2)'),
    Task('Write a Python function `is_prime(n)` returning True when n is a prime number. Call it like `is_prime(97)`.', 'True', 'coding', kind='code', code_checks=('def is_prime',), test_call='is_prime(97)'),
    Task('Write a Python function `collatz_len(n)` returning the number of steps for n to reach 1 under Collatz rules (halve if even, otherwise triple and add one). Call it like `collatz_len(27)`.', '111', 'coding', kind='code', code_checks=('def collatz_len',), test_call='collatz_len(27)'),
    Task('Write a Python function `rotate_matrix(matrix)` that rotates a square matrix 90 degrees clockwise. Call it like `rotate_matrix([[1, 2], [3, 4]])`.', '[[3, 1], [4, 2]]', 'coding', kind='code', code_checks=('def rotate_matrix',), test_call='rotate_matrix([[1, 2], [3, 4]])'),
    Task('Write a Python function `bst_preorder(values)` that inserts the values into a binary search tree in order and returns the preorder traversal. Call it like `bst_preorder([10, 5, 20, 3, 8])`.', '[10, 5, 3, 8, 20]', 'coding', kind='code', code_checks=('def bst_preorder',), test_call='bst_preorder([10, 5, 20, 3, 8])'),
    Task('Write a Python function `kth_smallest(items, k)` returning the k-th smallest value (1-indexed). Call it like `kth_smallest([7, 10, 4, 3, 20, 15], 3)`.', '7', 'coding', kind='code', code_checks=('def kth_smallest',), test_call='kth_smallest([7, 10, 4, 3, 20, 15], 3)'),
    Task("Write a Python function `lcs_len(a, b)` returning the length of the longest common subsequence of two strings. Call it like `lcs_len('stone', 'longest')`.", '3', 'coding', kind='code', code_checks=('def lcs_len',), test_call="lcs_len('stone', 'longest')"),
    Task("Write a Python function `edit_distance(a, b)` returning the minimum number of single-character edits (insert, delete, replace) needed to turn a into b. Call it like `edit_distance('kitten', 'sitting')`.", '3', 'coding', kind='code', code_checks=('def edit_distance',), test_call="edit_distance('kitten', 'sitting')"),
    Task('Write a Python function `count_islands(grid)` returning the number of connected groups of 1s in a binary grid, connected horizontally or vertically. Call it like `count_islands([[1, 1, 0], [0, 1, 0], [0, 0, 1]])`.', '2', 'coding', kind='code', code_checks=('def count_islands',), test_call='count_islands([[1, 1, 0], [0, 1, 0], [0, 0, 1]])'),
    Task('Write a Python function `zero_sum_triplets(items)` returning all unique triplets that sum to 0, as sorted tuples in sorted order. Call it like `zero_sum_triplets([-1, 0, 1, 2, -1, -4])`.', '[(-1, -1, 2), (-1, 0, 1)]', 'coding', kind='code', code_checks=('def zero_sum_triplets',), test_call='zero_sum_triplets([-1, 0, 1, 2, -1, -4])'),
    Task("Write a TypeScript function `formatDuration(totalSeconds: number): string` that formats a non-negative number of seconds as zero-padded 'HH:MM:SS', e.g. formatDuration(3909) === '01:05:09'. Return only the code in a typescript block.", '01:05:09', 'coding', kind='code', code_checks=('function formatDuration', ': number', ': string')),
    Task("Write a TypeScript function `greetUser(name: string, visits: number): string` that returns the phrase '<name> has <visits> visits'. Return only the code in a typescript block.", 'Ada has 3 visits', 'coding', kind='code', code_checks=('function greetUser', ': string', ': number')),
    Task('Define a TypeScript interface `Task` with fields id: number, title: string and done: boolean, plus a function `toggle(task: Task): Task` returning a copy with done flipped. Return only the code in a typescript block.', 'a copy of the task with done flipped', 'coding', kind='code', code_checks=('interface Task', 'done: boolean', 'function toggle')),
    Task('Write a TypeScript function `parseScore(value: string | null): number` that returns the numeric value, or 0 when value is null or not a valid number. Return only the code in a typescript block.', '0 for null or invalid input', 'coding', kind='code', code_checks=('function parseScore', 'string | null', ': number')),
    Task('Write a TypeScript generic function `firstOrNull<T>(items: T[]): T | null` returning the first element of the array, or null when it is empty. Return only the code in a typescript block.', 'the first element or null', 'coding', kind='code', code_checks=('function firstOrNull', '<T>', 'T[]', 'T | null')),
    Task('Write a SQL query against an orders table (customer_id, total) listing each customer with more than 3 orders and a combined total above 100, showing customer_id and the summed total, highest spend first. Return only the query in a sql block.', 'SELECT customer_id, SUM(total) FROM orders GROUP BY customer_id HAVING COUNT(*) > 3 AND SUM(total) > 100 ORDER BY SUM(total) DESC', 'coding', kind='code', code_checks=('GROUP BY', 'HAVING', 'COUNT(', 'SUM(', 'ORDER BY', 'DESC')),
    Task('Write a SQL query returning the second-highest distinct salary from an employees table with a single salary column, or NULL if there is none, using DISTINCT with ORDER BY, LIMIT and OFFSET. Return only the query in a sql block.', 'SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1', 'coding', kind='code', code_checks=('DISTINCT', 'ORDER BY', 'LIMIT', 'OFFSET')),
    Task('Write a SQL query listing every customer name from customers(id, name) together with how many orders they placed in orders(customer_id), including customers with zero orders. Return only the query in a sql block.', 'SELECT c.name, COUNT(o.customer_id) FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.name', 'coding', kind='code', code_checks=('LEFT JOIN', 'COUNT(', 'GROUP BY')),
    # ---- AXE-Pro ------------------------------------------
    Task('Write a Python function `dedupe(lst)` that returns the list with duplicates removed, preserving the first occurrence order. The list may contain unhashable items such as nested lists. Function definition only.', '[[1, 2], [3], [4]]', 'coding', pro=True, code_checks=('def dedupe',), test_call='dedupe([[1, 2], [3], [1, 2], [4]])'),
    Task('Write a Python function `median(nums)` that returns the median of a list. The list may contain an even number of elements — return the lower median in that case. Function definition only.', '3', 'coding', pro=True, code_checks=('def median',), test_call='median([4, 1, 3, 2, 5, 6])'),
    Task('Write a Python function `flatten(lst)` that flattens an arbitrarily nested list into a single list, preserving order. Nested lists can be empty and nesting can be deep. Function definition only.', '[1, 2, 3, 4]', 'coding', pro=True, code_checks=('def flatten',), test_call='flatten([1, [], [2, [3, []]], 4])'),
    Task('Write a Python function `count_words(s)` that takes a string and returns a dictionary mapping each word to its count. Words are separated by whitespace; strip surrounding punctuation (.,!?;:) from each word before counting; treat empty results as absent. Function definition only.', "{'hello': 2, 'world': 1}", 'coding', pro=True, code_checks=('def count_words',), test_call="count_words('hello, hello world!')"),
    Task('Write a Python function `run_length(s)` that returns the run-length encoding of string s as a list of (character, count) tuples. An empty string returns an empty list. Function definition only.', "[('a', 2), ('b', 2), ('c', 1)]", 'coding', pro=True, code_checks=('def run_length',), test_call="run_length('aabbc')"),
    Task('Write a Python function `rotate(items, k)` that rotates a list right by k positions, handling empty lists and k larger than the length without raising. Call it like `rotate([1, 2, 3, 4, 5], 7)`.', '[4, 5, 1, 2, 3]', 'coding', pro=True, kind='code', code_checks=('def rotate',), test_call='rotate([1, 2, 3, 4, 5], 7)'),
    Task('Write a Python function `fib_mod(n, m)` returning the n-th Fibonacci number modulo m (fib(0) = 0), fast enough for n in the millions. Call it like `fib_mod(1000, 998244353)`.', '548571675', 'coding', pro=True, kind='code', code_checks=('def fib_mod',), test_call='fib_mod(1000, 998244353)'),
    Task("Write a Python function `eval_rpn(tokens)` that evaluates a reverse-Polish expression given as a list of strings, returning an integer and truncating division toward zero. Call it like `eval_rpn(['2', '1', '+', '3', '*'])`.", '9', 'coding', pro=True, kind='code', code_checks=('def eval_rpn',), test_call="eval_rpn(['2', '1', '+', '3', '*'])"),
    Task('Write a Python function `interval_merge(intervals)` merging overlapping [start, end] intervals and returning them sorted as a list of tuples. Call it like `interval_merge([[1, 4], [2, 6], [8, 10]])`.', '[(1, 6), (8, 10)]', 'coding', pro=True, kind='code', code_checks=('def interval_merge',), test_call='interval_merge([[1, 4], [2, 6], [8, 10]])'),
    Task('Write a Python function `trapped_water(heights)` computing how many units of rain water the bar profile traps. Call it like `trapped_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])`.', '6', 'coding', pro=True, kind='code', code_checks=('def trapped_water',), test_call='trapped_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])'),
    Task("Write a Python function `group_anagrams(words)` returning anagram groups as a list of lists, each group sorted alphabetically and the groups ordered by their first element. Call it like `group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])`.", "[['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']]", 'coding', pro=True, kind='code', code_checks=('def group_anagrams',), test_call="group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])"),
    Task('Write a TypeScript generic function `deepClone<T>(value: T): T` that deep-clones plain objects and arrays via JSON serialisation. Return only the code in a typescript block.', 'a deep copy via JSON round-trip', 'coding', pro=True, kind='code', code_checks=('function deepClone', '<T>', 'JSON.parse', 'JSON.stringify')),
    Task('Write a SQL query using the DENSE_RANK() window function over (PARTITION BY department ORDER BY salary DESC) ranking employees by salary within each department. Return only the query in a sql block.', 'SELECT name, department, salary, DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank FROM employees', 'coding', pro=True, kind='code', code_checks=('DENSE_RANK()', 'OVER (PARTITION BY', 'ORDER BY')),
)

REASONING = (
    # ---- reasoning ---
    # ---- standard -----------------------------------------
    Task('What is 17 times 23? Answer with just the number.', '391', 'reasoning'),
    Task('A shirt costs $40 and is discounted by 25%. What is the sale price in dollars? Answer with just the number.', '30', 'reasoning'),
    Task('Solve for x: 3x + 5 = 20. Answer with just the number.', '5', 'reasoning'),
    Task('How many seconds are in one day? Answer with just the number.', '86400', 'reasoning'),
    Task('What is the sum of the first 10 positive integers? Answer with just the number.', '55', 'reasoning'),
    Task('If today is Monday, what day of the week is it exactly 100 days from now? Answer with just the day name.', 'wednesday', 'reasoning'),
    Task('How many days are in a leap year? Answer with just the number.', '366', 'reasoning'),
    Task('A train travels at 60 miles per hour for 2.5 hours. How far does it go in miles? Answer with just the number.', '150', 'reasoning'),
    Task('What is 2 to the power of 10? Answer with just the number.', '1024', 'reasoning'),
    Task('What is the next number in the sequence 2, 6, 18, 54, ...? Answer with just the number.', '162', 'reasoning'),
    Task('What is the square root of 144? Answer with just the number.', '12', 'reasoning'),
    Task('If 5 machines take 5 minutes to make 5 widgets, how many minutes do 100 machines take to make 100 widgets? Answer with just the number.', '5', 'reasoning'),
    Task('What is 15% of 200? Answer with just the number.', '30', 'reasoning'),
    Task('The average of four numbers is 12. Three of them are 10, 14, and 16. What is the fourth number? Answer with just the number.', '8', 'reasoning'),
    Task('How many minutes are in one week? Answer with just the number.', '10080', 'reasoning'),
    Task('A pen and a pencil cost $3 together. The pen costs $2 more than the pencil. How much is the pencil in dollars?', '0.5', 'reasoning', aliases=('50 cents', 'half a dollar', '$0.50')),
    Task('A pasta recipe for 4 people uses 300 g of flour. How many grams are needed for 6 people?', '450', 'reasoning'),
    Task('A car loses 20% of its value each year. Starting at $25,000, what is it worth after two years, in dollars?', '16000', 'reasoning', aliases=('16,000', '16000 dollars')),
    Task('What is the remainder when 2^20 is divided by 7?', '4', 'reasoning'),
    Task('What is the sum of every multiple of 3 from 1 to 100 inclusive?', '1683', 'reasoning'),
    Task('A 5x5x5 wooden cube is painted red on the outside, then cut into 125 unit cubes. How many unit cubes have exactly two red faces?', '36', 'reasoning'),
    Task('A login code is 3 characters long, each a lowercase letter a-z. How many different codes are possible?', '17576', 'reasoning', aliases=('17,576', '26 cubed')),
    Task('Two fair six-sided dice are rolled. In how many different ways can the faces sum to exactly 7?', '6', 'reasoning'),
    Task("Ana is twice as old as Ben. In 6 years, Ana will be one-and-a-half times Ben's age. How old is Ana now?", '12', 'reasoning', aliases=('twelve',)),
    Task('You buy a vase for $60 and sell it for $75, later buy it back for $80 and sell it again for $90. What is your total profit in dollars?', '25', 'reasoning'),
    Task('Pipe A alone fills a pool in 6 hours and pipe B alone in 4 hours. How many hours do they need together?', '2.4', 'reasoning', aliases=('12/5', '2 hours 24 minutes')),
    Task('How many diagonals does a regular octagon have?', '20', 'reasoning', aliases=('twenty',)),
    Task('What is the angle in degrees between the hour and minute hands of a clock at 3:30?', '75', 'reasoning', aliases=('75 degrees',)),
    Task('You know that A > B, that B > C, and that C = D. Is A > D guaranteed?', 'yes', 'reasoning'),
    Task('All bloops are razzies, and all razzies are lazzies. Are all bloops definitely lazzies?', 'yes', 'reasoning'),
    Task('In a 20-runner race, gold, silver and bronze go to three different runners. How many possible podium arrangements are there?', '6840', 'reasoning', aliases=('6,840',)),
    Task('A number is doubled, then 6 is added, giving 32. What was the number?', '13', 'reasoning', aliases=('thirteen',)),
    Task('With F(1) = 1 and F(2) = 1, what is F(10) in the Fibonacci sequence?', '55', 'reasoning'),
    Task('How many trailing zeros does 100! end in?', '24', 'reasoning'),
    Task('A bag has 4 red and 6 blue marbles. Two are drawn without replacement. What is the probability both are red, as a fully reduced fraction?', '2/15', 'reasoning'),
    Task('If x is 30% of 60, what is 150% of x?', '27', 'reasoning'),
    Task('A 13-metre ladder leans against a wall with its base 5 metres from the wall. At what height does it touch the wall, in metres?', '12', 'reasoning'),
    Task('A book numbers its pages 1 through 400. How many times does the digit 4 appear across all page numbers?', '81', 'reasoning'),
    # ---- AXE-Pro ------------------------------------------
    Task('If 3 cats catch 3 mice in 3 minutes, how many cats are needed to catch 100 mice in 100 minutes? Answer with just the number.', '3', 'reasoning', pro=True),
    Task("A clock strikes 6 times at 6 o'clock. The interval between strikes is uniform, and 6 strikes take 10 seconds from first to last. How many seconds do 12 strikes take? Answer with just the number.", '22', 'reasoning', pro=True),
    Task('What is the sum of all odd numbers from 1 to 19 inclusive? Answer with just the number.', '100', 'reasoning', pro=True),
    Task('If you fold a standard sheet of paper in half 6 times, how many layers thick is it? Answer with just the number.', '64', 'reasoning', pro=True),
    Task('A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How many cents does the ball cost? Answer with just the number.', '5', 'reasoning', pro=True),
    Task('How many ways can 8 people be seated around a round table, counting rotations of the same arrangement as identical?', '5040', 'reasoning', pro=True),
    Task('What is the units digit of 7 to the power 343?', '3', 'reasoning', pro=True),
    Task('You have a balance scale and 27 identical-looking balls, one slightly heavier. What is the minimum number of weighings that guarantees finding it?', '3', 'reasoning', pro=True),
    Task('How many squares of all sizes are drawn on a standard chessboard?', '204', 'reasoning', pro=True),
    Task('If the day after tomorrow is Wednesday, what weekday was the day before yesterday?', 'saturday', 'reasoning', pro=True),
    Task('What is the smallest positive integer that has exactly 12 positive divisors?', '60', 'reasoning', pro=True),
)

TASKS: tuple[Task, ...] = GENERAL + CODING + REASONING

def select(*, category: str | None = None, pro: bool = False) -> list[Task]:
    """Return tasks filtered by category (None = all) and track.

    With pro=False only standard tasks come back; with pro=True only
    the AXE-Pro subset does.  Order is bank order.
    """
    chosen = [task for task in TASKS if task.pro == pro]
    if category is not None:
        chosen = [task for task in chosen if task.category == category]
    return chosen

"""Reference implementations, one per executable coding task name.

Used only by the self-check (test_axe.py) to prove every `answer`
matches what a correct implementation actually returns for its
`test_call`.  A single implementation serves both the standard and
the AXE-Pro variant where they share a function name.
"""

SOLUTIONS: dict[str, str] = {
    "count_words":
'''
def count_words(text):
    counts = {}
    for word in "".join(c.lower() if c.isalnum() else " " for c in text).split():
        counts[word] = counts.get(word, 0) + 1
    return counts
''',
    "fizzbuzz":
'''
def fizzbuzz(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
''',
    "is_palindrome":
'''
def is_palindrome(text):
    s = "".join(c.lower() for c in text if c.isalnum())
    return s == s[::-1]
''',
    "fib":
'''
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
''',
    "flatten":
'''
def flatten(nested):
    out = []
    for item in nested:
        if isinstance(item, list):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out
''',
    "run_length":
'''
def run_length(text):
    runs = []
    for ch in text:
        if runs and runs[-1][0] == ch:
            runs[-1] = (ch, runs[-1][1] + 1)
        else:
            runs.append((ch, 1))
    return runs
''',
    "merge_dicts":
'''
def merge_dicts(a, b):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0) + value
    return out
''',
    "reverse_words":
'''
def reverse_words(text):
    return " ".join(reversed(text.split()))
''',
    "median":
'''
def median(nums):
    s = sorted(nums)
    return s[(len(s) - 1) // 2]
''',
    "title_case":
'''
def title_case(text):
    return " ".join(w[:1].upper() + w[1:] for w in text.split())
''',
    "chunk":
'''
def chunk(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]
''',
    "factorial":
'''
def factorial(n):
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out
''',
    "most_common":
'''
def most_common(items):
    return max(set(items), key=items.count)
''',
    "dedupe":
'''
def dedupe(items):
    return [x for i, x in enumerate(items) if x not in items[:i]]
''',
    "gcd":
'''
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
''',
    "slugify":
'''
def slugify(text):
    out = []
    prev = ""
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")
''',
    "roman":
'''
def roman(n):
    pairs = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = []
    for value, numeral in pairs:
        while n >= value:
            out.append(numeral)
            n -= value
    return "".join(out)
''',
    "parse_ranges":
'''
def parse_ranges(spec):
    nums = []
    for part in spec.split(","):
        if "-" in part:
            start, end = part.split("-")
            nums.extend(range(int(start), int(end) + 1))
        else:
            nums.append(int(part))
    return nums
''',
    "is_anagram":
'''
def is_anagram(a, b):
    norm = lambda s: sorted(c.lower() for c in s if c.isalnum())
    return norm(a) == norm(b)
''',
    "transpose":
'''
def transpose(matrix):
    return [list(row) for row in zip(*matrix)]
''',
    "caesar_shift":
'''
def caesar_shift(text, k):
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + k) % 26 + 97))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + k) % 26 + 65))
        else:
            out.append(ch)
    return "".join(out)
''',
    "binary_search_index":
'''
def binary_search_index(items, target):
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
''',
    "pascal_row":
'''
def pascal_row(n):
    row = [1]
    for _ in range(n):
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return row
''',
    "dot":
'''
def dot(a, b):
    return sum(a[i] * b[i] for i in range(len(a)))
''',
    "balanced":
'''
def balanced(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
''',
    "top_k":
'''
def top_k(items, k):
    return sorted(items, reverse=True)[:k]
''',
    "is_prime":
'''
def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True
''',
    "collatz_len":
'''
def collatz_len(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps
''',
    "rotate_matrix":
'''
def rotate_matrix(matrix):
    return [list(row) for row in zip(*matrix[::-1])]
''',
    "bst_preorder":
'''
def bst_preorder(values):
    def insert(node, v):
        if node is None:
            return [v, None, None]
        if v < node[0]:
            node[1] = insert(node[1], v)
        else:
            node[2] = insert(node[2], v)
        return node
    def walk(node, out):
        if node is not None:
            out.append(node[0])
            walk(node[1], out)
            walk(node[2], out)
    root = None
    for v in values:
        root = insert(root, v)
    out = []
    walk(root, out)
    return out
''',
    "kth_smallest":
'''
def kth_smallest(items, k):
    return sorted(items)[k - 1]
''',
    "lcs_len":
'''
def lcs_len(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
    return dp[-1][-1]
''',
    "edit_distance":
'''
def edit_distance(a, b):
    dp = [[j for j in range(len(b) + 1)] for j in range(len(a) + 1)]
    for i in range(len(a) + 1):
        dp[i][0] = i
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[-1][-1]
''',
    "count_islands":
'''
def count_islands(grid):
    seen = set()
    islands = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 1 and (r, c) not in seen:
                islands += 1
                stack = [(r, c)]
                while stack:
                    x, y = stack.pop()
                    if (x, y) in seen or not (0 <= x < len(grid) and 0 <= y < len(grid[0])) or grid[x][y] != 1:
                        continue
                    seen.add((x, y))
                    stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    return islands
''',
    "zero_sum_triplets":
'''
def zero_sum_triplets(items):
    nums = sorted(items)
    out = []
    for i in range(len(nums) - 2):
        if i and nums[i] == nums[i - 1]:
            continue
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            total = nums[i] + nums[lo] + nums[hi]
            if total == 0:
                out.append((nums[i], nums[lo], nums[hi]))
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
            elif total < 0:
                lo += 1
            else:
                hi -= 1
    return out
''',
    "rotate":
'''
def rotate(items, k):
    if not items:
        return []
    k %= len(items)
    return items[-k:] + items[:-k] if k else list(items)
''',
    "fib_mod":
'''
def fib_mod(n, m):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b) % m
    return a
''',
    "eval_rpn":
'''
def eval_rpn(tokens):
    stack = []
    for tok in tokens:
        if tok in "+-*/":
            b, a = stack.pop(), stack.pop()
            if tok == "+":
                stack.append(a + b)
            elif tok == "-":
                stack.append(a - b)
            elif tok == "*":
                stack.append(a * b)
            else:
                q = abs(a) // abs(b)
                stack.append(q if (a >= 0) == (b >= 0) else -q)
        else:
            stack.append(int(tok))
    return stack[0]
''',
    "interval_merge":
'''
def interval_merge(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
''',
    "trapped_water":
'''
def trapped_water(heights):
    lo, hi = 0, len(heights) - 1
    left = right = water = 0
    while lo < hi:
        if heights[lo] <= heights[hi]:
            left = max(left, heights[lo])
            water += left - heights[lo]
            lo += 1
        else:
            right = max(right, heights[hi])
            water += right - heights[hi]
            hi -= 1
    return water
''',
    "group_anagrams":
'''
def group_anagrams(words):
    groups = {}
    for word in words:
        groups.setdefault("".join(sorted(word)), []).append(word)
    return sorted(sorted(g) for g in groups.values())
''',
}
