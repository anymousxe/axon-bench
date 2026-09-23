from textwrap import dedent, indent

ROWS = []


def _add(name, args, contract, difficulty, pro, body, cases):
    prompt = (f"Write Python standard-library-only function {name}({args}). "
              + contract + " Return function code, with any required imports.")
    source = f"def {name}({args}):\n" + indent(dedent(body).strip(), "    ") + "\n"
    ROWS.append((name, prompt, difficulty, pro, source, tuple(cases)))


# Normal bank: independent contracts, with literal oracles.
_add('run_groups', 'text',
     'For a string, return a list of (character, consecutive run length) tuples in encounter order. Empty text returns []. Characters are case-sensitive Unicode code points.',
     'easy', False, '''
    out = []
    for ch in text:
        if out and out[-1][0] == ch:
            out[-1] = (ch, out[-1][1] + 1)
        else:
            out.append((ch, 1))
    return out
''', [(('',), []), (('aaabbca',), [('a', 3), ('b', 2), ('c', 1), ('a', 1)]), (('AaA',), [('A', 1), ('a', 1), ('A', 1)]), (('éé漢',), [('é', 2), ('漢', 1)])])

_add('merge_spans', 'spans',
     'spans is a list of integer closed intervals (lo, hi), lo <= hi. Return sorted merged intervals as tuples; intervals sharing an endpoint merge, but merely adjacent integers do not. Empty returns [].',
     'medium', False, '''
    out = []
    for lo, hi in sorted(spans):
        if out and lo <= out[-1][1]:
            out[-1] = (out[-1][0], max(hi, out[-1][1]))
        else:
            out.append((lo, hi))
    return out
''', [(([],), []), (([(4, 7), (1, 3), (3, 5)],), [(1, 7)]), (([(1, 2), (3, 4)],), [(1, 2), (3, 4)]), (([(2, 2), (0, 6), (0, 1)],), [(0, 6)])])

_add('rank_tokens', 'words, k',
     'Given strings words and nonnegative integer k, return up to k distinct words ranked by descending frequency then ascending Python string order. Empty input or k=0 returns [].',
     'easy', False, '''
    from collections import Counter
    counts = Counter(words)
    return sorted(counts, key=lambda w: (-counts[w], w))[:k]
''', [(([], 3), []), ((['b', 'a', 'b', 'a', 'c'], 2), ['a', 'b']), ((['z'], 0), []), ((['x', 'y', 'x'], 8), ['x', 'y'])])

_add('quarter_turn', 'matrix',
     'Return a rectangular list-of-lists matrix rotated 90 degrees clockwise. Entries are integers. [] and any matrix with zero columns return [].',
     'easy', False, '''
    return [list(row) for row in zip(*matrix[::-1])]
''', [(([],), []), (([[], []],), []), (([[1, 2, 3], [4, 5, 6]],), [[4, 1], [5, 2], [6, 3]]), (([[7]],), [[7]])])

_add('canonical_path', 'path',
     'Normalize an absolute POSIX path string lexically: collapse slashes, ignore . components, and resolve .. without going above root. No filesystem access. Return root as / and otherwise omit trailing slash.',
     'medium', False, '''
    parts = []
    for part in path.split('/'):
        if part == '..':
            if parts:
                parts.pop()
        elif part and part != '.':
            parts.append(part)
    return '/' + '/'.join(parts)
''', [(('/',), '/'), (('/a//b/../c/.',), '/a/c'), (('/../../x',), '/x'), (('/.../a/..',), '/...')])

_add('balanced_delimiters', 'text',
     'Return whether (), [], {} delimiters in text are properly nested. Ignore all other characters (there is no string-literal syntax). Empty is valid.',
     'easy', False, '''
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in text:
        if ch in '([{':
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
''', [(('',), True), (('a{b[c](d)}',), True), (('([)]',), False), (('x(',), False)])

_add('peak_rooms', 'meetings',
     'Return minimum simultaneous rooms for integer half-open intervals (start,end), start <= end. Ignore zero-duration meetings; end at t frees a room for start at t. Empty returns 0.',
     'medium', False, '''
    events = []
    for a, b in meetings:
        if a < b:
            events.extend([(a, 1), (b, -1)])
    used = best = 0
    for _, delta in sorted(events):
        used += delta
        best = max(best, used)
    return best
''', [(([],), 0), (([(0, 2), (2, 4), (1, 3)],), 2), (([(1, 1), (1, 1)],), 0), (([(0, 5), (0, 5), (2, 4)],), 3)])

_add('lex_topology', 'n, edges',
     'Vertices are 0..n-1; directed edges (u,v) may repeat. Return lexicographically smallest topological vertex list or [] if cyclic. Isolated vertices participate; n=0 returns [].',
     'hard', False, '''
    import heapq
    adj = [set() for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        if v not in adj[u]:
            adj[u].add(v)
            indeg[v] += 1
    heap = [u for u in range(n) if not indeg[u]]
    heapq.heapify(heap)
    out = []
    while heap:
        u = heapq.heappop(heap)
        out.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if not indeg[v]:
                heapq.heappush(heap, v)
    return out if len(out) == n else []
''', [((0, []), []), ((4, [(0, 2), (1, 2), (0, 2)]), [0, 1, 2, 3]), ((2, [(0, 1), (1, 0)]), []), ((4, [(3, 0), (0, 1)]), [2, 3, 0, 1])])

_add('component_sizes', 'n, edges',
     'For an undirected graph on 0..n-1, return connected-component sizes sorted descending. Self loops and duplicate edges are allowed; isolated vertices count. n=0 returns [].',
     'medium', False, '''
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = set()
    out = []
    for root in range(n):
        if root in seen:
            continue
        stack = [root]
        seen.add(root)
        size = 0
        while stack:
            u = stack.pop()
            size += 1
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        out.append(size)
    return sorted(out, reverse=True)
''', [((0, []), []), ((4, []), [1, 1, 1, 1]), ((5, [(0, 1), (1, 2), (3, 4)]), [3, 2]), ((3, [(0, 0), (0, 1), (1, 0)]), [2, 1])])

_add('grid_distance', 'grid',
     'grid is a rectangular list of strings of . and #. Return shortest four-neighbor path length in edges from top-left to bottom-right using . cells, or -1 if absent/blocked/unreachable. Empty or zero-width grid returns -1.',
     'medium', False, '''
    from collections import deque
    if not grid or not grid[0] or grid[0][0] == '#' or grid[-1][-1] == '#':
        return -1
    h, w = len(grid), len(grid[0])
    q = deque([(0, 0, 0)])
    seen = {(0, 0)}
    while q:
        r, c, d = q.popleft()
        if (r, c) == (h - 1, w - 1):
            return d
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = r + dr, c + dc
            if 0 <= a < h and 0 <= b < w and grid[a][b] == '.' and (a, b) not in seen:
                seen.add((a, b))
                q.append((a, b, d + 1))
    return -1
''', [(([],), -1), ((['.'],), 0), ((['.#.', '.#.', '...'],), 4), ((['.#', '#.'],), -1)])

_add('fewest_coins', 'coins, amount',
     'For positive integer coin denominations (duplicates allowed) and nonnegative amount, return fewest coins with unlimited supply, or -1 if impossible. amount=0 returns 0, including with no denominations.',
     'medium', False, '''
    dp = [0] + [amount + 1] * amount
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x:
                dp[x] = min(dp[x], dp[x - c] + 1)
    return dp[amount] if dp[amount] <= amount else -1
''', [(([], 0), 0), (([2], 3), -1), (([1, 3, 4], 6), 2), (([2, 2, 5], 9), 3)])

_add('pack_value', 'items, capacity',
     'items are (positive integer weight, integer value), each usable at most once. Return maximum total value of a subset within nonnegative capacity. Selecting nothing is allowed; duplicates represent separate items.',
     'medium', False, '''
    dp = [0] * (capacity + 1)
    for w, v in items:
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]
''', [(([], 5), 0), (([(2, 5), (3, 6), (4, 10)], 6), 15), (([(1, -3), (2, -1)], 3), 0), (([(2, 4), (2, 4)], 3), 4)])

_add('strict_lis', 'values',
     'Return length of the longest strictly increasing subsequence of integer values. Equal elements cannot extend it. Empty returns 0. Support up to 100000 elements in O(n log n).',
     'medium', False, '''
    from bisect import bisect_left
    tails = []
    for x in values:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
''', [(([],), 0), (([2, 2, 2],), 1), (([3, 1, 2, 5, 4, 6],), 4), (([5, 4, 3, 2],), 1)])

_add('unit_edit_distance', 'a, b',
     'Return Levenshtein distance of two strings using unit-cost insertion, deletion, substitution; transposition is not one edit. Compare code points case-sensitively. Empty strings allowed.',
     'medium', False, '''
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        nxt = [i]
        for j, y in enumerate(b, 1):
            nxt.append(min(nxt[-1] + 1, row[j] + 1, row[j - 1] + (x != y)))
        row = nxt
    return row[-1]
''', [(('', 'abc'), 3), (('kitten', 'sitting'), 3), (('ab', 'ba'), 2), (('same', 'same'), 0)])

_add('palindrome_cuts', 'text',
     'Return minimum cuts dividing a string into nonempty palindromic substrings. Empty text returns 0. Case-sensitive code-point comparison. Length at most 500.',
     'hard', False, '''
    n = len(text)
    if not n:
        return 0
    pal = [[False] * n for _ in range(n)]
    cuts = list(range(-1, n))
    for j in range(n):
        for i in range(j + 1):
            if text[i] == text[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                cuts[j + 1] = min(cuts[j + 1], cuts[i] + 1)
    return cuts[n]
''', [(('',), 0), (('aab',), 1), (('abacdc',), 1), (('abcd',), 3)])

_add('best_jobs', 'jobs',
     'jobs are (start,end,profit), integer start < end and integer profit. Return maximum profit from nonoverlapping half-open jobs; touching endpoints are compatible. Taking none is allowed; duplicates are distinct competing jobs.',
     'hard', False, '''
    from bisect import bisect_right
    jobs = sorted(jobs, key=lambda x: x[1])
    ends = [b for a, b, p in jobs]
    dp = [0]
    for i, (a, b, p) in enumerate(jobs):
        k = bisect_right(ends, a, 0, i)
        dp.append(max(dp[-1], dp[k] + p))
    return dp[-1]
''', [(([],), 0), (([(0, 2, 4), (2, 4, 5), (0, 4, 8)],), 9), (([(0, 1, -1)],), 0), (([(0, 3, 6), (1, 2, 4), (2, 3, 4), (3, 5, 2)],), 10)])

_add('window_lower_medians', 'values, k',
     'Return lower median of each consecutive length-k window of integers: index (k-1)//2 in sorted window. k is positive; k>len(values) returns []. Support n<=2000; duplicate values retain multiplicity.',
     'hard', False, '''
    from bisect import bisect_left, insort
    if k > len(values):
        return []
    window = sorted(values[:k])
    out = [window[(k - 1) // 2]]
    for i in range(k, len(values)):
        window.pop(bisect_left(window, values[i - k]))
        insort(window, values[i])
        out.append(window[(k - 1) // 2])
    return out
''', [(([], 1), []), (([3, 1, 4, 2], 2), [1, 1, 2]), (([2, 2, 1, 3], 3), [2, 2]), (([-2, 8], 1), [-2, 8])])

_add('land_perimeter', 'grid',
     'For a rectangular 0/1 integer matrix, return total perimeter of all 1 cells. Every edge bordering a 0 or outside counts, including enclosed holes. Empty and zero-width return 0.',
     'medium', False, '''
    total = 0
    for r, row in enumerate(grid):
        for c, x in enumerate(row):
            if x:
                total += 4
                if r and grid[r - 1][c]:
                    total -= 2
                if c and row[c - 1]:
                    total -= 2
    return total
''', [(([],), 0), (([[1]],), 4), (([[1, 1], [1, 1]],), 8), (([[1, 1, 1], [1, 0, 1], [1, 1, 1]],), 16)])

_add('parse_csv_record', 'record',
     'Parse one valid CSV record with comma delimiter, double-quoted fields, and doubled quotes inside quoted fields. No newline characters. Quoted fields begin at field start and end immediately before comma or record end. Unquoted fields contain no quotes; preserve their whitespace. Return list of strings. Empty record is one empty field, and trailing comma creates an empty field.',
     'medium', False, '''
    out = []
    field = []
    quoted = False
    i = 0
    while i < len(record):
        ch = record[i]
        if ch == '"':
            if quoted and i + 1 < len(record) and record[i + 1] == '"':
                field.append('"')
                i += 1
            else:
                quoted = not quoted
        elif ch == ',' and not quoted:
            out.append(''.join(field))
            field = []
        else:
            field.append(ch)
        i += 1
    return out + [''.join(field)]
''', [(('',), ['']), (('a,b,',), ['a', 'b', '']), (('"a,b","c""d"',), ['a,b', 'c"d']), ((' a ," x "',), [' a ', ' x '])])

_add('eval_postfix', 'tokens',
     'Evaluate a valid nonempty postfix token list containing signed decimal integers and binary +,-,*,/. Division truncates toward zero, with no zero divisors. Return integer; use exact integer arithmetic, not floating point.',
     'medium', False, '''
    stack = []
    for token in tokens:
        if token not in ('+', '-', '*', '/'):
            stack.append(int(token))
            continue
        b, a = stack.pop(), stack.pop()
        if token == '+':
            stack.append(a + b)
        elif token == '-':
            stack.append(a - b)
        elif token == '*':
            stack.append(a * b)
        else:
            stack.append((abs(a) // abs(b)) * (-1 if (a < 0) != (b < 0) else 1))
    return stack[0]
''', [((['42'],), 42), ((['-7', '3', '/'],), -2), ((['2', '3', '+', '4', '*'],), 20), ((['100000000000000000001', '3', '/'],), 33333333333333333333)])

_add('expand_repeats', 'text',
     'Decode valid nested repetition syntax: a sequence of lowercase letters or count[sequence], count is a nonnegative decimal integer. Empty groups and leading zero counts allowed. Return expanded string, whose length is at most 10000.',
     'hard', False, '''
    stack = []
    current = ''
    number = 0
    for ch in text:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch == '[':
            stack.append((current, number))
            current, number = '', 0
        elif ch == ']':
            prefix, count = stack.pop()
            current = prefix + current * count
        else:
            current += ch
    return current
''', [(('',), ''), (('2[a3[b]]x',), 'abbbabbbx'), (('0[abc]2[]z',), 'z'), (('02[ab]c',), 'ababc')])

_add('compare_releases', 'a, b',
     'a,b are nonempty dotted sequences of nonnegative decimal integers. Compare components numerically, treating missing trailing components as zero. Leading zeros are legal. Return -1,0,1 according as a is smaller,equal,larger.',
     'medium', False, '''
    from itertools import zip_longest
    for x, y in zip_longest(map(int, a.split('.')), map(int, b.split('.')), fillvalue=0):
        if x != y:
            return 1 if x > y else -1
    return 0
''', [(('1.02', '1.2.0'), 0), (('1.10', '1.9'), 1), (('0.0.1', '0'), 1), (('3', '3.0.1'), -1)])

_add('prefix_counts', 'words, prefixes',
     'Return for each prefix the number of words beginning with it, counting duplicate words separately. Strings are case-sensitive; empty prefix matches every word, including empty words. Preserve query order.',
     'medium', False, '''
    counts = {'': len(words)}
    for word in words:
        for i in range(1, len(word) + 1):
            p = word[:i]
            counts[p] = counts.get(p, 0) + 1
    return [counts.get(p, 0) for p in prefixes]
''', [(([], ['', 'a']), [0, 0]), ((['a', 'ab', 'a', ''], ['', 'a', 'ab', 'b']), [4, 3, 1, 0]), ((['Cat', 'cat'], ['C', 'c', 'cat']), [1, 1, 1]), ((['xy'], []), [])])

_add('lru_reads', 'capacity, operations',
     'Simulate LRU cache with nonnegative capacity. Operations are ("put",key,value) or ("get",key), with string keys and integer values. Get returns -1 when absent. Both successful get and put mark most-recent; updating does not increase size. Return only get results in order. Capacity zero stores nothing.',
     'medium', False, '''
    from collections import OrderedDict
    cache = OrderedDict()
    out = []
    for op in operations:
        key = op[1]
        if op[0] == 'get':
            out.append(cache.get(key, -1))
            if key in cache:
                cache.move_to_end(key)
        elif capacity:
            cache[key] = op[2]
            cache.move_to_end(key)
            if len(cache) > capacity:
                cache.popitem(last=False)
    return out
''', [((0, [('put', 'a', 2), ('get', 'a')]), [-1]), ((2, [('put', 'a', 1), ('put', 'b', 2), ('get', 'a'), ('put', 'c', 3), ('get', 'b'), ('get', 'c')]), [1, -1, 3]), ((1, [('put', 'a', 1), ('put', 'a', 9), ('get', 'a')]), [9]), ((2, [('get', 'x'), ('get', 'x')]), [-1, -1])])

_add('expiring_reads', 'operations',
     'Simulate expiring key/value storage. Ops are ("set",time,key,value,ttl), ("get",time,key), or ("delete",time,key); integer times are nondecreasing, ttl>=0, keys strings, values integers. Set replaces expiry with time+ttl. A key is live iff query time < expiry. Return get values or None when absent; deletion is silent.',
     'medium', False, '''
    cache = {}
    out = []
    for op in operations:
        kind, time, key = op[:3]
        if kind == 'set':
            cache[key] = (op[3], time + op[4])
        elif kind == 'delete':
            cache.pop(key, None)
        else:
            item = cache.get(key)
            out.append(item[0] if item and time < item[1] else None)
    return out
''', [(([],), []), (([('set', 0, 'a', 4, 2), ('get', 1, 'a'), ('get', 2, 'a')],), [4, None]), (([('set', 0, 'a', 1, 10), ('set', 1, 'a', 2, 0), ('get', 1, 'a')],), [None]), (([('set', 0, 'x', 7, 8), ('delete', 0, 'x'), ('get', 0, 'x'), ('get', 9, 'y')],), [None, None])])

_add('free_spans', 'lo, hi, busy',
     'Within integer half-open horizon [lo,hi), lo<=hi, return maximal free intervals as sorted tuples after subtracting busy half-open intervals (a,b), a<=b. Busy may be overlapping, outside horizon, unsorted, or empty. Omit zero-length results.',
     'medium', False, '''
    out = []
    cursor = lo
    for a, b in sorted(busy):
        a, b = max(a, lo), min(b, hi)
        if a >= b:
            continue
        if a > cursor:
            out.append((cursor, a))
        cursor = max(cursor, b)
    if cursor < hi:
        out.append((cursor, hi))
    return out
''', [((0, 0, []), []), ((0, 10, []), [(0, 10)]), ((0, 10, [(-2, 2), (4, 6), (5, 8), (12, 20)]), [(2, 4), (8, 10)]), ((0, 5, [(0, 3), (3, 5), (2, 2)]), [])])

_add('sparse_product', 'rows, inner, cols, a, b',
     'Multiply sparse integer matrices A(rows x inner) and B(inner x cols). a,b are lists of (row,col,value) triples; duplicate coordinates add, including cancellation. Dimensions nonnegative and coordinates valid. Return nonzero product triples sorted by (row,col); omit zeros.',
     'hard', False, '''
    from collections import defaultdict
    aa = defaultdict(int)
    bb = defaultdict(int)
    for r, c, v in a:
        aa[r, c] += v
    for r, c, v in b:
        bb[r, c] += v
    byrow = defaultdict(list)
    for (r, c), v in bb.items():
        if v:
            byrow[r].append((c, v))
    out = defaultdict(int)
    for (r, k), v in aa.items():
        for c, w in byrow[k]:
            out[r, c] += v * w
    return [(r, c, v) for (r, c), v in sorted(out.items()) if v]
''', [((0, 0, 0, [], []), []), ((1, 1, 1, [(0, 0, 2), (0, 0, -2)], [(0, 0, 5)]), []), ((2, 2, 2, [(0, 0, 2), (0, 1, 3), (1, 1, 4)], [(0, 1, 5), (1, 0, 7)]), [(0, 0, 21), (0, 1, 10), (1, 0, 28)]), ((1, 2, 1, [(0, 0, 1), (0, 1, 1)], [(0, 0, 3), (1, 0, -3)]), [])])

_add('spiral_values', 'matrix',
     'Return rectangular integer matrix entries in clockwise spiral order starting top-left, initially right. Empty and zero-width matrices return []. Each entry appears once.',
     'medium', False, '''
    if not matrix or not matrix[0]:
        return []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    out = []
    while top <= bottom and left <= right:
        out.extend(matrix[top][left:right + 1])
        top += 1
        for r in range(top, bottom + 1):
            out.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            out.extend(matrix[bottom][left:right + 1][::-1])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                out.append(matrix[r][left])
            left += 1
    return out
''', [(([],), []), (([[1, 2, 3]],), [1, 2, 3]), (([[1], [2], [3]],), [1, 2, 3]), (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 3, 6, 9, 8, 7, 4, 5])])

_add('next_strictly_greater', 'values',
     'For each integer in values return the index of the first strictly greater element to its right, or -1. Equal elements do not qualify. Empty returns []. Require O(n) time.',
     'medium', False, '''
    out = [-1] * len(values)
    stack = []
    for i, x in enumerate(values):
        while stack and values[stack[-1]] < x:
            out[stack.pop()] = i
        stack.append(i)
    return out
''', [(([],), []), (([2, 2, 3],), [2, 2, -1]), (([5, 4, 3],), [-1, -1, -1]), (([1, 4, 2, 3, 5],), [1, 4, 3, 4, -1])])

_add('histogram_area', 'heights',
     'Return largest rectangle area under unit-width bars with nonnegative integer heights. Rectangle spans contiguous bars. Empty or all-zero input returns 0. Require O(n) time.',
     'hard', False, '''
    stack = []
    best = 0
    for i, h in enumerate(list(heights) + [0]):
        start = i
        while stack and stack[-1][1] > h:
            j, old = stack.pop()
            best = max(best, old * (i - j))
            start = j
        if not stack or stack[-1][1] < h:
            stack.append((start, h))
    return best
''', [(([],), 0), (([2, 1, 5, 6, 2, 3],), 10), (([2, 2, 2],), 6), (([0, 3, 0, 4],), 4)])

_add('overlapping_matches', 'text, pattern',
     'Return all starting indices where pattern occurs in text, including overlaps. Empty pattern matches every boundary 0..len(text). Case-sensitive strings. Require O(len(text)+len(pattern)+output) time.',
     'medium', False, '''
    if not pattern:
        return list(range(len(text) + 1))
    pi = [0] * len(pattern)
    for i in range(1, len(pattern)):
        j = pi[i - 1]
        while j and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        pi[i] = j
    out = []
    j = 0
    for i, ch in enumerate(text):
        while j and ch != pattern[j]:
            j = pi[j - 1]
        if ch == pattern[j]:
            j += 1
        if j == len(pattern):
            out.append(i - j + 1)
            j = pi[j - 1]
    return out
''', [(('aaa', 'aa'), [0, 1]), (('ab', ''), [0, 1, 2]), (('', 'x'), []), (('ababaabab', 'abab'), [0, 5])])

_add('mutable_range_sums', 'values, operations',
     'Start with integer array values. Operations are ("set",index,value) or ("sum",lo,hi), with valid indices and 0<=lo<=hi<=n. Return sum results for half-open ranges in order. Support 100000 elements/operations with logarithmic updates and queries.',
     'hard', False, '''
    a = list(values)
    tree = [0] * (len(a) + 1)
    def add(i, delta):
        i += 1
        while i < len(tree):
            tree[i] += delta
            i += i & -i
    def prefix(i):
        total = 0
        while i:
            total += tree[i]
            i -= i & -i
        return total
    for i, x in enumerate(a):
        add(i, x)
    out = []
    for op, i, j in operations:
        if op == 'set':
            add(i, j - a[i])
            a[i] = j
        else:
            out.append(prefix(j) - prefix(i))
    return out
''', [(([], [('sum', 0, 0)]), [0]), (([1, 2, 3], [('sum', 0, 3), ('set', 1, -2), ('sum', 0, 2)]), [6, -1]), (([4], [('set', 0, 4), ('sum', 0, 1), ('sum', 1, 1)]), [4, 0]), (([-3, 5, 8], [('sum', 1, 3), ('set', 2, 0), ('sum', 0, 3)]), [13, 2])])

_add('sum_fractions', 'text',
     'Evaluate a nonempty expression consisting of signed integer fractions joined by + or -, with optional ASCII spaces. Each denominator is positive and numerator digits unsigned except its preceding sign. Return reduced n/d string with positive denominator, including 0/1 for zero. No parentheses.',
     'medium', False, '''
    import re
    from fractions import Fraction
    total = Fraction(0)
    for n, d in re.findall(r'([+-]?\\d+)/(\\d+)', text.replace(' ', '')):
        total += Fraction(int(n), int(d))
    return f'{total.numerator}/{total.denominator}'
''', [(('1/2+1/3',), '5/6'), (('-1/2 + 1/2',), '0/1'), (('2/4-5/6',), '-1/3'), (('7/3',), '7/3')])

_add('integer_expression', 'text',
     'Evaluate a valid nonempty integer expression with decimal nonnegative literals, ASCII spaces, binary +,-,*, parentheses, and arbitrarily nested unary +/-. Standard precedence, binary operators left-associative. Return exact integer; do not use eval or exec.',
     'hard', False, '''
    import re
    tokens = re.findall(r'\\d+|[^\\s]', text)
    pos = 0
    def atom():
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if token in ('+', '-'):
            x = atom()
            return x if token == '+' else -x
        if token == '(':
            x = expr()
            pos += 1
            return x
        return int(token)
    def term():
        nonlocal pos
        x = atom()
        while pos < len(tokens) and tokens[pos] == '*':
            pos += 1
            x *= atom()
        return x
    def expr():
        nonlocal pos
        x = term()
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            y = term()
            x = x + y if op == '+' else x - y
        return x
    return expr()
''', [(('0',), 0), (('2+3*4',), 14), (('-(2+3)*--4',), -20), (('10-3-2',), 5)])

_add('ticket_route', 'start, tickets',
     'tickets are directed (origin,destination) string pairs, with duplicates representing distinct tickets. Return lexicographically smallest airport list starting at start and using every ticket once; return [] if impossible. No tickets returns [start]. At most 12 tickets; ties compare entire airport sequences.',
     'expert', False, '''
    from collections import Counter
    counts = Counter(map(tuple, tickets))
    dests = {}
    for a, b in counts:
        dests.setdefault(a, set()).add(b)
    def search(u, left):
        if not left:
            return [u]
        for v in sorted(dests.get(u, ())):
            if counts[u, v]:
                counts[u, v] -= 1
                tail = search(v, left - 1)
                counts[u, v] += 1
                if tail is not None:
                    return [u] + tail
        return None
    result = search(start, len(tickets))
    return result if result is not None else []
''', [(('A', []), ['A']), (('A', [('A', 'B'), ('A', 'C'), ('C', 'A')]), ['A', 'C', 'A', 'B']), (('A', [('A', 'B'), ('A', 'B'), ('B', 'A')]), ['A', 'B', 'A', 'B']), (('A', [('B', 'C')]), [])])

_add('word_steps', 'begin, end, words',
     'Return minimum one-character substitutions turning begin into end, with every word after begin in words. All strings are lowercase and have the same length. Duplicate dictionary entries are irrelevant. Return -1 if impossible; begin==end returns 0 even if absent from words.',
     'hard', False, '''
    from collections import deque
    if begin == end:
        return 0
    unseen = set(words)
    if end not in unseen:
        return -1
    unseen.discard(begin)
    q = deque([(begin, 0)])
    while q:
        word, dist = q.popleft()
        for nxt in list(unseen):
            if sum(a != b for a, b in zip(word, nxt)) == 1:
                if nxt == end:
                    return dist + 1
                unseen.remove(nxt)
                q.append((nxt, dist + 1))
    return -1
''', [(('a', 'a', []), 0), (('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log', 'cog']), 4), (('ab', 'cd', ['cd']), -1), (('ab', 'bb', ['bb', 'bb']), 1)])

_add('alien_alphabet', 'words',
     'words is a list of strings purportedly sorted by an unknown character order. Return lexicographically smallest string ordering all characters that occur, consistent with the list, or None if impossible (including a longer word before its proper prefix). Empty input returns empty string. Repeated words add no constraint.',
     'expert', False, '''
    import heapq
    adj = {ch: set() for w in words for ch in w}
    deg = dict.fromkeys(adj, 0)
    for a, b in zip(words, words[1:]):
        for x, y in zip(a, b):
            if x != y:
                if y not in adj[x]:
                    adj[x].add(y)
                    deg[y] += 1
                break
        else:
            if len(a) > len(b):
                return None
    heap = [ch for ch in deg if deg[ch] == 0]
    heapq.heapify(heap)
    out = []
    while heap:
        ch = heapq.heappop(heap)
        out.append(ch)
        for nxt in adj[ch]:
            deg[nxt] -= 1
            if not deg[nxt]:
                heapq.heappush(heap, nxt)
    return ''.join(out) if len(out) == len(adj) else None
''', [(([],), ''), ((['abc', 'ab'],), None), ((['z', 'x', 'z'],), None), ((['za', 'zb', 'ca', 'cb'],), 'abzc')])

_add('cycle_vertices', 'n, edges',
     'For a directed graph on 0..n-1 return the sorted list of vertices lying on at least one directed cycle. Self-loops qualify, duplicate edges do not change output. n<=150; empty returns [].',
     'hard', False, '''
    reach = [[False] * n for _ in range(n)]
    for u, v in edges:
        reach[u][v] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    reach[i][j] = reach[i][j] or reach[k][j]
    return [i for i in range(n) if reach[i][i]]
''', [((0, []), []), ((4, [(0, 1), (1, 2), (2, 1), (2, 3)]), [1, 2]), ((3, [(0, 0), (1, 2)]), [0]), ((3, [(0, 1), (1, 2)]), [])])

_add('strong_components', 'n, edges',
     'Return strongly connected components of a directed graph on 0..n-1 as sorted vertex lists, sorted lexicographically as lists. Include isolated vertices. Duplicate edges/self-loops allowed. n<=300.',
     'expert', False, '''
    adj = [[] for _ in range(n)]
    rev = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        rev[v].append(u)
    seen, order = set(), []
    def visit(u):
        seen.add(u)
        for v in adj[u]:
            if v not in seen:
                visit(v)
        order.append(u)
    for u in range(n):
        if u not in seen:
            visit(u)
    seen.clear()
    out = []
    for u in reversed(order):
        if u in seen:
            continue
        comp, stack = [], [u]
        seen.add(u)
        while stack:
            v = stack.pop()
            comp.append(v)
            for w in rev[v]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        out.append(sorted(comp))
    return sorted(out)
''', [((0, []), []), ((3, []), [[0], [1], [2]]), ((5, [(0, 1), (1, 0), (1, 2), (2, 3), (3, 2), (3, 4)]), [[0, 1], [2, 3], [4]]), ((2, [(0, 0), (0, 1), (1, 0)]), [[0, 1]])])

_add('bipartite_partition', 'n, edges',
     'For an undirected graph on 0..n-1, return (side0,side1) as sorted lists, or None if not bipartite. In each connected component its smallest vertex must be on side0. Include isolated vertices. Self-loops invalidate; duplicate edges allowed.',
     'medium', False, '''
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = {}
    for root in range(n):
        if root in color:
            continue
        color[root] = 0
        stack = [root]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v in color:
                    if color[v] == color[u]:
                        return None
                else:
                    color[v] = 1 - color[u]
                    stack.append(v)
    return ([u for u in range(n) if color[u] == 0], [u for u in range(n) if color[u] == 1])
''', [((0, []), ([], [])), ((5, [(0, 2), (2, 1), (3, 4)]), ([0, 1, 3], [2, 4])), ((3, [(0, 1), (1, 2), (2, 0)]), None), ((1, [(0, 0)]), None)])

_add('forest_weight', 'n, edges',
     'Return sum of edge weights in a minimum spanning forest of an undirected graph on 0..n-1. Edges are (u,v,integer weight), negative weights, parallel edges and loops allowed. Every original component must be spanned; isolated vertices add zero. Return 0 for n=0.',
     'hard', False, '''
    parent = list(range(n))
    def root(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    total = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        a, b = root(u), root(v)
        if a != b:
            parent[a] = b
            total += w
    return total
''', [((0, []), 0), ((4, [(0, 1, 3), (1, 2, 2), (0, 2, 9)]), 5), ((2, [(0, 0, -9), (0, 1, 4), (0, 1, -2)]), -2), ((4, [(0, 1, 2), (2, 3, -1)]), 1)])

_add('merge_identities', 'groups',
     'groups is a list of lists of email strings. Merge nonempty groups connected by any shared email transitively. Return sorted unique emails per merged group and sort resulting lists lexicographically. Ignore empty groups; no names or case folding.',
     'medium', False, '''
    parent = {}
    def root(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for group in groups:
        for item in group:
            parent[root(item)] = root(group[0])
    merged = {}
    for x in parent:
        merged.setdefault(root(x), []).append(x)
    return sorted(sorted(xs) for xs in merged.values())
''', [(([],), []), (([[], ['a', 'a']],), [['a']]), (([['a', 'b'], ['c'], ['b', 'd'], ['d', 'c']],), [['a', 'b', 'c', 'd']]), (([['z'], ['b', 'a']],), [['a', 'b'], ['z']])])

_add('target_subarrays', 'values, target',
     'Return number of nonempty contiguous subarrays whose sum equals integer target. values may contain negative integers and zeros. Empty returns 0. Require O(n) expected time.',
     'medium', False, '''
    counts = {0: 1}
    prefix = total = 0
    for x in values:
        prefix += x
        total += counts.get(prefix - target, 0)
        counts[prefix] = counts.get(prefix, 0) + 1
    return total
''', [(([], 0), 0), (([0, 0, 0], 0), 6), (([1, -1, 1], 1), 3), (([1, 2, 3], 3), 2)])

_add('minimum_cover', 'text, required',
     'Return shortest substring of text containing every character of required with multiplicity. Break equal-length ties by smallest starting index. Case-sensitive; required empty or no cover returns empty string. Require linear time in input lengths.',
     'hard', False, '''
    from collections import Counter
    if not required:
        return ''
    need = Counter(required)
    missing = len(required)
    left = 0
    best = None
    for right, ch in enumerate(text):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            candidate = (right - left + 1, left)
            if best is None or candidate < best:
                best = candidate
            old = text[left]
            need[old] += 1
            if need[old] > 0:
                missing += 1
            left += 1
    return '' if best is None else text[best[1]:best[1] + best[0]]
''', [(('abc', ''), ''), (('ADOBECODEBANC', 'ABC'), 'BANC'), (('a', 'aa'), ''), (('baacaa', 'aa'), 'aa')])

_add('limited_change_count', 'stocks, amount',
     'stocks is a list of (positive denomination,nonnegative count) with distinct denominations. Return number of ways to form nonnegative amount using at most each count. Order of coins does not matter. Empty stocks forms zero in one way; no modulus.',
     'hard', False, '''
    dp = [1] + [0] * amount
    for coin, count in stocks:
        nxt = [0] * (amount + 1)
        for value in range(amount + 1):
            for used in range(min(count, value // coin) + 1):
                nxt[value] += dp[value - used * coin]
        dp = nxt
    return dp[amount]
''', [(([], 0), 1), (([(1, 2), (2, 2)], 4), 2), (([(3, 1), (5, 0)], 6), 0), (([(1, 0), (2, 2)], 2), 1)])

_add('digit_decodings', 'digits',
     'Given a string of ASCII digits, count decompositions into codes 1..26, with no leading zeros in a code. Empty string has one decomposition. Return exact integer without modulus.',
     'medium', False, '''
    before, current = 0, 1
    for i, ch in enumerate(digits):
        nxt = current if ch != '0' else 0
        if i and 10 <= int(digits[i - 1:i + 1]) <= 26:
            nxt += before
        before, current = current, nxt
    return current
''', [(('',), 1), (('226',), 3), (('100',), 0), (('101',), 1)])

_add('intersect_span_sets', 'a, b',
     'a,b are sorted lists of disjoint nonempty half-open integer intervals, with touching intervals allowed. Return all nonempty pairwise intersections as sorted tuples; do not coalesce touching results. Empty list yields [].',
     'medium', False, '''
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if lo < hi:
            out.append((lo, hi))
        if a[i][1] <= b[j][1]:
            i += 1
        else:
            j += 1
    return out
''', [(([], [(0, 1)]), []), (([(0, 2)], [(2, 3)]), []), (([(0, 5), (7, 9)], [(2, 8)]), [(2, 5), (7, 8)]), (([(0, 2), (2, 4)], [(1, 3)]), [(1, 2), (2, 3)])])

_add('colliding_rocks', 'rocks',
     'Nonzero integers are rocks in left-to-right order; positive moves right, negative left, absolute value is size. Colliding unequal sizes destroy the smaller; equal destroy both. All speeds equal. Return surviving signed integers in order; empty returns [].',
     'medium', False, '''
    stack = []
    for x in rocks:
        alive = True
        while alive and x < 0 and stack and stack[-1] > 0:
            if stack[-1] < -x:
                stack.pop()
            elif stack[-1] == -x:
                stack.pop()
                alive = False
            else:
                alive = False
        if alive:
            stack.append(x)
    return stack
''', [(([],), []), (([5, 10, -5],), [5, 10]), (([8, -8],), []), (([10, 2, -5, -12, 3],), [-12, 3])])

# Pro bank: different problems, not alternate parameterizations of normal tasks.
_add('minimum_assignment', 'costs',
     'costs is an n-by-n matrix of integer costs or None for forbidden worker/job assignments, n<=14. Assign each worker exactly one distinct job. Return (minimum total cost, lexicographically smallest job-index list in worker order among optima), or None if impossible. Empty returns (0,[]).',
     'hard', True, '''
    from functools import lru_cache
    n = len(costs)
    @lru_cache(None)
    def solve(mask):
        i = mask.bit_count()
        if i == n:
            return (0, ())
        best = None
        for j in range(n):
            if not mask >> j & 1 and costs[i][j] is not None:
                tail = solve(mask | 1 << j)
                if tail is not None:
                    candidate = (costs[i][j] + tail[0], (j,) + tail[1])
                    if best is None or candidate < best:
                        best = candidate
        return best
    result = solve(0)
    return None if result is None else (result[0], list(result[1]))
''', [(([],), (0, [])), (([[1, 1], [1, 1]],), (2, [0, 1])), (([[None, 2], [None, 3]],), None), (([[4, 1, 3], [2, 0, 5], [3, 2, 2]],), (5, [1, 0, 2]))])

_add('directed_flow', 'n, edges, source, sink',
     'Return maximum flow in directed graph n>=2, vertices 0..n-1, distinct source/sink. edges=(u,v,nonnegative integer capacity), parallel/antiparallel edges and loops allowed. Sum parallel capacities. n<=50; return integer, zero if disconnected.',
     'hard', True, '''
    from collections import deque
    cap = [[0] * n for _ in range(n)]
    for u, v, c in edges:
        if u != v:
            cap[u][v] += c
    total = 0
    while True:
        parent = [-1] * n
        parent[source] = source
        q = deque([source])
        while q and parent[sink] < 0:
            u = q.popleft()
            for v in range(n):
                if cap[u][v] and parent[v] < 0:
                    parent[v] = u
                    q.append(v)
        if parent[sink] < 0:
            return total
        amount = None
        v = sink
        while v != source:
            u = parent[v]
            amount = cap[u][v] if amount is None else min(amount, cap[u][v])
            v = u
        v = sink
        while v != source:
            u = parent[v]
            cap[u][v] -= amount
            cap[v][u] += amount
            v = u
        total += amount
''', [((2, [], 0, 1), 0), ((2, [(0, 1, 2), (0, 1, 3), (1, 0, 9), (0, 0, 7)], 0, 1), 5), ((4, [(0, 1, 3), (0, 2, 2), (1, 2, 1), (1, 3, 2), (2, 3, 3)], 0, 3), 5), ((3, [(0, 1, 8), (1, 2, 2)], 0, 2), 2)])

_add('canonical_min_cut', 'n, edges',
     'For an undirected graph with 2<=n<=12 and edges (u,v,nonnegative integer weight), return (minimum cut weight, side). side is a sorted proper nonempty vertex list containing vertex 0; choose lexicographically smallest such list among minimum cuts. Parallel edges sum; self-loops never cross.',
     'hard', True, '''
    best = None
    for mask in range(1, 1 << n, 2):
        if mask == (1 << n) - 1:
            continue
        weight = sum(w for u, v, w in edges if ((mask >> u) ^ (mask >> v)) & 1)
        side = [i for i in range(n) if mask >> i & 1]
        candidate = (weight, side)
        if best is None or candidate < best:
            best = candidate
    return best
''', [((2, []), (0, [0])), ((3, [(0, 1, 1), (1, 2, 1), (0, 2, 1)]), (2, [0])), ((3, [(0, 1, 5), (1, 2, 1)]), (1, [0, 1])), ((2, [(0, 1, 2), (1, 0, 3), (0, 0, 99)]), (5, [0]))])

_add('rooted_arborescence_cost', 'n, edges, root',
     'Return minimum cost of a directed spanning out-arborescence rooted at root: root reaches every vertex and every other vertex has one incoming edge. edges=(u,v,integer weight), loops/parallel edges allowed. 1<=n<=6, <=18 edges. Return None if impossible, 0 for singleton; negative weights allowed.',
     'expert', True, '''
    from itertools import product
    incoming = [[] for _ in range(n)]
    for u, v, w in edges:
        if u != v and v != root:
            incoming[v].append((u, w))
    vertices = [v for v in range(n) if v != root]
    best = None
    for chosen in product(*(incoming[v] for v in vertices)):
        parent = {v: item[0] for v, item in zip(vertices, chosen)}
        valid = True
        for v in vertices:
            seen = set()
            while v != root and v not in seen:
                seen.add(v)
                v = parent[v]
            if v != root:
                valid = False
                break
        if valid:
            cost = sum(item[1] for item in chosen)
            best = cost if best is None else min(best, cost)
    return best
''', [((1, [(0, 0, -5)], 0), 0), ((3, [(0, 1, 5), (0, 2, 5), (1, 2, 1), (2, 1, 1)], 0), 6), ((3, [(1, 2, 1), (2, 1, 1)], 0), None), ((3, [(0, 1, 2), (1, 2, -4), (0, 2, 1)], 0), -2)])

_add('steiner_tree_cost', 'n, edges, terminals',
     'Return minimum total edge weight of an undirected connected subgraph containing all terminals, possibly other vertices. n<=10, positive integer weighted edges (u,v,w), parallel edges allowed. Terminals valid, duplicates ignored. Zero or one distinct terminal costs 0; impossible returns None.',
     'expert', True, '''
    required = sum(1 << t for t in set(terminals))
    if required.bit_count() < 2:
        return 0
    best = None
    ordered = sorted(edges, key=lambda e: e[2])
    for mask in range(1 << n):
        if mask & required != required:
            continue
        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x
        cost = used = 0
        for u, v, w in ordered:
            if mask >> u & 1 and mask >> v & 1:
                a, b = find(u), find(v)
                if a != b:
                    parent[a] = b
                    cost += w
                    used += 1
        if used == mask.bit_count() - 1:
            best = cost if best is None else min(best, cost)
    return best
''', [((3, [], []), 0), ((4, [(0, 3, 1), (1, 3, 1), (2, 3, 1), (0, 1, 5)], [0, 1, 2]), 3), ((3, [(0, 1, 1)], [0, 2]), None), ((3, [(0, 1, 2), (1, 2, 3), (0, 2, 9)], [0, 2, 0]), 5)])

_add('required_route', 'n, edges, start, finish, required',
     'Return shortest directed walk cost from start to finish that visits every vertex in required at least once. edges=(u,v,positive integer weight); n<=20, at most 10 distinct required vertices. Repeated vertices/edges allowed. Start and finish visits count; duplicate requirements ignored. Return None if impossible.',
     'hard', True, '''
    import heapq
    bits = {v: 1 << i for i, v in enumerate(sorted(set(required)))}
    full = (1 << len(bits)) - 1
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    mask = bits.get(start, 0)
    dist = {(start, mask): 0}
    heap = [(0, start, mask)]
    while heap:
        cost, u, mask = heapq.heappop(heap)
        if cost != dist[u, mask]:
            continue
        if u == finish and mask == full:
            return cost
        for v, w in adj[u]:
            nxt = mask | bits.get(v, 0)
            if cost + w < dist.get((v, nxt), float('inf')):
                dist[v, nxt] = cost + w
                heapq.heappush(heap, (cost + w, v, nxt))
    return None
''', [((1, [], 0, 0, []), 0), ((3, [(0, 2, 1), (0, 1, 2), (1, 0, 2)], 0, 2, [1]), 5), ((3, [(0, 2, 1)], 0, 2, [1]), None), ((3, [(0, 1, 2), (1, 2, 3)], 0, 2, [0, 2, 2]), 5)])

_add('second_walk_length', 'n, edges, start, finish',
     'In a directed graph edges=(u,v,positive integer weight), return second smallest DISTINCT cost among walks from start to finish, or None if fewer than two costs exist. Walks may repeat vertices/edges; parallel edges do not by themselves make equal costs distinct. The empty walk counts when start==finish. n<=100.',
     'expert', True, '''
    import heapq
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    accepted = [[] for _ in range(n)]
    heap = [(0, start)]
    while heap:
        cost, u = heapq.heappop(heap)
        if cost in accepted[u] or len(accepted[u]) == 2:
            continue
        accepted[u].append(cost)
        if u == finish and len(accepted[u]) == 2:
            return cost
        for v, w in adj[u]:
            heapq.heappush(heap, (cost + w, v))
    return None
''', [((1, [], 0, 0), None), ((2, [(0, 1, 3), (0, 1, 3)], 0, 1), None), ((2, [(0, 1, 2), (1, 0, 1)], 0, 1), 5), ((3, [(0, 2, 3), (0, 1, 2), (1, 2, 2)], 0, 2), 4)])

_add('bridge_edge_ids', 'n, edges',
     'For an undirected multigraph on 0..n-1, edges are (u,v) in input order. Return sorted input indices of bridges: deleting that one edge increases connected-component count. Parallel edges and loops allowed. n<=300; disconnected and empty graphs valid.',
     'hard', True, '''
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin = [-1] * n
    low = [0] * n
    clock = 0
    out = []
    def dfs(u, parent_edge):
        nonlocal clock
        tin[u] = low[u] = clock
        clock += 1
        for v, eid in adj[u]:
            if eid == parent_edge:
                continue
            if tin[v] >= 0:
                low[u] = min(low[u], tin[v])
            else:
                dfs(v, eid)
                low[u] = min(low[u], low[v])
                if low[v] > tin[u]:
                    out.append(eid)
    for u in range(n):
        if tin[u] < 0:
            dfs(u, -1)
    return sorted(out)
''', [((0, []), []), ((2, [(0, 1), (0, 1), (0, 0)]), []), ((4, [(0, 1), (1, 2), (2, 0), (2, 3)]), [3]), ((5, [(0, 1), (2, 3), (3, 4)]), [0, 1, 2])])

_add('dynamic_connectivity', 'n, operations',
     'Maintain undirected edge multiplicities on vertices 0..n-1, initially empty. Ops=("add",u,v),("remove",u,v),("ask",u,v). Remove subtracts one copy, and is ignored if absent. Return bool results of ask, with each vertex connected to itself. Self-loops legal; n<=60, <=500 ops.',
     'hard', True, '''
    from collections import Counter
    counts = Counter()
    out = []
    for op, u, v in operations:
        edge = tuple(sorted((u, v)))
        if op == 'add':
            counts[edge] += 1
        elif op == 'remove':
            if counts[edge]:
                counts[edge] -= 1
        else:
            seen = {u}
            stack = [u]
            while stack:
                x = stack.pop()
                for (a, b), count in counts.items():
                    if count and (a == x or b == x):
                        y = b if a == x else a
                        if y not in seen:
                            seen.add(y)
                            stack.append(y)
            out.append(v in seen)
    return out
''', [((1, [('ask', 0, 0)]), [True]), ((2, [('add', 0, 1), ('add', 1, 0), ('remove', 0, 1), ('ask', 0, 1), ('remove', 1, 0), ('ask', 0, 1)]), [True, False]), ((3, [('add', 0, 1), ('add', 1, 2), ('ask', 0, 2), ('remove', 1, 2), ('ask', 0, 2)]), [True, False]), ((2, [('remove', 0, 1), ('ask', 0, 1)]), [False])])

_add('difference_feasible', 'n, constraints',
     'constraints are (u,v,w) meaning real variables x[v]-x[u]<=integer w, indices 0..n-1. Return whether all can hold simultaneously. No variable is fixed. Self constraints and duplicates allowed; n<=100. Empty system, including n=0, is feasible.',
     'hard', True, '''
    dist = [0] * n
    for step in range(n):
        changed = False
        for u, v, w in constraints:
            if dist[v] > dist[u] + w:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            return True
    return not changed if n else True
''', [((0, []), True), ((2, [(0, 1, 3), (1, 0, -3)]), True), ((2, [(0, 1, 2), (1, 0, -3)]), False), ((3, [(2, 2, -1)]), False)])

_add('tree_independent_weight', 'weights, edges',
     'weights are integer vertex weights and edges undirected pairs forming a forest on 0..len(weights)-1, no loops/duplicates. Return maximum weight of a vertex subset containing no adjacent pair; choosing nothing allowed. Up to 500 vertices; disconnected/empty valid.',
     'hard', True, '''
    n = len(weights)
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = set()
    def dfs(u, parent):
        seen.add(u)
        take, skip = weights[u], 0
        for v in adj[u]:
            if v != parent:
                a, b = dfs(v, u)
                take += b
                skip += max(a, b)
        return take, skip
    total = 0
    for u in range(n):
        if u not in seen:
            total += max(dfs(u, -1))
    return total
''', [(([], []), 0), (([-3, -1], [(0, 1)]), 0), (([5, 8, 5], [(0, 1), (1, 2)]), 10), (([2, 9, 2, 4], [(0, 1), (1, 2)]), 13)])

_add('tree_farthest_pair', 'n, edges',
     'edges=(u,v,nonnegative integer weight) form a tree on 0..n-1, n>=1. Return (maximum path weight,(a,b)) with a<=b, breaking ties by smallest (a,b). A vertex-to-itself zero path is allowed. n<=300; zero-weight edges require correct endpoint tie-breaking.',
     'hard', True, '''
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    best = (0, (0, 0))
    for a in range(n):
        stack = [(a, -1, 0)]
        while stack:
            u, parent, dist = stack.pop()
            if u >= a and (dist > best[0] or dist == best[0] and (a, u) < best[1]):
                best = (dist, (a, u))
            for v, w in adj[u]:
                if v != parent:
                    stack.append((v, u, dist + w))
    return best
''', [((1, []), (0, (0, 0))), ((3, [(0, 1, 0), (1, 2, 0)]), (0, (0, 0))), ((4, [(0, 1, 2), (0, 2, 2), (0, 3, 2)]), (4, (1, 2))), ((3, [(0, 1, 2), (1, 2, 5)]), (7, (0, 2)))])

_add('polynomial_inverse', 'coefficients, length, prime',
     'Return first length coefficients of the formal power-series inverse of coefficients modulo prime: product is 1 modulo x**length. coefficients is a nonempty integer list with first coefficient nonzero modulo prime; prime is prime, length>=0 and <=300. Coefficients beyond input are zero. Return residues 0..prime-1; length=0 returns [].',
     'hard', True, '''
    if not length:
        return []
    inv = pow(coefficients[0], -1, prime)
    out = [inv]
    for k in range(1, length):
        total = sum(coefficients[i] * out[k - i] for i in range(1, min(k + 1, len(coefficients))))
        out.append(-inv * total % prime)
    return out
''', [(([1, 2], 0, 7), []), (([1, -1], 5, 7), [1, 1, 1, 1, 1]), (([2], 4, 7), [4, 0, 0, 0]), (([1, 1, 1], 6, 5), [1, 4, 0, 1, 4, 0])])

_add('recurrence_term', 'initial, coefficients, index, modulus',
     'For k>=1, initial has k integers f[0..k-1], coefficients has k integers c where f[t]=sum(c[j]*f[t-1-j],j=0..k-1). Return f[index] modulo positive modulus. index>=0 up to 10**18, k<=12. Use logarithmic dependence on index; modulus may be composite or 1.',
     'expert', True, '''
    k = len(initial)
    if index < k:
        return initial[index] % modulus
    def multiply(a, b):
        out = [[0] * k for _ in range(k)]
        for i in range(k):
            for j in range(k):
                if a[i][j]:
                    for t in range(k):
                        out[i][t] = (out[i][t] + a[i][j] * b[j][t]) % modulus
        return out
    base = [[x % modulus for x in coefficients]] + [[int(j == i - 1) for j in range(k)] for i in range(1, k)]
    result = [[int(i == j) for j in range(k)] for i in range(k)]
    power = index - k + 1
    while power:
        if power & 1:
            result = multiply(result, base)
        base = multiply(base, base)
        power //= 2
    return sum(result[0][j] * initial[k - 1 - j] for j in range(k)) % modulus
''', [(([0, 1], [1, 1], 10, 1000), 55), (([3], [2], 4, 100), 48), (([5, 8], [1, 1], 0, 7), 5), (([9], [1], 1000000000000000000, 1), 0)])

_add('combined_congruence', 'congruences',
     'Given (residue,positive modulus) integer pairs, return (smallest nonnegative solution, least positive common period) solving all congruences, or None if inconsistent. Moduli need not be coprime; negative residues allowed. Empty returns (0,1).',
     'hard', True, '''
    from math import gcd
    value, period = 0, 1
    for residue, modulus in congruences:
        g = gcd(period, modulus)
        if (residue - value) % g:
            return None
        reduced = modulus // g
        step = ((residue - value) // g * pow(period // g, -1, reduced)) % reduced if reduced > 1 else 0
        value += period * step
        period *= reduced
        value %= period
    return value, period
''', [(([],), (0, 1)), (([(2, 6), (5, 9)],), (14, 18)), (([(0, 2), (1, 4)],), None), (([(-1, 4), (3, 8), (0, 1)],), (3, 8))])

_add('rational_system', 'matrix, rhs',
     'matrix is m-by-n integers with m>=1 and n>=1; rhs has m integers. Solve matrix*x=rhs over rationals. Return "inconsistent" if no solution, "multiple" if more than one, otherwise a list of reduced "numerator/denominator" strings (including /1). m,n<=12; overdetermined systems allowed.',
     'expert', True, '''
    from fractions import Fraction
    m, n = len(matrix), len(matrix[0])
    a = [[Fraction(x) for x in row] + [Fraction(y)] for row, y in zip(matrix, rhs)]
    pivot_cols = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        scale = a[r][c]
        a[r] = [x / scale for x in a[r]]
        for i in range(m):
            if i != r:
                scale = a[i][c]
                a[i] = [x - scale * y for x, y in zip(a[i], a[r])]
        pivot_cols.append(c)
        r += 1
        if r == m:
            break
    if any(not any(row[:n]) and row[n] for row in a):
        return 'inconsistent'
    if r < n:
        return 'multiple'
    out = [None] * n
    for i, c in enumerate(pivot_cols):
        x = a[i][n]
        out[c] = f'{x.numerator}/{x.denominator}'
    return out
''', [(([[2]], [1]), ['1/2']), (([[1, 1], [2, 2]], [1, 2]), 'multiple'), (([[1, 1], [2, 2]], [1, 3]), 'inconsistent'), (([[1, 1], [1, -1], [2, 0]], [3, 1, 4]), ['2/1', '1/1'])])

_add('integer_determinant', 'matrix',
     'Return exact integer determinant of a square integer matrix, dimension <=30. Empty matrix determinant is 1. Singular matrices and row swaps must be handled; no floating-point arithmetic.',
     'hard', True, '''
    from fractions import Fraction
    n = len(matrix)
    a = [[Fraction(x) for x in row] for row in matrix]
    det = Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if a[r][c]), None)
        if p is None:
            return 0
        if p != c:
            a[c], a[p] = a[p], a[c]
            det = -det
        pivot = a[c][c]
        det *= pivot
        for r in range(c + 1, n):
            scale = a[r][c] / pivot
            for j in range(c + 1, n):
                a[r][j] -= scale * a[c][j]
    return int(det)
''', [(([],), 1), (([[0, 2], [3, 4]],), -6), (([[1, 2], [2, 4]],), 0), (([[2, 1, 0], [0, 3, 1], [1, 0, 4]],), 25)])

_add('rational_rpn_program', 'program',
     'Execute tokens on an initially empty rational stack. Tokens are integer strings, +,-,*,/ (pop b then a), dup (copy top), swap (exchange top two), drop (discard top). Return the entire final stack bottom-to-top as reduced n/d strings. Return None on unknown token, stack underflow or division by zero, immediately. Empty returns []. Integers may have a leading + or -; no whitespace inside a token.',
     'hard', True, '''
    from fractions import Fraction
    import re
    stack = []
    for token in program:
        if re.fullmatch(r'[+-]?\\d+', token):
            stack.append(Fraction(int(token)))
        elif token in ('dup', 'drop'):
            if not stack:
                return None
            if token == 'dup':
                stack.append(stack[-1])
            else:
                stack.pop()
        elif token in ('swap', '+', '-', '*', '/'):
            if len(stack) < 2:
                return None
            if token == 'swap':
                stack[-1], stack[-2] = stack[-2], stack[-1]
                continue
            b, a = stack.pop(), stack.pop()
            if token == '/' and not b:
                return None
            stack.append(a + b if token == '+' else a - b if token == '-' else a * b if token == '*' else a / b)
        else:
            return None
    return [f'{x.numerator}/{x.denominator}' for x in stack]
''', [(([],), []), ((['2', '3', '/', 'dup', '*', '5', 'swap'],), ['5/1', '4/9']), ((['1', '0', '/'],), None), ((['2', 'drop', 'dup'],), None), ((['2', 'wat'],), None)])

_add('restricted_regex', 'text, pattern',
     'Return whether the whole lowercase text matches valid regex pattern using lowercase literals, . for any one character, and postfix * for zero or more copies of the preceding atom. No other syntax, no leading * or repeated *. Empty text/pattern allowed. Lengths <=200. Do not use regex libraries.',
     'hard', True, '''
    from functools import lru_cache
    @lru_cache(None)
    def match(i, j):
        if j == len(pattern):
            return i == len(text)
        first = i < len(text) and pattern[j] in ('.', text[i])
        if j + 1 < len(pattern) and pattern[j + 1] == '*':
            return match(i, j + 2) or first and match(i + 1, j)
        return first and match(i + 1, j + 1)
    return match(0, 0)
''', [(('', 'a*b*'), True), (('aab', 'c*a*b'), True), (('mississippi', 'mis*is*p*.'), False), (('ab', '.*c'), False), (('', ''), True)])

_add('boolean_parenthesizations', 'expression',
     'expression is a valid alternating sequence of literals T/F and binary &,|,^, no spaces or parentheses. Return (number evaluating False, number evaluating True) across all full binary parenthesizations, with no operator precedence. Empty returns (0,0). At most 20 literals; exact counts.',
     'hard', True, '''
    from functools import lru_cache
    if not expression:
        return (0, 0)
    @lru_cache(None)
    def solve(lo, hi):
        if lo == hi:
            return (int(expression[lo] == 'F'), int(expression[lo] == 'T'))
        out = [0, 0]
        for k in range(lo + 1, hi, 2):
            left, right = solve(lo, k - 1), solve(k + 1, hi)
            for a in (0, 1):
                for b in (0, 1):
                    value = a & b if expression[k] == '&' else a | b if expression[k] == '|' else a ^ b
                    out[value] += left[a] * right[b]
        return tuple(out)
    return solve(0, len(expression) - 1)
''', [(('',), (0, 0)), (('T',), (0, 1)), (('T|F&T',), (0, 2)), (('T^T&T',), (2, 0)), (('F&T|T',), (1, 1))])

_add('scramble_equivalent', 'a, b',
     'Return whether equal-length strings are scramble-equivalent: recursively split a string at any interior position, independently scramble both pieces, and optionally swap their order. Zero or more splits; compare case-sensitively. Unequal lengths return False; empty pair True. Length <=25.',
     'expert', True, '''
    from functools import lru_cache
    @lru_cache(None)
    def solve(x, y):
        if x == y:
            return True
        if sorted(x) != sorted(y):
            return False
        for k in range(1, len(x)):
            if solve(x[:k], y[:k]) and solve(x[k:], y[k:]):
                return True
            if solve(x[:k], y[-k:]) and solve(x[k:], y[:-k]):
                return True
        return False
    return len(a) == len(b) and solve(a, b)
''', [(('', ''), True), (('great', 'rgeat'), True), (('abcde', 'caebd'), False), (('a', 'aa'), False)])

_add('insert_palindrome', 'text',
     'Return the shortest palindrome obtainable by inserting characters anywhere into text, without deleting/reordering original characters. Among shortest results choose lexicographically smallest Python string. Empty returns empty. Length <=120.',
     'hard', True, '''
    from functools import lru_cache
    @lru_cache(None)
    def solve(i, j):
        if i > j:
            return ''
        if i == j:
            return text[i]
        if text[i] == text[j]:
            return text[i] + solve(i + 1, j - 1) + text[j]
        options = [text[i] + solve(i + 1, j) + text[i], text[j] + solve(i, j - 1) + text[j]]
        return min(options, key=lambda s: (len(s), s))
    return solve(0, len(text) - 1)
''', [(('',), ''), (('ab',), 'aba'), (('race',), 'ecarace'), (('aba',), 'aba')])

_add('canonical_supersequence', 'a, b',
     'Return shortest string containing both a and b as subsequences (not necessarily contiguous), breaking ties lexicographically. Strings case-sensitive, lengths <=100. Empty inputs allowed.',
     'hard', True, '''
    from functools import lru_cache
    @lru_cache(None)
    def solve(i, j):
        if i == len(a):
            return b[j:]
        if j == len(b):
            return a[i:]
        if a[i] == b[j]:
            return a[i] + solve(i + 1, j + 1)
        choices = [a[i] + solve(i + 1, j), b[j] + solve(i, j + 1)]
        return min(choices, key=lambda s: (len(s), s))
    return solve(0, 0)
''', [(('', 'xy'), 'xy'), (('ab', 'ba'), 'aba'), (('abac', 'cab'), 'cabac'), (('aa', 'aa'), 'aa')])

_add('shortest_superstring', 'words',
     'Return shortest string containing every supplied word as a contiguous substring, tie-breaking lexicographically. Duplicate/empty/contained words impose no extra obligation. At most 9 words, each <=12 characters. Empty list returns empty string.',
     'expert', True, '''
    from functools import lru_cache
    words = sorted(set(words))
    words = [w for w in words if not any(w != v and w in v for v in words)]
    n = len(words)
    if not n:
        return ''
    overlap = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(1, min(len(words[i]), len(words[j])) + 1):
                if words[i][-k:] == words[j][:k]:
                    overlap[i][j] = k
    @lru_cache(None)
    def solve(mask, last):
        if mask == (1 << n) - 1:
            return ''
        choices = []
        for nxt in range(n):
            if not mask >> nxt & 1:
                choices.append(words[nxt][overlap[last][nxt]:] + solve(mask | 1 << nxt, nxt))
        return min(choices, key=lambda s: (len(s), s))
    return min((words[i] + solve(1 << i, i) for i in range(n)), key=lambda s: (len(s), s))
''', [(([],), ''), ((['abc', 'b', 'abc', ''],), 'abc'), ((['ab', 'ba'],), 'aba'), ((['catg', 'atgc', 'tgca'],), 'catgca')])

_add('cheapest_tokenization', 'text, entries',
     'entries are (nonempty word,nonnegative integer cost), duplicate words allowed with potentially different costs. Segment all of text into entries. Return (minimum cost, word list), choosing lexicographically smallest word list among equal costs (Python list comparison). Return None if impossible; empty text returns (0,[]). Length<=200.',
     'hard', True, '''
    from functools import lru_cache
    prices = {}
    for word, cost in entries:
        prices[word] = min(prices.get(word, cost), cost)
    @lru_cache(None)
    def solve(i):
        if i == len(text):
            return (0, ())
        best = None
        for word, cost in prices.items():
            if text.startswith(word, i):
                tail = solve(i + len(word))
                if tail is not None:
                    option = (cost + tail[0], (word,) + tail[1])
                    if best is None or option < best:
                        best = option
        return best
    result = solve(0)
    return None if result is None else (result[0], list(result[1]))
''', [(('', []), (0, [])), (('aa', [('a', 1), ('aa', 2)]), (2, ['a', 'a'])), (('abc', [('ab', 1)]), None), (('aba', [('a', 3), ('ab', 2), ('ba', 1), ('a', 1)]), (2, ['a', 'ba']))])

_add('repair_brackets', 'text',
     'text contains only ()[]. Delete the fewest characters so remaining brackets are properly nested. Return all distinct optimal strings sorted lexicographically. Empty returns [empty string]. Length<=14; no substitutions/reordering.',
     'expert', True, '''
    def valid(s):
        stack = []
        for ch in s:
            if ch in '([':
                stack.append(ch)
            elif not stack or stack.pop() != ( '(' if ch == ')' else '[' ):
                return False
        return not stack
    level = {text}
    while True:
        good = sorted(s for s in level if valid(s))
        if good:
            return good
        level = {s[:i] + s[i + 1:] for s in level for i in range(len(s))}
''', [(('',), ['']), (('([)]',), ['()', '[]']), (('(()',), ['()']), (('][',), [''])])

_add('wildcard_bracket_count', 'text',
     'text consists of (,),?; each ? must become exactly one of ( or ), not empty. Return number of replacements yielding balanced parentheses, modulo 1000000007. Empty has one replacement. Length<=500; fixed invalid prefixes cannot be repaired later.',
     'hard', True, '''
    dp = {0: 1}
    for ch in text:
        nxt = {}
        for balance, count in dp.items():
            if ch in '(?':
                nxt[balance + 1] = (nxt.get(balance + 1, 0) + count) % 1000000007
            if ch in ')?' and balance:
                nxt[balance - 1] = (nxt.get(balance - 1, 0) + count) % 1000000007
        dp = nxt
    return dp.get(0, 0)
''', [(('',), 1), (('????',), 2), ((')?',), 0), (('(?))',), 1), (('???',), 0)])

_add('packet_sort', 'packets',
     'A packet is an integer or recursively nested list of packets, depth<=50. Compare integers numerically; when one operand is an integer promote it to a singleton list; lists compare elementwise recursively then shorter first. Return input indices in stable sorted order under this comparator. Equivalent packets retain input order; empty returns [].',
     'hard', True, '''
    from functools import cmp_to_key
    def compare(a, b):
        if isinstance(a, int) and isinstance(b, int):
            return (a > b) - (a < b)
        if isinstance(a, int):
            a = [a]
        if isinstance(b, int):
            b = [b]
        for x, y in zip(a, b):
            result = compare(x, y)
            if result:
                return result
        return (len(a) > len(b)) - (len(a) < len(b))
    return sorted(range(len(packets)), key=cmp_to_key(lambda i, j: compare(packets[i], packets[j])))
''', [(([],), []), (([2, [2], [[2]], 1],), [3, 0, 1, 2]), (([[1, 2], [1], [], [1, 1]],), [2, 1, 3, 0]), (([[[-1]], -2, [[0]], []],), [3, 1, 0, 2])])

_add('chemical_inventory', 'formula',
     'Parse a valid chemical formula of element symbols (ASCII uppercase followed by zero or more lowercase letters), positive decimal multipliers, and nested parentheses. A missing multiplier is 1; no hydrate dots or charges. Return sorted (element,count) tuples. Empty formula returns []; depth<=50.',
     'hard', True, '''
    import re
    from collections import Counter
    tokens = re.findall(r'[A-Z][a-z]*|\\d+|[()]', formula)
    stack = [Counter()]
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == '(':
            stack.append(Counter())
            i += 1
            continue
        current = stack.pop() if token == ')' else Counter({token: 1})
        i += 1
        count = 1
        if i < len(tokens) and tokens[i].isdigit():
            count = int(tokens[i])
            i += 1
        for element, amount in current.items():
            stack[-1][element] += amount * count
    return sorted(stack[0].items())
''', [(('',), []), (('H2O',), [('H', 2), ('O', 1)]), (('K4(ON(SO3)2)2',), [('K', 4), ('N', 2), ('O', 14), ('S', 4)]), (('Mg(OH)2Mg',), [('H', 2), ('Mg', 2), ('O', 2)])])

_add('pointer_updates', 'document, operations',
     'Apply valid JSON-pointer-like updates to a JSON-compatible document. Operations=("set",pointer,value) or ("remove",pointer). Empty pointer replaces root for set and makes root None for remove. Nonempty pointers split on /; decode ~1 to / and ~0 to ~ in that order. Intermediate containers exist. Dict set adds/replaces keys; list set replaces valid index, except final - appends. Remove targets exist and list deletion shifts indices. Return final document. No mutation guarantee is requested.',
     'hard', True, '''
    import copy
    root = copy.deepcopy(document)
    for op in operations:
        kind, pointer = op[:2]
        if pointer == '':
            root = copy.deepcopy(op[2]) if kind == 'set' else None
            continue
        parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer[1:].split('/')]
        current = root
        for key in parts[:-1]:
            current = current[int(key)] if isinstance(current, list) else current[key]
        key = parts[-1]
        if isinstance(current, list):
            if kind == 'remove':
                current.pop(int(key))
            elif key == '-':
                current.append(copy.deepcopy(op[2]))
            else:
                current[int(key)] = copy.deepcopy(op[2])
        elif kind == 'remove':
            del current[key]
        else:
            current[key] = copy.deepcopy(op[2])
    return root
''', [(({'a': 1}, []), {'a': 1}), (({'a/b': {'~x': 1}}, [('set', '/a~1b/~0x', 4)]), {'a/b': {'~x': 4}}), (([1, 2, 3], [('remove', '/1'), ('set', '/-', 9), ('set', '/0', 5)]), [5, 3, 9]), (({'a': 2}, [('set', '', [7]), ('remove', '')]), None), (({'': 1}, [('set', '/', 2)]), {'': 2})])

_add('savepoint_store', 'operations',
     'Start with an empty string-to-integer map and a stack of snapshots. Ops=("set",key,value),("delete",key),("get",key),("begin",),("commit",),("rollback",). begin snapshots current map. commit discards newest snapshot but keeps current values; rollback restores and pops newest snapshot. Commit/rollback without a snapshot do nothing. Delete missing key does nothing. Return get results, absent as None. Nested transactions supported.',
     'hard', True, '''
    store, stack, out = {}, [], []
    for op in operations:
        kind = op[0]
        if kind == 'set':
            store[op[1]] = op[2]
        elif kind == 'delete':
            store.pop(op[1], None)
        elif kind == 'get':
            out.append(store.get(op[1]))
        elif kind == 'begin':
            stack.append(store.copy())
        elif kind == 'commit' and stack:
            stack.pop()
        elif kind == 'rollback' and stack:
            store = stack.pop()
    return out
''', [(([('get', 'x'), ('rollback',), ('commit',)],), [None]), (([('set', 'x', 1), ('begin',), ('set', 'x', 2), ('rollback',), ('get', 'x')],), [1]), (([('begin',), ('set', 'x', 1), ('begin',), ('set', 'x', 2), ('commit',), ('get', 'x'), ('rollback',), ('get', 'x')],), [2, None]), (([('set', 'x', 3), ('begin',), ('delete', 'x'), ('commit',), ('get', 'x')],), [None])])

_add('optimal_cache_misses', 'requests, capacity',
     'requests is a sequence of integer page IDs, cache initially empty, nonnegative capacity. On a miss requested page must be loaded (unless capacity=0); when full any resident page may be evicted at no cost. Return minimum possible misses with future knowledge. Every request at capacity zero misses. At most 2000 requests.',
     'hard', True, '''
    from collections import defaultdict, deque
    future = defaultdict(deque)
    for i, page in enumerate(requests):
        future[page].append(i)
    cache = set()
    misses = 0
    for i, page in enumerate(requests):
        future[page].popleft()
        if page in cache:
            continue
        misses += 1
        if capacity == 0:
            continue
        if len(cache) == capacity:
            victim = max(cache, key=lambda p: future[p][0] if future[p] else len(requests))
            cache.remove(victim)
        cache.add(page)
    return misses
''', [(([], 2), 0), (([1, 1, 2], 0), 3), (([1, 2, 3, 1, 2, 3], 2), 4), (([1, 1, 2, 1], 1), 3)])

_add('shortest_remaining_schedule', 'jobs',
     'jobs are (nonnegative integer arrival,positive integer duration), ID=input index. One CPU always runs available job with shortest remaining duration, ties by smaller ID, preempting at arrivals. Return completion times in input order. Idle until next arrival if needed. Empty returns []; times may be large, so jump between events, not ticks.',
     'expert', True, '''
    import heapq
    pending = sorted((a, i, d) for i, (a, d) in enumerate(jobs))
    heap, done = [], [0] * len(jobs)
    i = time = 0
    while i < len(pending) or heap:
        if not heap:
            time = max(time, pending[i][0])
        while i < len(pending) and pending[i][0] <= time:
            a, ident, duration = pending[i]
            heapq.heappush(heap, (duration, ident))
            i += 1
        remaining, ident = heapq.heappop(heap)
        step = remaining if i == len(pending) else min(remaining, pending[i][0] - time)
        remaining -= step
        time += step
        if remaining:
            heapq.heappush(heap, (remaining, ident))
        else:
            done[ident] = time
    return done
''', [(([],), []), (([(4, 3)],), [7]), (([(0, 8), (1, 2), (2, 1)],), [11, 3, 4]), (([(0, 2), (0, 2), (1, 1)],), [2, 5, 3])])

_add('precedence_completion_cost', 'durations, weights, edges',
     'Schedule all jobs nonpreemptively on one machine from time zero, no idle time; edges=(u,v) require u before v. durations are positive integers, weights nonnegative, same length n<=16. Return minimum sum(weights[i]*completion_time[i]), or None if precedence graph cyclic. Empty returns 0; duplicate edges allowed.',
     'expert', True, '''
    n = len(durations)
    pred = [0] * n
    for u, v in edges:
        pred[v] |= 1 << u
    size = 1 << n
    elapsed = [0] * size
    dp = [None] * size
    dp[0] = 0
    for mask in range(1, size):
        bit = mask & -mask
        elapsed[mask] = elapsed[mask ^ bit] + durations[bit.bit_length() - 1]
    for mask in range(size):
        if dp[mask] is None:
            continue
        for i in range(n):
            if not mask >> i & 1 and pred[i] & mask == pred[i]:
                nxt = mask | 1 << i
                cost = dp[mask] + weights[i] * elapsed[nxt]
                if dp[nxt] is None or cost < dp[nxt]:
                    dp[nxt] = cost
    return dp[-1]
''', [(([], [], []), 0), (([3, 1], [1, 4], []), 8), (([3, 1], [1, 4], [(0, 1)]), 19), (([1, 1], [1, 1], [(0, 1), (1, 0)]), None)])

_add('parallel_makespan', 'durations, machines',
     'Assign nonpreemptive jobs of nonnegative integer durations to identical machines, all available at zero, minimizing maximum machine load. machines>=1; at most 12 jobs. Return optimal makespan integer. Empty/all-zero jobs return 0; machines may exceed job count.',
     'expert', True, '''
    if not durations:
        return 0
    jobs = sorted(durations, reverse=True)
    loads = [0] * min(machines, len(jobs))
    best = sum(jobs)
    def search(i):
        nonlocal best
        if i == len(jobs):
            best = min(best, max(loads))
            return
        tried = set()
        for j in range(len(loads)):
            if loads[j] in tried or loads[j] + jobs[i] >= best:
                continue
            tried.add(loads[j])
            loads[j] += jobs[i]
            search(i + 1)
            loads[j] -= jobs[i]
    search(0)
    return best
''', [(([], 3), 0), (([0, 0], 1), 0), (([8, 7, 6, 5, 4], 2), 15), (([3, 2], 5), 3)])

_add('rectangle_union_area', 'rectangles',
     'rectangles=(x1,y1,x2,y2) integer axis-aligned half-open rectangles with x1<=x2,y1<=y2. Return exact area of their union. Degenerate rectangles add zero; overlaps/duplicates count once. <=200 rectangles; coordinates may be negative.',
     'hard', True, '''
    rects = [(a, b, c, d) for a, b, c, d in rectangles if a < c and b < d]
    xs = sorted({x for a, b, c, d in rects for x in (a, c)})
    area = 0
    for left, right in zip(xs, xs[1:]):
        spans = sorted((b, d) for a, b, c, d in rects if a <= left and c >= right)
        covered = 0
        end = None
        for lo, hi in spans:
            if end is None or lo > end:
                covered += hi - lo
                end = hi
            elif hi > end:
                covered += hi - end
                end = hi
        area += (right - left) * covered
    return area
''', [(([],), 0), (([(0, 0, 2, 2), (1, 1, 3, 3)],), 7), (([(-2, -1, 0, 1), (-2, -1, 0, 1), (0, 0, 0, 9)],), 4), (([(0, 0, 1, 1), (1, 0, 2, 1)],), 2)])

_add('most_collinear', 'points',
     'points are integer (x,y) pairs, duplicate coordinates count as separate points. Return maximum number on a single straight line; empty returns 0, singleton 1. Use exact arithmetic, not floating-point slopes. <=300 points.',
     'hard', True, '''
    from math import gcd
    best = 0
    for i, (x, y) in enumerate(points):
        slopes = {}
        duplicates = 1
        for a, b in points[i + 1:]:
            dx, dy = a - x, b - y
            if not dx and not dy:
                duplicates += 1
                continue
            g = gcd(dx, dy)
            dx, dy = dx // g, dy // g
            if dx < 0 or dx == 0 and dy < 0:
                dx, dy = -dx, -dy
            slopes[dx, dy] = slopes.get((dx, dy), 0) + 1
        best = max(best, duplicates + max(slopes.values(), default=0))
    return best
''', [(([],), 0), (([(1, 1), (1, 1), (1, 1)],), 3), (([(0, 0), (1, 1), (2, 2), (0, 1)],), 3), (([(2, 0), (2, 3), (2, -1), (0, 0), (2, 0)],), 4)])

_add('convex_boundary', 'points',
     'Return extreme vertices of convex hull of integer points as coordinate tuples, counterclockwise starting at lexicographically smallest point. Deduplicate points; omit points strictly inside a straight hull edge. Collinear input returns two endpoints; singleton one point; empty []. Exact arithmetic required.',
     'hard', True, '''
    points = sorted(set(map(tuple, points)))
    if len(points) <= 1:
        return points
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    lower, upper = [], []
    for p in points:
        while len(lower) > 1 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper) > 1 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]
''', [(([],), []), (([(2, 2), (2, 2)],), [(2, 2)]), (([(2, 2), (0, 0), (1, 1)],), [(0, 0), (2, 2)]), (([(0, 0), (1, 0), (2, 0), (2, 2), (0, 2), (1, 1)],), [(0, 0), (2, 0), (2, 2), (0, 2)])])

_add('maximum_sum_rectangle', 'matrix',
     'For a nonempty rectangular integer matrix with at least one column, return (maximum sum,(top,left,bottom,right)) over nonempty half-open subrectangles. Among equal sums choose lexicographically smallest coordinate tuple, not smallest area. Dimensions<=30; all-negative matrices valid.',
     'expert', True, '''
    h, w = len(matrix), len(matrix[0])
    best = None
    for top in range(h):
        sums = [0] * w
        for bottom in range(top + 1, h + 1):
            sums = [a + b for a, b in zip(sums, matrix[bottom - 1])]
            prefix = 0
            low = 0
            left = 0
            for right, value in enumerate(sums, 1):
                prefix += value
                candidate = (prefix - low, (top, left, bottom, right))
                if best is None or candidate[0] > best[0] or candidate[0] == best[0] and candidate[1] < best[1]:
                    best = candidate
                if prefix < low:
                    low, left = prefix, right
    return best
''', [(([[-5]],), (-5, (0, 0, 1, 1))), (([[0, 0], [0, 0]],), (0, (0, 0, 1, 1))), (([[1, -2, 3], [4, -1, 2]],), (7, (0, 0, 2, 3))), (([[-4, -2], [-2, -5]],), (-2, (0, 1, 1, 2)))])

_add('all_one_rectangle', 'grid',
     'For a rectangular binary-string grid, return (largest all-1 rectangle area,(top,left,bottom,right)) using half-open coordinates. Tie-break lexicographically on coordinates. Empty/zero-width/no 1 returns (0,None). Dimensions<=80.',
     'expert', True, '''
    if not grid or not grid[0]:
        return (0, None)
    h, w = len(grid), len(grid[0])
    best = (0, None)
    for top in range(h):
        alive = [True] * w
        for bottom in range(top + 1, h + 1):
            left = 0
            for c in range(w + 1):
                if c < w:
                    alive[c] = alive[c] and grid[bottom - 1][c] == '1'
                if c == w or not alive[c]:
                    if c > left:
                        area = (bottom - top) * (c - left)
                        box = (top, left, bottom, c)
                        if area > best[0] or area == best[0] and (best[1] is None or box < best[1]):
                            best = (area, box)
                    left = c + 1
    return best
''', [(([],), (0, None)), ((['000'],), (0, None)), ((['110', '111'],), (4, (0, 0, 2, 2))), ((['101', '101'],), (2, (0, 0, 2, 1)))])

_add('knight_survival', 'size, row, col, moves',
     'On size-by-size board (size>=1), knight starts at valid (row,col). At each of moves>=0 steps choose uniformly among all 8 chess knight moves; leaving board loses permanently. Return exact survival probability as reduced n/d string. size<=12,moves<=30, no floating point.',
     'hard', True, '''
    from fractions import Fraction
    directions = [(a, b) for a, b in ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1))]
    counts = {(row, col): 1}
    for _ in range(moves):
        nxt = {}
        for (r, c), count in counts.items():
            for dr, dc in directions:
                a, b = r + dr, c + dc
                if 0 <= a < size and 0 <= b < size:
                    nxt[a, b] = nxt.get((a, b), 0) + count
        counts = nxt
    result = Fraction(sum(counts.values()), 8 ** moves)
    return f'{result.numerator}/{result.denominator}'
''', [((1, 0, 0, 0), '1/1'), ((1, 0, 0, 1), '0/1'), ((3, 0, 0, 2), '1/16'), ((8, 3, 3, 1), '1/1')])

_add('sliding_tiles', 'board',
     'board is a 2-by-3 matrix containing each integer 0..5 once, 0 blank. A move swaps blank with orthogonally adjacent tile. Return fewest moves to [[1,2,3],[4,5,0]], or -1 if unreachable.',
     'hard', True, '''
    from collections import deque
    start = tuple(x for row in board for x in row)
    target = (1, 2, 3, 4, 5, 0)
    adj = ((1, 3), (0, 2, 4), (1, 5), (0, 4), (1, 3, 5), (2, 4))
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        state, distance = queue.popleft()
        if state == target:
            return distance
        zero = state.index(0)
        for j in adj[zero]:
            nxt = list(state)
            nxt[zero], nxt[j] = nxt[j], nxt[zero]
            nxt = tuple(nxt)
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, distance + 1))
    return -1
''', [(([[1, 2, 3], [4, 5, 0]],), 0), (([[1, 2, 3], [4, 0, 5]],), 1), (([[1, 2, 3], [5, 4, 0]],), -1), (([[4, 1, 2], [5, 0, 3]],), 5)])

_add('box_pushes', 'grid',
     'grid is rectangular strings containing # wall, . floor, exactly one S player, B box, T target at distinct cells. Move player orthogonally on floor; moving into box pushes it one square if next square is free. Return minimum pushes to get box onto T, not minimum walking steps; -1 if impossible. Outside is wall. At most 8x8.',
     'expert', True, '''
    from collections import deque
    floor = {(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch != '#'}
    positions = {ch: (r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch in 'SBT'}
    moves = ((1, 0), (-1, 0), (0, 1), (0, -1))
    start = (positions['B'], positions['S'])
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (box, player), pushes = queue.popleft()
        if box == positions['T']:
            return pushes
        reach = {player}
        walk = [player]
        while walk:
            r, c = walk.pop()
            for dr, dc in moves:
                nxt = (r + dr, c + dc)
                if nxt in floor and nxt != box and nxt not in reach:
                    reach.add(nxt)
                    walk.append(nxt)
        r, c = box
        for dr, dc in moves:
            behind, ahead = (r - dr, c - dc), (r + dr, c + dc)
            state = (ahead, box)
            if behind in reach and ahead in floor and state not in seen:
                seen.add(state)
                queue.append((state, pushes + 1))
    return -1
''', [((['SBT'],), 1), ((['TBS'],), 1), ((['BST'],), -1), ((['#####', '#S..#', '#.B.#', '#..T#', '#####'],), 2)])

_add('nonogram_completions', 'pattern, runs',
     'pattern contains ., #, ? for known empty, known filled, unknown. runs is ordered list of positive filled-run lengths; adjacent runs must have >=1 empty cell. Return all matching replacements of ? sorted lexicographically (Python order, # before .). Empty pattern with empty runs yields [empty string]. Length<=18.',
     'hard', True, '''
    from itertools import product
    out = []
    unknown = [i for i, ch in enumerate(pattern) if ch == '?']
    for values in product('#.', repeat=len(unknown)):
        chars = list(pattern)
        for i, ch in zip(unknown, values):
            chars[i] = ch
        text = ''.join(chars)
        actual = [len(part) for part in text.split('.') if part]
        if actual == list(runs):
            out.append(text)
    return sorted(out)
''', [(('', []), ['']), (('???', [2]), ['##.', '.##']), (('#?#', [1, 1]), ['#.#']), (('??', [1, 1]), [])])

_add('minimum_exact_cover', 'universe_size, subsets',
     'Universe is 0..universe_size-1; subsets is <=18 lists of distinct valid elements; empty subsets legal. Choose input indices so every universe element occurs in exactly one chosen subset. Return shortest sorted index list, ties lexicographically, or None if impossible. Empty universe returns [].',
     'expert', True, '''
    masks = [sum(1 << x for x in subset) for subset in subsets]
    full = (1 << universe_size) - 1
    best = None
    def search(i, used, chosen):
        nonlocal best
        if used == full:
            if best is None or (len(chosen), chosen) < (len(best), best):
                best = chosen[:]
            return
        if i == len(masks) or best is not None and len(chosen) >= len(best):
            return
        if masks[i] and not used & masks[i]:
            search(i + 1, used | masks[i], chosen + [i])
        search(i + 1, used, chosen)
    search(0, 0, [])
    return best
''', [((0, [[], []]), []), ((3, [[0, 1], [1, 2]]), None), ((3, [[0], [1, 2], [0, 1], [2]]), [0, 1]), ((3, [[0], [1], [2], [0, 1, 2]]), [3])])

_add('domino_tilings', 'grid',
     'grid is rectangular strings of . free and # blocked cells, at most 24 free cells. Return number of ways to cover each free cell exactly once with horizontal/vertical 1x2 dominoes, indistinguishable. Empty or entirely blocked board has one tiling. Exact integer, no modulus.',
     'expert', True, '''
    from functools import lru_cache
    cells = [(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == '.']
    index = {cell: i for i, cell in enumerate(cells)}
    @lru_cache(None)
    def solve(mask):
        if not mask:
            return 1
        bit = mask & -mask
        i = bit.bit_length() - 1
        r, c = cells[i]
        total = 0
        for cell in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            j = index.get(cell)
            if j is not None and mask >> j & 1:
                total += solve(mask ^ bit ^ (1 << j))
        return total
    return solve((1 << len(cells)) - 1)
''', [(([],), 1), ((['..', '..'],), 2), ((['...', '...'],), 3), ((['.#', '..'],), 0), ((['##'],), 1)])

_add('linear_extension_count', 'n, edges',
     'Return number of permutations of vertices 0..n-1 respecting all precedence edges (u,v) with u before v. n<=18; duplicates allowed, cycles/self-loops yield 0. Empty graph on zero vertices has one ordering. Exact integer, no modulus.',
     'expert', True, '''
    pred = [0] * n
    for u, v in edges:
        pred[v] |= 1 << u
    dp = [0] * (1 << n)
    dp[0] = 1
    for mask in range(1 << n):
        if not dp[mask]:
            continue
        for v in range(n):
            if not mask >> v & 1 and mask & pred[v] == pred[v]:
                dp[mask | 1 << v] += dp[mask]
    return dp[-1]
''', [((0, []), 1), ((3, []), 6), ((4, [(0, 2), (1, 2), (2, 3), (0, 2)]), 2), ((2, [(0, 1), (1, 0)]), 0)])

_add('alphabetic_merge_cost', 'weights',
     'weights is a list of nonnegative integer pile weights. Repeatedly merge two adjacent piles, paying their combined weight; the merged pile stays in their position. Return minimum total cost to merge all into one. Empty/singleton costs zero. Input order cannot be permuted. Length<=120.',
     'hard', True, '''
    n = len(weights)
    if n < 2:
        return 0
    prefix = [0]
    for x in weights:
        prefix.append(prefix[-1] + x)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for lo in range(n - length + 1):
            hi = lo + length - 1
            dp[lo][hi] = prefix[hi + 1] - prefix[lo] + min(dp[lo][k] + dp[k + 1][hi] for k in range(lo, hi))
    return dp[0][-1]
''', [(([],), 0), (([7],), 0), (([1, 2, 3, 4],), 19), (([4, 1, 1, 4],), 18), (([0, 0, 0],), 0)])
