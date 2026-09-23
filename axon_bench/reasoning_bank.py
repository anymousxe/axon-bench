"""Independently specified reasoning problems and auditable answer derivations."""

# Each row is (slug, prompt, answer, difficulty, pro, reference).
ROWS = [
    # Normal 01
    (
        "dice_conditioned_maximum",
        "Two independent fair six-sided dice are rolled. Given that their maximum is exactly 5, what is the probability that their sum is 8? Give a reduced fraction.",
        "2/9", "medium", False,
        "There are 5^2-4^2=9 ordered outcomes with maximum 5. Only (3,5) and (5,3) sum to 8, so the conditional probability is 2/9.",
    ),
    # Normal 02
    (
        "urn_conditioned_pair",
        "An urn has three red and two blue balls, all individually distinct. Two balls are sampled uniformly without replacement. Given that at least one is red, what is the probability both are red? Give a reduced fraction.",
        "1/3", "medium", False,
        "There are C(5,2)=10 equally likely pairs. Removing the single all-blue pair leaves 9; C(3,2)=3 are all-red. Thus 3/9=1/3.",
    ),
    # Normal 03
    (
        "factory_posterior",
        "A component comes from factory A with probability 1/4 and factory B otherwise. A components fail a test with probability 1/5; B components fail with probability 1/20. Given a failed test, what is the probability the component came from A? Give a reduced fraction.",
        "4/7", "medium", False,
        "The A-and-failure probability is 1/20=4/80; B-and-failure is 3/80. Conditioning on their sum gives 4/7.",
    ),
    # Normal 04
    (
        "first_repeat_wait",
        "Independent fair coin tosses continue until a toss equals the immediately preceding toss. The first toss cannot stop the process. What is the expected total number of tosses? Give an integer.",
        "3", "medium", False,
        "After the first toss, each next toss matches the current last toss with probability 1/2. The additional waiting time is geometric with mean 2, for total mean 3.",
    ),
    # Normal 05
    (
        "paired_indicator_expectation",
        "A uniformly random permutation of the numbers 1 through 7 is written in a row. Count the indices i in {1,...,6} for which entry i is smaller than entry i+1. What is the expected count? Give an integer.",
        "3", "medium", False,
        "For each adjacent pair either ordering is equally likely, so its increasing indicator has mean 1/2. Linearity gives 6/2=3 without requiring independence.",
    ),
    # Normal 06
    (
        "committee_two_divisions",
        "A committee of four is chosen from five engineers and four designers, all distinct. How many committees contain at least two engineers and at least one designer?",
        "100", "medium", False,
        "The only possible engineer/designer splits are 2/2 and 3/1. They contribute C(5,2)C(4,2)=60 and C(5,3)C(4,1)=40, totaling 100.",
    ),
    # Normal 07
    (
        "separated_selected_positions",
        "How many subsets of size three of {1,2,...,9} contain no two consecutive integers?",
        "35", "medium", False,
        "For selected a<b<c with gaps at least two, map to a<b-1<c-2 in {1,...,7}. This is a bijection to three-subsets of seven positions, giving C(7,3)=35.",
    ),
    # Normal 08
    (
        "bounded_compositions",
        "How many ordered triples (x,y,z) of nonnegative integers satisfy x+y+z=8 and each coordinate is at most 4?",
        "15", "hard", False,
        "Unbounded there are C(10,2)=45. For each coordinate at least 5, subtract C(5,2)=10 after shifting it down by 5. Two violations require sum at least 10 and are impossible, giving 45-30=15.",
    ),
    # Normal 09
    (
        "multiset_no_adjacent_a",
        "How many distinct strings can be made from exactly three A's, two B's, and one C, if no two A's may be adjacent?",
        "12", "medium", False,
        "The non-A multiset BBC has 3 distinct arrangements. Each has four gaps; select three gaps for the three isolated A's in C(4,3)=4 ways. Product 12.",
    ),
    # Normal 10
    (
        "fixed_point_exclusion",
        "How many permutations p of {1,2,3,4,5} have exactly three indices i for which p(i)=i?",
        "10", "medium", False,
        "Choose the three fixed indices in C(5,3)=10 ways. The other two must swap, with exactly one possible permutation. Hence 10.",
    ),
    # Normal 11
    (
        "door_truth_count",
        "Exactly one of doors A, B, C hides a prize. Sign A says 'The prize is behind A.' Sign B says 'The prize is not behind A.' Sign C says 'The prize is behind B.' Exactly two signs are true. Which door hides the prize? Answer with its uppercase letter.",
        "B", "medium", False,
        "A and B's signs are complements, so exactly one is always true. For two signs to be true, C's sign must be true. This uniquely puts the prize behind B.",
    ),
    # Normal 12
    (
        "implication_models",
        "How many truth assignments to Boolean variables P,Q,R satisfy (P implies Q), (Q implies R), and (P or R)? Here 'or' is inclusive.",
        "3", "medium", False,
        "If R were false then Q and P would be false, violating P or R. With R true, allowed (P,Q) are (false,false), (false,true), and (true,true), giving 3.",
    ),
    # Normal 13
    (
        "rank_constraints",
        "Four distinct runners A,B,C,D finish without ties. A finishes before C, B finishes before C, and D finishes immediately after A. How many finish orders meet all three conditions?",
        "2", "medium", False,
        "Treat AD as a block. C must follow that block because A precedes C and nothing can occur between A and D; C must also follow B. Thus C is last among the three units, and the only orders are AD,B,C and B,AD,C, giving 2.",
    ),
    # Normal 14
    (
        "cyclic_remainders",
        "Find the least positive integer n with n congruent to 2 modulo 5, n congruent to 3 modulo 7, and n congruent to 4 modulo 9.",
        "157", "hard", False,
        "Write n=2+5k. Modulo 7 gives 5k=1, hence k=3 mod 7 and n=17+35t. Modulo 9 this becomes 8+8t=4, so t=4 mod 9. The least positive solution is 17+140=157.",
    ),
    # Normal 15
    (
        "power_last_digits",
        "What are the last two decimal digits of 7^2026? Give exactly two digits, including a leading zero if needed.",
        "49", "medium", False,
        "Modulo 100, 7^2=49 and 7^4=1. Since 2026 is 2 modulo 4, the residue is 49.",
    ),
    # Normal 16
    (
        "linear_congruence_count",
        "How many integers x with 0<=x<60 satisfy 18x congruent to 12 modulo 60?",
        "6", "medium", False,
        "Divide by gcd(18,60)=6 to get 3x=2 mod 10, or x=4 mod 10. In the specified range the solutions are 4,14,24,34,44,54.",
    ),
    # Normal 17
    (
        "euclid_division_trace",
        "Run Euclid's algorithm on (252,198), repeatedly replacing (a,b) by (b,a mod b) until b=0. How many replacement steps occur?",
        "4", "medium", False,
        "The pairs after replacements are (198,54), (54,36), (36,18), (18,0), so four replacements occur.",
    ),
    # Normal 18
    (
        "stable_insertion_shifts",
        "Insertion sort processes [4,1,3,1,2] from left to right in ascending order. It shifts an earlier element right only when that element is strictly greater than the key. How many such rightward shifts occur in total?",
        "6", "medium", False,
        "The keys at original indices 1,2,3,4 require 1,1,2,2 shifts respectively. Equal 1s are not shifted past one another. Total 6.",
    ),
    # Normal 19
    (
        "fifo_cache_trace",
        "An initially empty cache holds three distinct pages. On a miss, insert the requested page; if full, first evict the page inserted earliest. Hits do not change insertion order. For requests A,B,C,A,D,B,E,A, how many misses occur?",
        "6", "medium", False,
        "A,B,C miss; A hits. D misses and evicts A; B hits. E misses and evicts B. A misses and evicts C. There are six misses.",
    ),
    # Normal 20
    (
        "breadth_first_parent",
        "An undirected graph has edges AB, AC, BD, BE, CE, CF, DF, EG. Run breadth-first search from A, enqueueing a vertex only on first discovery and visiting each vertex's neighbors in alphabetical order. What is the discovery-tree path from A to G? Format letters separated by hyphens.",
        "A-B-E-G", "medium", False,
        "A discovers B,C. B discovers D,E before C is processed; C discovers F. E later discovers G, giving parents G<-E<-B<-A.",
    ),
    # Normal 21
    (
        "weighted_interval_choice",
        "Jobs have (start,end,value): A=(0,3,5), B=(1,4,6), C=(3,5,4), D=(4,7,7), E=(5,7,5). Jobs cannot overlap but an end equal to another start is allowed. What is the maximum total value of a compatible subset?",
        "14", "hard", False,
        "A,C,E are compatible and total 14. A,D total 12; B,D total 13; B,E total 11. The only compatible three-job chain is A,C,E, and no longer chain exists, so 14 is optimal.",
    ),
    # Normal 22
    (
        "two_machine_makespan",
        "Four nonpreemptive jobs have processing times 2,3,4,7. They are available at time zero and can run on either of two identical machines; a machine runs at most one job at a time. What is the minimum time at which all jobs can finish?",
        "9", "medium", False,
        "Total load 16 gives bound 8, but no subset sums to 8: a subset containing 7 cannot add 1, and without 7 the available sums from 2,3,4 omit 8. Loads 7+2=9 and 4+3=7 achieve 9.",
    ),
    # Normal 23
    (
        "precedence_critical_path",
        "Tasks A,B,C,D,E take 3,5,4,2,3 time units respectively. A and B have no prerequisites; C follows A; D follows both A and B; E follows both C and D. With unlimited processors and no delays other than prerequisites, what is the earliest completion time of E?",
        "10", "medium", False,
        "A,B finish at 3,5. C finishes at 7 and D at max(3,5)+2=7. E finishes at max(7,7)+3=10.",
    ),
    # Normal 24
    (
        "binary_search_worst_queries",
        "An unknown integer is in {1,...,100}. Each query asks whether it is at most a chosen integer and receives a truthful yes/no answer. Queries may adapt to previous answers. What is the minimum worst-case number of queries needed to identify it?",
        "7", "medium", False,
        "Six binary answers distinguish at most 64 possibilities, fewer than 100. Balanced binary splitting distinguishes up to 128 possibilities with seven queries, so seven is necessary and sufficient.",
    ),
    # Normal 25
    (
        "prefix_code_missing_length",
        "A binary prefix-free code has exactly four codewords, with lengths 1,2,3,L where L is a positive integer. What is the smallest possible L?",
        "3", "medium", False,
        "The first three Kraft weights total 1/2+1/4+1/8=7/8, leaving at most 1/8, so L>=3. Codewords 0,10,110,111 realize L=3.",
    ),
    # Normal 26
    (
        "subtraction_game_position",
        "Two players alternate removing 1,3,or 4 stones from a pile; a move cannot remove more stones than remain. The player taking the last stone wins. With 8 stones initially and optimal play, which first move wins? Answer the number of stones removed; exactly one first move is winning.",
        "1", "hard", False,
        "The losing positions through 7 are 0,2,7: each has no move to a losing position, while each of 1,3,4,5,6 has such a move. From 8, removing 1 reaches losing 7; removing 3 or 4 reaches winning 5 or 4. Only removing 1 wins.",
    ),
    # Normal 27
    (
        "nim_unique_move",
        "Normal-play Nim starts with heap sizes (3,4,5). A move removes any positive number from exactly one heap; taking the last object wins. What heap sizes should the first player leave to force a win? Give a comma-separated triple in the original heap order.",
        "1,4,5", "hard", False,
        "The xor is 3 xor 4 xor 5=2. Only the first heap has that leading bit set, and its target size is 3 xor 2=1. The resulting xor is zero.",
    ),
    # Normal 28
    (
        "coupon_two_types",
        "Independent draws produce A with probability 1/3 and B with probability 2/3. Starting with neither type, what is the expected number of draws until both types have appeared? Give a reduced fraction.",
        "7/2", "hard", False,
        "The first draw costs one. If it is A, mean additional wait for B is 3/2; if B, mean wait for A is 3. Thus 1+(1/3)(3/2)+(2/3)3=7/2.",
    ),
    # Normal 29
    (
        "random_walk_hitting",
        "A token starts at 2 on the integer line {0,1,2,3,4,5}. At each step before reaching 0 or 5 it moves left or right with equal probability. What is the probability it reaches 5 before 0? Give a reduced fraction.",
        "2/5", "medium", False,
        "The hitting probabilities satisfy h(0)=0, h(5)=1, and h(i)=(h(i-1)+h(i+1))/2. Their unique solution is h(i)=i/5, so h(2)=2/5.",
    ),
    # Normal 30
    (
        "lattice_paths_forbidden_vertex",
        "A path from (0,0) to (4,3) uses only unit steps right or up. How many such paths do not visit (2,1)?",
        "17", "medium", False,
        "All paths number C(7,3)=35. Paths through (2,1) number C(3,1)C(4,2)=3*6=18, leaving 17.",
    ),
    # Normal 31
    (
        "proper_cycle_colors",
        "Each vertex of a cycle with four labeled vertices is colored with one of three labeled colors. Adjacent vertices must have different colors; unused colors are allowed. How many colorings are possible?",
        "18", "hard", False,
        "Choose color of vertex 1 in 3 ways and vertex 2 in 2. If vertex 3 equals vertex 1, vertex 4 has 2 choices; otherwise vertex 3 is the third color and vertex 4 has 1 choice. Thus 3*2*(2+1)=18.",
    ),
    # Normal 32
    (
        "degree_sequence_edge_count",
        "A simple undirected graph has eight vertices. Three have degree 4, four have degree 3, and one has degree 2. How many edges does the graph have?",
        "13", "easy", False,
        "The degree sum is 3*4+4*3+2=26. Each edge contributes twice, so there are 13 edges.",
    ),
    # Normal 33
    (
        "set_union_exactly_one",
        "In a group of 60 people, 35 know language A, 28 know language B, and 12 know neither. How many know exactly one of the two languages?",
        "33", "medium", False,
        "The union has 48 people. The intersection is 35+28-48=15. Exactly one totals 48-15=33.",
    ),
    # Normal 34
    (
        "binary_parity_assignments",
        "Bits a,b,c,d satisfy a XOR b=1, b XOR c=0, and c XOR d=1. How many four-bit strings abcd satisfy all three equations?",
        "2", "medium", False,
        "Choose b freely; then a=1-b, c=b, d=1-b. The two strings are 1001 and 0110.",
    ),
    # Normal 35
    (
        "circular_seating_rotation",
        "Six distinct people sit around a round table. Seating arrangements differing only by rotation are identical, but reflections are distinct. Two designated people must sit next to each other. How many arrangements satisfy this?",
        "48", "medium", False,
        "Collapse the designated pair into a block. Five distinct units around a circle have (5-1)!=24 orders, with 2 internal orders of the block, giving 48.",
    ),
    # Normal 36
    (
        "median_after_deletion",
        "Five distinct integers in increasing order are 2,5,9,12,20. One of them is deleted uniformly at random. Define the median of the four remaining numbers as the mean of their two middle numbers. What is the expected median? Give a reduced fraction.",
        "87/10", "medium", False,
        "Deleting 2 or 5 gives median 21/2; deleting 9 gives 17/2; deleting 12 or 20 gives 7. Their sum is 87/2, so the mean is 87/10.",
    ),
    # Normal 37
    (
        "measurement_difference_bound",
        "Positive real lengths x and y satisfy 4<=x<=7 and 2<=y<=5. What is the greatest possible value of x/(x+y)? Give a reduced fraction.",
        "7/9", "medium", False,
        "For positive lengths the ratio increases with x and decreases with y. It is maximized at x=7,y=2, yielding 7/9.",
    ),
    # Normal 38
    (
        "deterministic_rewrite_trace",
        "Starting from the word AB, simultaneously replace each A by AB and each B by A on each round. After four rounds, how many B's are present?",
        "5", "medium", False,
        "The counts (A,B) start at (1,1), and each round maps (a,b) to (a+b,a). The four results are (2,1),(3,2),(5,3),(8,5), so there are 5 B's.",
    ),
    # Normal 39
    (
        "stack_permutation_feasibility",
        "The input stream 1,2,3,4 must be pushed in that order onto one initially empty stack. Pops may be interleaved arbitrarily. Which candidate output cannot occur: A=2,1,4,3; B=3,2,1,4; C=3,1,2,4; D=1,4,3,2? Answer one uppercase letter.",
        "C", "hard", False,
        "To output 3 first, 1 and 2 must already be below it. After popping 3, 2 blocks 1, so C is impossible. A uses paired pushes/pops; B pops 3,2,1 then 4; D pops 1 then pushes and pops 2,3,4 in reverse.",
    ),
    # Normal 40
    (
        "shortest_path_tied_routes",
        "A directed graph has weighted edges S->A:2, S->B:1, A->T:3, B->T:4, A->B:1, B->C:2, C->T:2. How many distinct directed paths from S to T have minimum total weight?",
        "3", "hard", False,
        "S-A-T, S-B-T, and S-B-C-T each weigh 5. Routes beginning S-A-B weigh at least 2+1+4=7, and no other paths exist. Thus there are three shortest paths.",
    ),
    # Normal 41
    (
        "meeting_interval_overlap",
        "Meetings occupy half-open intervals [0,4), [2,5), [4,7), [5,6), [5,8). A room holds one meeting at a time, and a meeting ending at t frees its room for one starting at t. What is the minimum number of rooms required?",
        "3", "medium", False,
        "On [5,6), three meetings are active: [4,7),[5,6),[5,8). At all other times at most three are active; greedy reuse of rooms attains this maximum overlap, so three suffice.",
    ),
    # Normal 42
    (
        "digit_sum_divisibility",
        "How many three-digit decimal integers use three distinct digits from {1,2,3,4,5} and are divisible by 3?",
        "24", "medium", False,
        "The eligible digit subsets with sum divisible by 3 are {1,2,3},{1,3,5},{2,3,4},{3,4,5}. Each has 3!=6 orderings, totaling 24.",
    ),
    # Normal 43
    (
        "tournament_wins",
        "Five players play a round-robin tournament: each pair plays once, with no draws. Four players' win totals are 0,1,2,3. How many wins does the fifth player have?",
        "4", "easy", False,
        "There are C(5,2)=10 games and hence ten wins. The specified players total six, leaving four wins for the fifth.",
    ),
    # Normal 44
    (
        "two_events_independence",
        "Events E and F are independent, with P(E)=2/5 and P(F)=3/4. What is the probability that exactly one occurs? Give a reduced fraction.",
        "11/20", "medium", False,
        "The disjoint cases E and not F, and F and not E, have probabilities (2/5)(1/4)=2/20 and (3/5)(3/4)=9/20, totaling 11/20.",
    ),
    # Normal 45
    (
        "residue_pigeonhole_threshold",
        "What is the smallest integer k such that every choice of k distinct integers from {1,...,20} contains two whose sum is 21?",
        "11", "medium", False,
        "The numbers form ten disjoint complementary pairs (1,20),...,(10,11). A selection of 11 must complete a pair, while selecting {1,...,10} avoids every pair.",
    ),
    # Normal 46
    (
        "load_balanced_transport",
        "A boat carries at most two people. Four people take 1,2,7,10 minutes respectively to cross; a crossing takes the slower occupant's time. Everyone starts on the left, the boat starts there, and each return trip must have an occupant. What is the minimum total time to get everyone to the right?",
        "17", "hard", False,
        "Use crossings (1,2) right:2; 1 left:1; (7,10) right:10; 2 left:2; (1,2) right:2, totaling 17. The two standard ways to transfer the slow pair cost min(1+2*2+10,2*1+7+10)=15 before the final fast-pair crossing of 2, yielding optimum 17.",
    ),
    # Normal 47
    (
        "finite_function_cycle",
        "Define f on {0,1,...,10} by f(x)=(3x+1) mod 11, with residues in that set. Starting at x=0, apply f exactly 100 times. What is the final x?",
        "0", "hard", False,
        "The orbit is 0,1,4,2,7,0 and has period 5. Since 100 is a multiple of 5, the final state is 0.",
    ),
    # Pro 01
    (
        "overlapping_pattern_wait",
        "Independent fair coin tosses continue until the consecutive pattern HTH first appears. What is the expected number of tosses, counting every toss from the start? Give an integer.",
        "10", "hard", True,
        "Let E0,EH,EHT be remaining expectations with longest suffix matching a pattern prefix of length 0,1,2. E0=1+(E0+EH)/2; EH=1+(EH+EHT)/2; EHT=1+E0/2. Thus E0=2+EH, EH=2+EHT, and E0=5+E0/2, giving 10.",
    ),
    # Pro 02
    (
        "urn_random_parameter_posterior",
        "Choose p uniformly from the three values 1/4,1/2,3/4. Conditional on p, toss a coin independently five times, each with head probability p. The first four tosses contain exactly three heads. What is the conditional probability the fifth toss is a head? Give a reduced fraction.",
        "29/46", "hard", True,
        "The likelihoods, with the common factor C(4,3) omitted, are p^3(1-p)=3/256,16/256,27/256. The predictive mean is ((3/4)+8+(81/4))/(3+16+27)=29/46.",
    ),
    # Pro 03
    (
        "sampling_until_color_change",
        "An urn initially contains three red and three blue balls. Draw balls uniformly without replacement until both colors have appeared. What is the variance of the total number of draws? Give a reduced fraction.",
        "9/20", "hard", True,
        "After the first draw, P(T=2)=3/5, P(T=3)=(2/5)(3/4)=3/10, and P(T=4)=(2/5)(1/4)=1/10. Hence E[T]=5/2 and E[T^2]=67/10, so Var(T)=67/10-25/4=9/20.",
    ),
    # Pro 04
    (
        "random_transposition_fixed_points",
        "Start with the identity permutation of four labeled objects. Independently twice, choose uniformly one of the six pairs of positions and swap the objects in those positions. What is the probability that the resulting permutation has no fixed points? Give a reduced fraction.",
        "1/6", "hard", True,
        "After the first transposition, the second either repeats it (one pair), shares exactly one position (four pairs), or is disjoint (one pair). Only the disjoint case moves all four objects, so the probability is 1/6.",
    ),
    # Pro 05
    (
        "negative_dependence_indicators",
        "A uniformly random subset of size three is selected from {1,...,8}. Let X be 1 if 1 is selected and 0 otherwise; define Y similarly for 2. What is Cov(X,Y)? Give a reduced signed fraction.",
        "-15/448", "hard", True,
        "E[X]=E[Y]=3/8. E[XY]=(3/8)(2/7)=3/28. The covariance is 3/28-9/64=(48-63)/448=-15/448.",
    ),
    # Pro 06
    (
        "ballot_strict_prefixes",
        "An election has seven votes for A and four for B. All strings containing these votes are equally likely. What is the probability that A is strictly ahead of B after every nonempty prefix of the count? Give a reduced fraction.",
        "3/11", "hard", True,
        "The strict ballot theorem gives (7-4)/(7+4)=3/11. Equivalently, the number of valid strings is (3/11)C(11,4)=90 out of 330.",
    ),
    # Pro 07
    (
        "surjections_with_fiber_parity",
        "How many functions from the labeled set {1,...,7} onto the labeled set {A,B,C} have an odd number of preimages for every target?",
        "546", "expert", True,
        "The positive odd fiber sizes summing to 7 are permutations of (5,1,1) and (3,3,1). The first contributes 3*7!/(5!1!1!)=126. The second contributes 3*7!/(3!3!1!)=420. Total 546.",
    ),
    # Pro 08
    (
        "necklaces_with_exact_weight",
        "A circular necklace has eight positions, exactly four black beads and four white beads. Two necklaces are identical if one rotates to the other; reflection alone does not identify them. How many distinct necklaces exist?",
        "10", "expert", True,
        "Burnside over eight rotations: identity fixes C(8,4)=70; rotations by 2 and 6 each fix 2; rotation by 4 fixes C(4,2)=6; odd rotations fix none. The average is (70+2+2+6)/8=10.",
    ),
    # Pro 09
    (
        "rook_forbidden_positions",
        "How many permutations p of {1,2,3,4,5} satisfy p(1) not in {1,2}, p(2) not in {1,2}, and p(3) !=3? No other positions are restricted.",
        "32", "hard", True,
        "First force positions 1 and 2 into distinct elements of {3,4,5}: 3*2*3!=36 permutations. Those with p(3)=3 must place 4,5 in the first two positions (2 ways), then arrange 1,2 in the last two (2 ways), so only 4 are excluded. Result 32.",
    ),
    # Pro 10
    (
        "noncrossing_matching_depth",
        "Six labeled points 1,...,6 lie in that clockwise order on a circle. A perfect matching pairs them using three straight chords, with no chords crossing in their interiors. How many such matchings do not pair 1 with 2?",
        "3", "hard", True,
        "There are Catalan C3=5 noncrossing perfect matchings. Fixing chord (1,2) leaves four consecutive points with C2=2 matchings, so 5-2=3 remain.",
    ),
    # Pro 11
    (
        "linear_extensions_two_chains",
        "Six distinct tasks A,B,C,D,E,F must be put in a total order. Constraints are A before B before C, D before E before F, and B before E. How many total orders satisfy these constraints?",
        "10", "hard", True,
        "Without B<E there are C(6,3)=20 interleavings of the chains. Swapping the entire two chains is a bijection exchanging B<E and E<B, which cannot tie, so exactly half, 10, satisfy B<E.",
    ),
    # Pro 12
    (
        "satisfying_assignments_exact_count",
        "Boolean variables a,b,c,d obey: exactly two are true; a implies b; c implies not b; and d implies (a or c), where or is inclusive. How many satisfying assignments are there?",
        "2", "hard", True,
        "Test the six pairs of true variables. {a,b} satisfies all clauses; {a,c} and {a,d} violate a=>b; {b,c} violates c=>not b; {b,d} violates d=>(a or c); {c,d} satisfies all clauses. Therefore there are 2 satisfying assignments.",
    ),
    # Pro 13
    (
        "epistemic_number_announcement",
        "Two agents each see their own positive integer but not the other's. It is common knowledge that the two integers sum to either 5 or 6, and both reason perfectly and truthfully. A publicly announces 'I do not know your number.' B then publicly announces 'I do not know your number.' A then publicly announces 'Now I know your number.' List all possible values of A's number in increasing order, separated by commas.",
        "1,4", "expert", True,
        "Initially an agent knows the other number only when their own is 5. A's first ignorance excludes A=5. B would then know when B=1 (only A=4 remains) or B=5 (only A=1), so B's ignorance excludes B in {1,5}. A can now distinguish the two sum possibilities only for A=1, where B=4 or 5, or A=4, where B=1 or 2. Thus A can be 1 or 4.",
    ),
    # Pro 14
    (
        "liar_cycle_consistency",
        "Five people A,B,C,D,E are each either a truth-teller or a liar. Truth-tellers' statements are true and liars' statements false. A says B is a liar; B says C is a liar; C says D is a liar; D says E is a liar; E says A is a truth-teller. How many assignments of types are consistent?",
        "2", "hard", True,
        "Let each letter also denote its truth bit. The equations are A=1-B, B=1-C, C=1-D, D=1-E, E=A. Four negations imply A=E, matching the last condition. A can be either bit, and determines all others uniquely, giving 2.",
    ),
    # Pro 15
    (
        "crt_non_coprime_feasibility",
        "Find the least nonnegative integer x satisfying x=5 mod 12, x=11 mod 18, and x=2 mod 7.",
        "65", "hard", True,
        "The first two combine to x=29 mod 36: 5+12k=11 mod18 gives 2k=1 mod3, hence k=2 mod3. Then 29+36t=2 mod7 gives 1+t=2, so t=1 mod7. Least nonnegative x is 65.",
    ),
    # Pro 16
    (
        "modular_square_roots",
        "How many residue classes x modulo 360 satisfy x^2=1 modulo 360?",
        "16", "expert", True,
        "Factor 360=8*9*5 with coprime factors. Modulo 8 every odd residue (4 choices) squares to 1. Modulo 9 and modulo 5 the only roots are plus/minus 1 (2 each). CRT combines them independently, giving 4*2*2=16.",
    ),
    # Pro 17
    (
        "valuation_binomial",
        "What is the exponent of 2 in the prime factorization of the binomial coefficient C(100,37)?",
        "6", "hard", True,
        "Legendre gives v2(100!)=50+25+12+6+3+1=97; v2(37!)=18+9+4+2+1=34; v2(63!)=31+15+7+3+1=57. The difference is 97-34-57=6.",
    ),
    # Pro 18
    (
        "polynomial_remainder_operator",
        "Let P(x)=x^100+x^50+1. When P is divided over the integers by x^2+x+1, the remainder is ax+b with degree less than two. Give a,b as a comma-separated pair.",
        "0,0", "hard", True,
        "Modulo x^2+x+1, x^3=1. Thus x^100=x and x^50=x^2=-x-1. Adding 1 makes zero, so a=b=0.",
    ),
    # Pro 19
    (
        "binary_matrix_rank_count",
        "How many 2-by-3 matrices over the field with two elements have rank exactly 1? Entries are 0 or 1, with arithmetic modulo 2.",
        "21", "hard", True,
        "A rank-one matrix is u v^T where u is a nonzero two-vector (3 choices) and v a nonzero three-vector (7 choices). Over this field there is no nontrivial scalar rescaling, so the representation is unique and the count is 21.",
    ),
    # Pro 20
    (
        "affine_bit_system_projection",
        "Bits x1,...,x6 satisfy x1 XOR x2 XOR x3=1, x2 XOR x4=0, x3 XOR x5=1, x4 XOR x5 XOR x6=0. Among all satisfying assignments, how many have x1=x6?",
        "4", "hard", True,
        "Set x2=s,x3=t freely. Then x1=1 XOR s XOR t, x4=s, x5=1 XOR t, x6=1 XOR s XOR t. Thus x1=x6 always, and there are 2^2=4 assignments.",
    ),
    # Pro 21
    (
        "minimax_search_unequal_costs",
        "An unknown value is one of the ordered integers 1,...,5. A query 'is the value at most k?' may use any integer k. A yes answer costs 1 unit and a no answer costs 2 units. Queries adapt to previous answers and identification itself costs zero. What is the minimum worst-case total cost to identify the value?",
        "4", "expert", True,
        "Let M(c) be the largest number of ordered possibilities distinguishable with worst-case budget c. M(0)=M(1)=1, and M(c)=M(c-1)+M(c-2) for c>=2. Thus M(2)=2,M(3)=3,M(4)=5. A root split into 3 lower and 2 upper values attains cost 4; cost 3 permits only 3 values.",
    ),
    # Pro 22
    (
        "huffman_merge_cost",
        "Six symbols have weights 2,3,7,9,18,25. Construct a binary prefix code minimizing the sum over symbols of weight times codeword length. What is that minimum weighted sum?",
        "141", "hard", True,
        "Huffman merges are 2+3=5, 5+7=12, 9+12=21, 18+21=39, 25+39=64. The weighted path length equals the sum of merged weights, 5+12+21+39+64=141.",
    ),
    # Pro 23
    (
        "single_lie_information_bound",
        "An unknown item is one of 16 labeled items. You may ask seven fixed, nonadaptive yes/no questions, each specifying any subset of the items; membership gives the truthful answer. An adversary may flip at most one answer. Can seven questions always identify the item? Answer YES or NO.",
        "YES", "expert", True,
        "Use the binary Hamming [7,4,3] code: label the 16 items with its 16 codewords, and question j asks whether bit j is 1. Minimum distance 3 permits correction of one flipped bit. The 16 radius-one balls each have 8 strings and partition all 128 seven-bit strings.",
    ),
    # Pro 24
    (
        "nonpreemptive_release_schedule",
        "On one machine, nonpreemptive jobs A,B,C have (release time,processing time) A=(0,4), B=(1,1), C=(2,1). Idle time is allowed. Minimize the sum of their completion times. What is the minimum sum?",
        "12", "hard", True,
        "Starting A immediately gives completions 4,5,6 and sum 15. Waiting for B then running B,C,A gives completions 2,3,7 and sum 12. The other orders, run as early as their releases permit, give at least 14: B,A,C gives 2,6,7=15; C,B,A gives 3,4,8=15; C,A,B gives 3,7,8=18; A,C,B gives 4,5,6=15. Delaying a fixed order cannot improve its sum.",
    ),
    # Pro 25
    (
        "resource_precedence_bottleneck",
        "Two identical processors execute nonpreemptive tasks. Tasks A,B,C have no prerequisites and durations 3,3,2. Task D lasts 4 and needs both A and B complete. Task E lasts 2 and needs C complete. Task F lasts 1 and needs both D and E complete. All tasks start at or after time zero. What is the minimum makespan?",
        "8", "hard", True,
        "The A-D-F chain gives lower bound 3+4+1=8. Run A,B simultaneously 0-3; run D 3-7 on one processor and C 3-5 then E 5-7 on the other; run F 7-8. Thus 8 is attained.",
    ),
    # Pro 26
    (
        "weighted_tardiness_order",
        "Three jobs on one machine are available at time zero. Their (processing time,deadline,weight) are A=(3,3,4), B=(2,2,2), C=(1,4,5). A schedule is a nonpreemptive permutation with no idle time. Minimize sum of weight*max(0,completion time-deadline). Give the optimal order as three letters with no separators.",
        "ACB", "hard", True,
        "The six weighted tardiness totals are ABC:16, ACB:8, BAC:18, BCA:12, CAB:12, CBA:14. Thus ACB uniquely minimizes the total at 8.",
    ),
    # Pro 27
    (
        "misere_nim_transition",
        "In misere Nim, a move removes any positive number from exactly one heap, but the player removing the last object loses. The heap sizes are (1,1,1,4). Under optimal play, how many objects should the first player remove to force a win?",
        "4", "hard", True,
        "With only singleton heaps remaining, an odd number is losing for the player to move. Remove the entire size-4 heap, leaving three singletons to the opponent. Reducing 4 to 1 leaves four singletons, a winning opponent position; reducing it to 2 or 3 lets the opponent remove that heap and leave three.",
    ),
    # Pro 28
    (
        "dag_grundy_sum",
        "A token game has positions A,B,C,D,E,F. Legal moves are B->A; C->A or B; D->B or C; E->A or D; F->C or E; A has no moves. Play the disjoint sum of two tokens, initially at D and F: each turn moves exactly one token, and a player with no legal move loses. What is the Sprague-Grundy value of this two-token position?",
        "0", "hard", True,
        "Successive mex values are g(A)=0,g(B)=1,g(C)=2,g(D)=mex{1,2}=0,g(E)=mex{0}=1,g(F)=mex{2,1}=0. The disjoint sum has nimber g(D) XOR g(F)=0.",
    ),
    # Pro 29
    (
        "take_ends_optimal_margin",
        "The row [8,15,3,7] is on a table. Players alternate taking either end number and add taken numbers to their own total. Both maximize their final own total; all four numbers must be taken. What is the first player's optimal final total minus the second player's final total?",
        "11", "hard", True,
        "The total is 33. Taking 7 first guarantees 22: if the opponent takes 8, take 15; if the opponent takes 3, again take 15. Taking 8 first lets the opponent take 15, limiting the first player to 15. Thus optimal totals are 22 and 11, with difference 11.",
    ),
    # Pro 30
    (
        "minimax_tree_with_shared_values",
        "At the root MAX chooses Left or Right, then MIN chooses a leaf under that branch. Left leaves have payoffs x and 8-x; Right leaves have payoffs 3 and x-1. The parameter x is an integer from 0 through 8 and is known to both players. How many values of x make Right strictly better for MAX than Left under optimal play?",
        "3", "hard", True,
        "Left's value is min(x,8-x) and Right's is min(3,x-1). For x<=4, Right is never larger. At x=5 both equal 3; at x=6,7,8 Right is 3 and Left is 2,1,0. Thus 3 parameter values work.",
    ),
    # Pro 31
    (
        "absorbing_chain_expected_time",
        "A Markov chain has transient states A,B and absorbing state Z. From A it stays at A with probability 1/2 and goes to B with probability 1/2. From B it goes to A with probability 1/4 and to Z with probability 3/4. Starting at A, what is the expected number of transitions until first reaching Z? Give an integer.",
        "4", "hard", True,
        "Let a,b be expected remaining transitions. a=1+a/2+b/2 implies a=2+b. Also b=1+a/4. Hence a=3+a/4 and a=4.",
    ),
    # Pro 32
    (
        "bayesian_stopping_observation",
        "Choose one of two coins uniformly: coin F has head probability 1/2 and coin G has head probability 3/4. Toss the chosen coin repeatedly until its first tail. You are told only that the stopping time was odd (1,3,5,...), not its actual value. What is the posterior probability the chosen coin was G? Give a reduced fraction.",
        "6/13", "expert", True,
        "For head probability p, P(odd stopping time)=(1-p)sum_{k>=0}p^(2k)=1/(1+p). Thus the likelihoods for F,G are 2/3 and 4/7. Equal priors give (4/7)/(2/3+4/7)=6/13.",
    ),
    # Pro 33
    (
        "random_mapping_two_cycle",
        "Choose a function f:{1,2,3,4}->{1,2,3,4} uniformly from all 4^4 functions. What is the probability that its functional graph contains at least one directed cycle of length exactly two? Give a reduced fraction.",
        "93/256", "hard", True,
        "For each unordered pair {a,b}, the event f(a)=b,f(b)=a fixes two outputs and allows 16 functions. There are six pairs. Intersections only occur for disjoint pairs, with three pairings of all four vertices and one function each. No three events coexist. Inclusion-exclusion gives (6*16-3)/256=93/256.",
    ),
    # Pro 34
    (
        "spanning_trees_deleted_edge",
        "Take the complete simple undirected graph on five labeled vertices and delete one specified edge. How many spanning trees remain?",
        "75", "expert", True,
        "Cayley's formula gives 5^3=125 spanning trees in K5. By edge symmetry, each of its ten edges occurs in 125*4/10=50 trees. Deleting the specified edge removes those 50, leaving 75.",
    ),
    # Pro 35
    (
        "max_flow_cut_certificate",
        "A directed network has capacities S->A:5, S->B:4, A->B:2, A->T:3, B->T:5, and no other edges. What is the maximum S-to-T flow value?",
        "8", "hard", True,
        "The sink incoming capacity bounds flow by 3+5=8. Send S-A=4,S-B=4,A-T=3,A-B=1,B-T=5 to attain 8, with capacity and conservation satisfied.",
    ),
    # Pro 36
    (
        "minimum_feedback_arc_order",
        "A directed graph on A,B,C,D contains A->B, B->C, C->A, A->D, D->C, and B->D. What is the smallest number of edges whose deletion makes it acyclic?",
        "1", "hard", True,
        "The triangle A->B->C->A requires at least one deletion. Delete C->A; the remaining edges all point forward in order A,B,D,C, so one deletion suffices.",
    ),
    # Pro 37
    (
        "automaton_forbidden_substrings",
        "How many binary strings of length 6 contain neither 000 nor 111 as a consecutive substring?",
        "26", "hard", True,
        "Track strings ending in runs of length one and two. At length 1 the counts are (2,0); each step maps (u,v) to (u+v,u). Lengths 2 through 6 give (2,2),(4,2),(6,4),(10,6),(16,10), totaling 26.",
    ),
    # Pro 38
    (
        "edit_distance_unit_cost",
        "Using single-character insertion, deletion, and substitution, each at cost 1, what is the Levenshtein distance from CA to ABC? Adjacent transposition is not an allowed operation.",
        "3", "hard", True,
        "Three edits suffice: substitute C->A, substitute A->B, and insert C. To use only two edits with net length increase one requires exactly one insertion and at most one substitution. With one substitution, the aligned original two positions must match at least one of CA's letters in an order-preserving length-two subsequence of ABC; AB,AC,BC each differ from CA in both positions. Therefore two edits cannot suffice.",
    ),
    # Pro 39
    (
        "matrix_chain_optimal_cost",
        "Four matrices A,B,C,D have dimensions 5x10,10x3,3x12,12x5. Multiplying an r-by-s matrix by an s-by-t matrix costs rst scalar multiplications. What is the minimum total cost over all parenthesizations of ABCD?",
        "405", "hard", True,
        "Pair costs are AB=150,BC=360,CD=180. ABC costs min(360+600,150+180)=330; BCD costs min(180+150,360+600)=330. Full splits cost A|(BCD):330+250=580; (AB)|(CD):150+180+75=405; (ABC)|D:330+300=630. Minimum 405.",
    ),
    # Pro 40
    (
        "optimal_bst_success_only",
        "Three ordered keys a<b<c are searched with probabilities 1/2,1/3,1/6 respectively; unsuccessful searches never occur. In a binary search tree each visited key costs one comparison, including the root. What is the minimum expected number of comparisons? Give a reduced fraction.",
        "5/3", "hard", True,
        "Root b gives depths (2,1,2), expectation 1+1/3+1/3=5/3. Root a with b as right child and c beneath b gives 1/2+2/3+1/2=5/3, while choosing c as that child costs 11/6. Root c's best arrangement gives a at depth 2 and b at depth 3, total 1+1+1/6=13/6. Minimum is 5/3.",
    ),
    # Pro 41
    (
        "two_sat_backbone",
        "Boolean variables p,q,r,s satisfy (p or q), (not p or r), (not q or r), (not r or s), and (not s or p). Which variables are true in every satisfying assignment? Give their lowercase names in alphabetical order, separated by commas.",
        "p,r,s", "hard", True,
        "The first clause forces p or q. Each implies r via the next two clauses, so r is forced. Then r implies s, and s implies p. With p,r,s true either q value satisfies all clauses, so exactly p,r,s are forced.",
    ),
    # Pro 42
    (
        "hall_deficiency_matching",
        "A bipartite graph has workers A,B,C,D,E and jobs 1,2,3,4,5. Allowed worker-job pairs are A:{1,2}, B:{1,2}, C:{1,2}, D:{2,3,4}, E:{4,5}. Each worker and job can appear in at most one matched pair. What is the maximum matching size?",
        "4", "hard", True,
        "Workers A,B,C collectively have only two neighbors, so at least one worker remains unmatched and size is at most 4. The pairs A-1,B-2,D-3,E-5 attain 4.",
    ),
    # Pro 43
    (
        "partition_square_optimization",
        "Partition the integer 12 into positive integer parts, with any positive number of parts allowed. Maximize the product of the parts subject to exactly one part being even. What is the maximum product?",
        "60", "expert", True,
        "Condition on the unique even part e=2,4,6,8,10,12. For each remaining sum s=12-e, maximize a product using odd parts only. The recurrence M(0)=1 and M(s)=max(j*M(s-j) for odd j<=s) gives M(2)=1,M(4)=3,M(6)=9,M(8)=15,M(10)=27. The six full products are therefore 54,60,54,24,10,12. The maximum 60 is attained by parts 4,5,3.",
    ),
    # Pro 44
    (
        "rational_recurrence_limit_free",
        "Let a0=0 and a(n+1)=(2*a(n)+1)/(a(n)+2) for n>=0. What is a5? Give a reduced fraction.",
        "121/122", "hard", True,
        "Set b(n)=(1+a(n))/(1-a(n)). Substitution gives b(n+1)=3*b(n), with b0=1. Thus b5=243 and a5=(243-1)/(243+1)=242/244=121/122.",
    ),
    # Pro 45
    (
        "inclusion_exclusion_onto_dice",
        "Roll a fair six-sided die eight independent times. How many ordered outcome sequences contain every face at least once?",
        "191520", "expert", True,
        "The face multiplicities must be (3,1,1,1,1,1) or (2,2,1,1,1,1). Their counts are 6*8!/3!=40320 and C(6,2)*8!/(2!2!)=151200. Sum 191520.",
    ),
    # Pro 46
    (
        "determinant_low_rank_update",
        "Let I be the 4-by-4 identity, u=(1,2,0,1)^T and v=(2,-1,3,1)^T. What is the determinant of the matrix I+u*v^T?",
        "2", "hard", True,
        "The matrix determinant lemma gives det(I+uv^T)=1+v^T u. The dot product is 2-2+0+1=1, so the determinant is 2.",
    ),
    # Pro 47
    (
        "finite_difference_hidden_value",
        "A polynomial P of degree at most 3 satisfies P(0)=2, P(1)=5, P(2)=12, and P(4)=42. What is P(3)? Give an integer.",
        "24", "hard", True,
        "Write P(x)=ax^3+bx^2+cx+2. The equations give a+b+c=3,4a+2b+c=5,16a+4b+c=10. Subtracting gives 3a+b=2 and 12a+2b=5, hence a=1/6,b=3/2,c=4/3. Then P(3)=27/6+27/2+4+2=24.",
    ),
]
