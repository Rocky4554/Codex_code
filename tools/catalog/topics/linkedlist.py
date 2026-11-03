"""Linked Lists — pointer manipulation on singly linked lists."""
import heapq

from lib import Playlist, Problem, boolstr, lines, rand_ints

PLAYLISTS = [
    Playlist(
        key="linkedlist",
        title="08 · Linked Lists",
        description="Walk, rewire and reverse singly linked lists: the pointer moves interviewers love to probe.",
        accent="#C9B1FF",
        titles=[
            "Linked List Length",
            "Insert Node at Position",
            "Delete Node with Value",
            "Find Middle Node",
            "Reverse Linked List",
            "Remove Duplicates from Sorted List",
            "Merge Two Sorted Linked Lists",
            "Detect Cycle in Linked List",
            "Palindrome Linked List",
            "Delete the Middle Node",
            "Remove Nth Node From End",
            "Odd Even Linked List",
            "Sort a 0-1-2 Linked List",
            "Swap Nodes in Pairs",
            "Add Two Numbers",
            "Rotate List",
            "Reverse Sublist Between Positions",
            "Partition List",
            "Sort Linked List",
            "Reverse Nodes in k-Group",
            "Merge K Sorted Lists",
        ],
    )
]

LIST_FORMAT = "A linked list is written on one line as its node values from head to tail, space-separated. An empty list is written as `null`."


# ── helpers ──────────────────────────────────────────────────────

class Node:
    __slots__ = ("val", "next")

    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt


def parse(line):
    line = line.strip()
    if line in ("", "null"):
        return []
    return [int(x) for x in line.split()]


def show(vals):
    return " ".join(map(str, vals)) if vals else "null"


def build(vals):
    head = None
    for v in reversed(vals):
        head = Node(v, head)
    return head


def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def lst(r, n, lo=-99, hi=99):
    return show(rand_ints(r, n, lo, hi))


def sorted_lst(r, n, lo=-50, hi=50):
    return show(sorted(rand_ints(r, n, lo, hi)))


# ── solutions ────────────────────────────────────────────────────

def _length(inp):
    head = build(parse(lines(inp)[0]))
    n = 0
    while head:
        n += 1
        head = head.next
    return str(n)


def _insert(inp):
    ls = lines(inp)
    vals = parse(ls[0])
    pos, val = map(int, ls[1].split())
    dummy = Node(0, build(vals))
    prev = dummy
    for _ in range(pos):
        prev = prev.next
    prev.next = Node(val, prev.next)
    return show(to_list(dummy.next))


def _insert_brute(inp):
    ls = lines(inp)
    vals = parse(ls[0])
    pos, val = map(int, ls[1].split())
    return show(vals[:pos] + [val] + vals[pos:])


def _delete_value(inp):
    ls = lines(inp)
    head = build(parse(ls[0]))
    x = int(ls[1])
    dummy = Node(0, head)
    prev = dummy
    while prev.next and prev.next.val != x:
        prev = prev.next
    if prev.next:
        prev.next = prev.next.next
    return show(to_list(dummy.next))


def _delete_value_brute(inp):
    ls = lines(inp)
    vals = parse(ls[0])
    x = int(ls[1])
    if x in vals:
        vals.pop(vals.index(x))
    return show(vals)


def _dedupe_sorted(inp):
    head = build(parse(lines(inp)[0]))
    cur = head
    while cur and cur.next:
        if cur.next.val == cur.val:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return show(to_list(head))


def _dedupe_sorted_brute(inp):
    vals = parse(lines(inp)[0])
    out = []
    for v in vals:
        if not out or out[-1] != v:
            out.append(v)
    return show(out)


def _palindrome(inp):
    head = build(parse(lines(inp)[0]))
    # find middle, reverse second half, compare
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    prev = None
    while slow:
        slow.next, prev, slow = prev, slow, slow.next
    a, b = head, prev
    while b:
        if a.val != b.val:
            return "false"
        a, b = a.next, b.next
    return "true"


def _palindrome_brute(inp):
    vals = parse(lines(inp)[0])
    return boolstr(vals == vals[::-1])


def _delete_middle(inp):
    head = build(parse(lines(inp)[0]))
    if head is None or head.next is None:
        return "null"
    slow, fast = head, head.next.next
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    slow.next = slow.next.next
    return show(to_list(head))


def _delete_middle_brute(inp):
    vals = parse(lines(inp)[0])
    if vals:
        vals.pop(len(vals) // 2)
    return show(vals)


def _odd_even(inp):
    head = build(parse(lines(inp)[0]))
    if not head:
        return "null"
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return show(to_list(head))


def _odd_even_brute(inp):
    vals = parse(lines(inp)[0])
    return show(vals[0::2] + vals[1::2])


def _sort012(inp):
    head = build(parse(lines(inp)[0]))
    heads = [Node(0), Node(0), Node(0)]
    tails = heads[:]
    while head:
        tails[head.val].next = head
        tails[head.val] = head
        head = head.next
    for t in tails:
        t.next = None
    tails[0].next = heads[1].next or heads[2].next
    tails[1].next = heads[2].next
    first = heads[0].next or heads[1].next or heads[2].next
    return show(to_list(first))


def _sort012_brute(inp):
    return show(sorted(parse(lines(inp)[0])))


def _swap_pairs(inp):
    dummy = Node(0, build(parse(lines(inp)[0])))
    prev = dummy
    while prev.next and prev.next.next:
        a, b = prev.next, prev.next.next
        a.next, b.next, prev.next = b.next, a, b
        prev = a
    return show(to_list(dummy.next))


def _swap_pairs_brute(inp):
    vals = parse(lines(inp)[0])
    for i in range(0, len(vals) - 1, 2):
        vals[i], vals[i + 1] = vals[i + 1], vals[i]
    return show(vals)


def _add_two(inp):
    ls = lines(inp)
    a, b = build(parse(ls[0])), build(parse(ls[1]))
    dummy = tail = Node(0)
    carry = 0
    while a or b or carry:
        s = carry + (a.val if a else 0) + (b.val if b else 0)
        carry, digit = divmod(s, 10)
        tail.next = Node(digit)
        tail = tail.next
        a = a.next if a else None
        b = b.next if b else None
    return show(to_list(dummy.next))


def _add_two_brute(inp):
    ls = lines(inp)
    a = int("".join(map(str, reversed(parse(ls[0])))))
    b = int("".join(map(str, reversed(parse(ls[1])))))
    return " ".join(reversed(str(a + b)))


def _rotate(inp):
    ls = lines(inp)
    head = build(parse(ls[0]))
    k = int(ls[1])
    if not head:
        return "null"
    n, tail = 1, head
    while tail.next:
        tail, n = tail.next, n + 1
    k %= n
    if k == 0:
        return show(to_list(head))
    tail.next = head
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head, new_tail.next = new_tail.next, None
    return show(to_list(new_head))


def _rotate_brute(inp):
    ls = lines(inp)
    vals, k = parse(ls[0]), int(ls[1])
    for _ in range(k % len(vals) if vals else 0):
        vals = [vals[-1]] + vals[:-1]
    return show(vals)


def _reverse_between(inp):
    ls = lines(inp)
    head = build(parse(ls[0]))
    left, right = map(int, ls[1].split())
    dummy = Node(0, head)
    before = dummy
    for _ in range(left - 1):
        before = before.next
    cur = before.next
    for _ in range(right - left):
        move = cur.next
        cur.next = move.next
        move.next = before.next
        before.next = move
    return show(to_list(dummy.next))


def _reverse_between_brute(inp):
    ls = lines(inp)
    vals = parse(ls[0])
    left, right = map(int, ls[1].split())
    return show(vals[: left - 1] + vals[left - 1 : right][::-1] + vals[right:])


def _partition(inp):
    ls = lines(inp)
    head = build(parse(ls[0]))
    x = int(ls[1])
    small = small_t = Node(0)
    big = big_t = Node(0)
    while head:
        if head.val < x:
            small_t.next = head
            small_t = head
        else:
            big_t.next = head
            big_t = head
        head = head.next
    big_t.next = None
    small_t.next = big.next
    return show(to_list(small.next))


def _partition_brute(inp):
    ls = lines(inp)
    vals, x = parse(ls[0]), int(ls[1])
    return show([v for v in vals if v < x] + [v for v in vals if v >= x])


def _merge(a, b):
    dummy = tail = Node(0)
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next


def _merge_sort(head):
    if not head or not head.next:
        return head
    slow, fast = head, head.next
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    mid, slow.next = slow.next, None
    return _merge(_merge_sort(head), _merge_sort(mid))


def _sort_list(inp):
    return show(to_list(_merge_sort(build(parse(lines(inp)[0])))))


def _sort_list_brute(inp):
    return show(sorted(parse(lines(inp)[0])))


def _reverse_k(inp):
    ls = lines(inp)
    head = build(parse(ls[0]))
    k = int(ls[1])
    dummy = Node(0, head)
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return show(to_list(dummy.next))
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            cur.next, prev, cur = prev, cur, cur.next
        first = group_prev.next
        group_prev.next = kth
        group_prev = first


def _reverse_k_brute(inp):
    ls = lines(inp)
    vals, k = parse(ls[0]), int(ls[1])
    out = []
    for i in range(0, len(vals), k):
        chunk = vals[i : i + k]
        out += chunk[::-1] if len(chunk) == k else chunk
    return show(out)


def _merge_k(inp):
    ls = lines(inp)
    k = int(ls[0])
    heads = [build(parse(ls[1 + i] if 1 + i < len(ls) else "null")) for i in range(k)]
    heap = [(h.val, i, h) for i, h in enumerate(heads) if h]
    heapq.heapify(heap)
    dummy = tail = Node(0)
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return show(to_list(dummy.next))


def _merge_k_brute(inp):
    ls = lines(inp)
    k = int(ls[0])
    allv = []
    for i in range(k):
        allv += parse(ls[1 + i] if 1 + i < len(ls) else "null")
    return show(sorted(allv))


# ── test generators ──────────────────────────────────────────────

def _t_insert(r):
    out = ["null\n0 5", "1\n0 9", "1\n1 9", "1 2 3\n3 4", "4 4 4\n1 4"]
    for n in (5, 12, 1500):
        out.append(f"{lst(r, n)}\n{r.randint(0, n)} {r.randint(-99, 99)}")
    return out


def _t_delete(r):
    out = ["null\n3", "7\n7", "7\n8", "1 2 3\n1", "1 2 3\n3", "5 5 5\n5"]
    for n in (8, 20, 1500):
        vals = rand_ints(r, n, -20, 20)
        out.append(f"{show(vals)}\n{r.choice(vals + [99])}")
    return out


def _t_kparam(r, lo_k=1):
    out = []
    for n in (1, 2, 5, 9, 1500):
        vals = rand_ints(r, n, -99, 99)
        out.append(f"{show(vals)}\n{r.randint(lo_k, n)}")
    return out


def _t_reverse_between(r):
    out = ["5\n1 1", "1 2\n1 2", "1 2 3 4 5\n1 5", "1 2 3 4 5\n3 3", "1 2 3 4 5\n4 5"]
    for n in (7, 15, 1500):
        a = r.randint(1, n)
        b = r.randint(a, n)
        out.append(f"{lst(r, n)}\n{a} {b}")
    return out


def _t_add(r):
    out = ["0\n0", "9 9 9 9\n1", "5\n5", "1\n9 9 9", "0 0 1\n0 0 9"]
    for n, m in ((5, 3), (20, 20), (1500, 1200)):
        a = rand_ints(r, n, 0, 9)
        b = rand_ints(r, m, 0, 9)
        if a[-1] == 0:
            a[-1] = r.randint(1, 9)
        if b[-1] == 0:
            b[-1] = r.randint(1, 9)
        out.append(f"{show(a)}\n{show(b)}")
    return out


def _t_merge_k(r):
    out = ["0", "1\nnull", "3\nnull\nnull\nnull", "2\n1\n1", "3\n1 4 5\n1 3 4\n2 6"]
    for k, n in ((4, 6), (6, 10), (20, 80)):
        rows = [sorted_lst(r, r.randint(0, n)) if r.random() < 0.85 else "null" for _ in range(k)]
        out.append(f"{k}\n" + "\n".join(rows))
    return out


def _single_list_tests(r, special, lo=-99, hi=99, sort=False):
    out = list(special)
    for n in (6, 11, 40, 1500):
        vals = rand_ints(r, n, lo, hi)
        if sort:
            vals.sort()
        out.append(show(vals))
    return out


PROBLEMS = [
    Problem(
        title="Linked List Length",
        difficulty="EASY",
        topics=["Linked List"],
        description=f"""Count the nodes of a linked list by walking it from the head until you fall off the end.

{LIST_FORMAT}

**Input:** one line, the list.

**Output:** the number of nodes.""",
        constraints=["0 <= number of nodes <= 10^4"],
        solve=_length,
        examples=[("3 1 4 1 5", "Five nodes."), ("null", "An empty list has no nodes.")],
        tests=lambda r: _single_list_tests(r, ["7", "0 0"]),
    ),
    Problem(
        title="Insert Node at Position",
        difficulty="EASY",
        topics=["Linked List"],
        description=f"""Insert a new node with value `val` so that it ends up at 0-based position `pos`. Position 0 makes it the new head; position `n` (the length) appends it at the tail.

{LIST_FORMAT}

**Input:** line 1 is the list; line 2 has `pos` and `val`.

**Output:** the list after the insertion.""",
        constraints=["0 <= n <= 10^4", "0 <= pos <= n"],
        solve=_insert,
        brute=_insert_brute,
        examples=[("10 20 30\n1 15", "15 goes between 10 and 20."), ("null\n0 7", "Inserting into an empty list creates a single node.")],
        tests=_t_insert,
    ),
    Problem(
        title="Delete Node with Value",
        difficulty="EASY",
        topics=["Linked List"],
        description=f"""Remove the **first** node whose value equals `x`. If no node has that value, the list is unchanged.

{LIST_FORMAT}

**Input:** line 1 is the list; line 2 is `x`.

**Output:** the list after the deletion (`null` if it becomes empty).""",
        constraints=["0 <= n <= 10^4"],
        solve=_delete_value,
        brute=_delete_value_brute,
        examples=[("4 2 7 2\n2", "Only the first 2 is removed."), ("9\n9", "Deleting the only node leaves an empty list.")],
        tests=_t_delete,
    ),
    Problem(
        title="Remove Duplicates from Sorted List",
        difficulty="EASY",
        topics=["Linked List"],
        description=f"""The list is sorted in non-decreasing order. Remove nodes so that every value appears exactly once, keeping the list sorted.

Because equal values sit next to each other, one pass that skips a node whenever it equals its predecessor is enough.

{LIST_FORMAT}

**Input:** one line, the sorted list.

**Output:** the list with duplicates removed.""",
        constraints=["0 <= n <= 10^4"],
        solve=_dedupe_sorted,
        brute=_dedupe_sorted_brute,
        examples=[("1 1 2 3 3", "Keep one 1 and one 3."), ("5 5 5", "Only one 5 survives.")],
        tests=lambda r: _single_list_tests(r, ["null", "4", "1 2 3"], -10, 10, sort=True),
    ),
    Problem(
        title="Palindrome Linked List",
        difficulty="EASY",
        topics=["Linked List", "Two Pointers"],
        description=f"""Print `true` if the list reads the same forwards and backwards, otherwise `false`.

Try to do it with `O(1)` extra space: find the middle with slow/fast pointers, reverse the second half, then compare the halves.

{LIST_FORMAT}

**Input:** one line, the list.

**Output:** `true` or `false`.""",
        constraints=["0 <= n <= 10^4"],
        solve=_palindrome,
        brute=_palindrome_brute,
        examples=[("1 2 3 2 1", "Same in both directions."), ("1 2", "Reversed it is 2 1.")],
        tests=lambda r: ["null", "7", "4 4", "1 2 2 1", "1 2 1 2", "3 1 4 1 3", "9 8 7 7 8 9 1"]
        + [show(v + v[::-1]) for v in (rand_ints(r, 30, 0, 5), rand_ints(r, 700, 0, 9))]
        + [show(rand_ints(r, 25, 0, 2))],
    ),
    Problem(
        title="Delete the Middle Node",
        difficulty="MEDIUM",
        topics=["Linked List", "Two Pointers"],
        description=f"""Delete the middle node of the list. For a list of length `n`, the middle is the node at 0-based index `⌊n / 2⌋`, so in a list of 4 nodes the third node is removed.

Do it in one pass: a fast pointer moving two steps per slow step stops when the slow pointer is just before the middle.

{LIST_FORMAT}

**Input:** one line, the list.

**Output:** the list without its middle node (`null` if it becomes empty).""",
        constraints=["0 <= n <= 10^4"],
        solve=_delete_middle,
        brute=_delete_middle_brute,
        examples=[("1 3 4 7 1 2 6", "n = 7, so index 3 (value 7) is removed."), ("1 2 3 4", "n = 4, so index 2 (value 3) is removed.")],
        tests=lambda r: _single_list_tests(r, ["null", "5", "1 2", "1 2 3"]),
    ),
    Problem(
        title="Odd Even Linked List",
        difficulty="MEDIUM",
        topics=["Linked List"],
        description=f"""Regroup the list so that all nodes at odd positions (1st, 3rd, 5th, …) come first, followed by all nodes at even positions. Keep the relative order inside each group. Positions are about where a node sits, not its value.

{LIST_FORMAT}

**Input:** one line, the list.

**Output:** the regrouped list.""",
        constraints=["0 <= n <= 10^4"],
        solve=_odd_even,
        brute=_odd_even_brute,
        examples=[("1 2 3 4 5", "Odd positions 1 3 5, then even positions 2 4."), ("2 1 3 5 6 4 7", "Positions 1,3,5,7 hold 2 3 6 7.")],
        tests=lambda r: _single_list_tests(r, ["null", "8", "1 2", "1 2 3"]),
    ),
    Problem(
        title="Sort a 0-1-2 Linked List",
        difficulty="MEDIUM",
        topics=["Linked List"],
        description=f"""Every node holds 0, 1 or 2. Rearrange the nodes so all 0s come first, then 1s, then 2s.

Instead of counting and overwriting values, try relinking the nodes into three separate chains and joining them.

{LIST_FORMAT}

**Input:** one line, the list.

**Output:** the sorted list.""",
        constraints=["0 <= n <= 10^4", "each value is 0, 1 or 2"],
        solve=_sort012,
        brute=_sort012_brute,
        examples=[("1 2 0 2 1 0", "Two of each."), ("2 2 1", "No zeros at all.")],
        tests=lambda r: _single_list_tests(r, ["null", "0", "2 2 2", "1 0", "2 0"], 0, 2),
    ),
    Problem(
        title="Swap Nodes in Pairs",
        difficulty="MEDIUM",
        topics=["Linked List"],
        description=f"""Swap every two adjacent nodes: the 1st with the 2nd, the 3rd with the 4th, and so on. If the length is odd, the last node stays where it is. Move the nodes themselves rather than swapping their values.

{LIST_FORMAT}

**Input:** one line, the list.

**Output:** the list after swapping pairs.""",
        constraints=["0 <= n <= 10^4"],
        solve=_swap_pairs,
        brute=_swap_pairs_brute,
        examples=[("1 2 3 4", "(1,2) and (3,4) swap."), ("1 2 3", "3 has no partner.")],
        tests=lambda r: _single_list_tests(r, ["null", "6", "1 2"]),
    ),
    Problem(
        title="Add Two Numbers",
        difficulty="MEDIUM",
        topics=["Linked List", "Math"],
        description="""Two non-negative integers are stored as linked lists of digits in **reverse order**: the head holds the ones digit. Add them and print the sum in the same reversed-digit form.

Neither number has leading zeros, except the number 0 itself (a single node `0`). The numbers can be much longer than any built-in integer type, so add digit by digit with a carry.

**Input:** two lines, each a list of digits (space-separated, ones digit first).

**Output:** the digits of the sum, space-separated, ones digit first.""",
        constraints=["1 <= digits per number <= 2000"],
        solve=_add_two,
        brute=_add_two_brute,
        examples=[("2 4 3\n5 6 4", "342 + 465 = 807, printed as 7 0 8."), ("9 9\n1", "99 + 1 = 100, printed as 0 0 1.")],
        tests=_t_add,
    ),
    Problem(
        title="Rotate List",
        difficulty="MEDIUM",
        topics=["Linked List"],
        description=f"""Rotate the list to the right by `k` places: each step moves the tail node to the front. `k` may be larger than the list's length.

Connect the tail to the head to form a ring, then cut it at the right place: `k mod n` nodes from the end.

{LIST_FORMAT}

**Input:** line 1 is the list; line 2 is `k`.

**Output:** the rotated list.""",
        constraints=["0 <= n <= 500", "0 <= k <= 2 * 10^9"],
        solve=_rotate,
        brute=lambda inp: _rotate_brute(inp) if int(lines(inp)[1]) < 10**5 else _rotate(inp),
        examples=[("1 2 3 4 5\n2", "4 5 move to the front."), ("0 1 2\n4", "4 mod 3 = 1, so one rotation.")],
        tests=lambda r: ["null\n3", "1\n0", "1\n99", "1 2\n2", "1 2 3\n0", "1 2 3\n2000000000"]
        + [f"{lst(r, n)}\n{r.randint(0, 3 * n)}" for n in (4, 9, 500)],
    ),
    Problem(
        title="Reverse Sublist Between Positions",
        difficulty="MEDIUM",
        topics=["Linked List"],
        description=f"""Reverse only the part of the list from position `left` to position `right` (1-based, inclusive), leaving the rest in place. Try to do it in a single pass.

{LIST_FORMAT}

**Input:** line 1 is a non-empty list; line 2 has `left` and `right`.

**Output:** the list after reversing that section.""",
        constraints=["1 <= n <= 10^4", "1 <= left <= right <= n"],
        solve=_reverse_between,
        brute=_reverse_between_brute,
        examples=[("1 2 3 4 5\n2 4", "2 3 4 becomes 4 3 2."), ("7\n1 1", "A one-node section doesn't change anything.")],
        tests=_t_reverse_between,
    ),
    Problem(
        title="Partition List",
        difficulty="MEDIUM",
        topics=["Linked List", "Two Pointers"],
        description=f"""Rearrange the list so that every node with a value **less than** `x` comes before every node with a value greater than or equal to `x`. Keep the original relative order within both parts.

{LIST_FORMAT}

**Input:** line 1 is the list; line 2 is `x`.

**Output:** the partitioned list.""",
        constraints=["0 <= n <= 10^4"],
        solve=_partition,
        brute=_partition_brute,
        examples=[("1 4 3 2 5 2\n3", "Values below 3 (1 2 2) keep their order, then 4 3 5."), ("2 1\n2", "1 moves ahead of 2.")],
        tests=lambda r: ["null\n0", "5\n5", "5\n6", "3 3 3\n3", "1 2 3\n0", "1 2 3\n9"]
        + [f"{lst(r, n, -20, 20)}\n{r.randint(-10, 10)}" for n in (8, 30, 1500)],
    ),
    Problem(
        title="Sort Linked List",
        difficulty="MEDIUM",
        topics=["Linked List", "Sorting"],
        description=f"""Sort the list in non-decreasing order. Aim for `O(n log n)` time: split the list at its middle, sort both halves recursively, and merge them (merge sort suits linked lists well because merging needs no extra array).

{LIST_FORMAT}

**Input:** one line, the list.

**Output:** the sorted list.""",
        constraints=["0 <= n <= 5 * 10^4", "-10^5 <= value <= 10^5"],
        solve=_sort_list,
        brute=_sort_list_brute,
        examples=[("4 2 1 3", "Merge (2 4) and (1 3)."), ("-1 5 3 4 0", "Negatives sort first.")],
        tests=lambda r: _single_list_tests(r, ["null", "1", "2 1", "3 3 3 1"]),
    ),
    Problem(
        title="Reverse Nodes in k-Group",
        difficulty="HARD",
        topics=["Linked List"],
        description=f"""Reverse the nodes of the list `k` at a time. Each full group of `k` consecutive nodes is reversed; if fewer than `k` nodes remain at the end, they stay in their original order.

{LIST_FORMAT}

**Input:** line 1 is a non-empty list; line 2 is `k`.

**Output:** the list after reversing every full group.""",
        constraints=["1 <= k <= n <= 5000"],
        solve=_reverse_k,
        brute=_reverse_k_brute,
        examples=[("1 2 3 4 5\n2", "(1 2) and (3 4) are reversed; 5 is left alone."), ("1 2 3 4 5\n3", "(1 2 3) reversed; 4 5 is too short.")],
        tests=lambda r: ["1\n1", "1 2\n2", "1 2 3\n1", "1 2 3\n3", "1 2 3 4\n3"] + _t_kparam(r),
    ),
    Problem(
        title="Merge K Sorted Lists",
        difficulty="HARD",
        topics=["Linked List", "Heap"],
        description=f"""You are given `k` linked lists, each sorted in non-decreasing order. Merge them into one sorted list.

A min-heap holding the current head of every list gives `O(N log k)` for `N` total nodes.

{LIST_FORMAT}

**Input:** line 1 is `k`; each of the next `k` lines is one sorted list (possibly `null`).

**Output:** the merged list (`null` if every list is empty).""",
        constraints=["0 <= k <= 500", "0 <= total nodes <= 10^4"],
        solve=_merge_k,
        brute=_merge_k_brute,
        examples=[("3\n1 4 5\n1 3 4\n2 6", "All eight values in order."), ("2\nnull\n0", "One empty list and one single node.")],
        tests=_t_merge_k,
    ),
]
