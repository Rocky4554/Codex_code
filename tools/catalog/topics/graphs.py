"""Graphs — traversals, grid BFS/DFS, cycles, topological order, shortest paths, MST and DSU."""
import heapq
from collections import deque
from itertools import product

from lib import Playlist, Problem, boolstr, lines

PLAYLISTS = [
    Playlist(
        key="graphs",
        title="16 · Graphs",
        description="From BFS and DFS through grid flood fills, cycle checks and topological order to Dijkstra, Bellman-Ford, MST and union-find.",
        accent="#B5D8FF",
        titles=[
            "BFS Traversal of a Graph",
            "DFS Traversal of a Graph",
            "Number of Provinces",
            "Number of Islands",
            "Flood Fill",
            "Rotting Oranges",
            "Distance to Nearest Zero",
            "Surrounded Regions",
            "Number of Enclaves",
            "Detect Cycle in an Undirected Graph",
            "Is Graph Bipartite",
            "Detect Cycle in a Directed Graph",
            "Topological Sort",
            "Course Schedule",
            "Shortest Path in an Unweighted Graph",
            "Shortest Path in a Binary Maze",
            "Word Ladder Length",
            "Dijkstra's Shortest Paths",
            "Network Delay Time",
            "Cheapest Flights Within K Stops",
            "Bellman-Ford with Negative Cycle Detection",
            "Floyd-Warshall All Pairs",
            "Minimum Spanning Tree Weight",
            "Number of Operations to Connect the Network",
        ],
    )
]

INF = float("inf")
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ── parsing / formatting helpers ─────────────────────────────────

def read_graph(inp):
    ls = lines(inp)
    n, m = map(int, ls[0].split())
    edges = [tuple(map(int, ls[1 + i].split())) for i in range(m)]
    return n, edges, ls[1 + m:]


def read_grid(inp):
    ls = lines(inp)
    r, c = map(int, ls[0].split())
    return [list(row) for row in ls[1:1 + r]], ls[1 + r:]


def fmt_graph(n, edges, tail=()):
    out = [f"{n} {len(edges)}"] + [" ".join(map(str, e)) for e in edges] + list(tail)
    return "\n".join(out)


def fmt_grid(rows, tail=()):
    return "\n".join([f"{len(rows)} {len(rows[0])}"] + ["".join(map(str, row)) for row in rows] + list(tail))


def gen_pairs(r, n, m, directed=False):
    """m distinct pairs (u, v), u != v. Undirected pairs come out in random orientation."""
    cap = n * (n - 1) if directed else n * (n - 1) // 2
    m = min(m, cap)
    seen, out = set(), []
    if n <= 120 and m > cap // 3:
        allp = [(u, v) for u in range(n) for v in range(n) if u != v and (directed or u < v)]
        picked = r.sample(allp, m)
    else:
        picked = []
        while len(picked) < m:
            u, v = r.randrange(n), r.randrange(n)
            if u == v:
                continue
            key = (u, v) if directed else (min(u, v), max(u, v))
            if key in seen:
                continue
            seen.add(key)
            picked.append(key)
    for u, v in picked:
        if not directed and r.random() < 0.5:
            u, v = v, u
        out.append((u, v))
    return out


def gen_dag(r, n, m):
    order = list(range(n))
    r.shuffle(order)
    pos = {v: i for i, v in enumerate(order)}
    pairs = gen_pairs(r, n, m, directed=False)
    return [(u, v) if pos[u] < pos[v] else (v, u) for u, v in pairs]


def connected_pairs(r, n, extra):
    """Random spanning tree plus `extra` more distinct undirected edges."""
    nodes = list(range(n))
    r.shuffle(nodes)
    seen, out = set(), []
    for i in range(1, n):
        u, v = nodes[i], nodes[r.randrange(i)]
        seen.add((min(u, v), max(u, v)))
        out.append((u, v))
    cap = n * (n - 1) // 2
    extra = min(extra, cap - len(out))
    while extra > 0:
        u, v = r.randrange(n), r.randrange(n)
        if u == v or (min(u, v), max(u, v)) in seen:
            continue
        seen.add((min(u, v), max(u, v)))
        out.append((u, v))
        extra -= 1
    r.shuffle(out)
    return out


def adj_undirected(n, edges):
    g = [[] for _ in range(n)]
    for u, v, *_ in edges:
        g[u].append(v)
        if u != v:
            g[v].append(u)
    return [sorted(x) for x in g]


def adj_directed(n, edges, weighted=False):
    g = [[] for _ in range(n)]
    for e in edges:
        g[e[0]].append((e[1], e[2]) if weighted else e[1])
    return g


class DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.size = [1] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.p[b] = a
        self.size[a] += self.size[b]
        return True


def components(n, edges):
    d = DSU(n)
    for u, v, *_ in edges:
        d.union(u, v)
    return len({d.find(x) for x in range(n)})


def bfs_dist(n, g, src):
    dist = [-1] * n
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in g[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def dijkstra(n, g, src):
    dist = [INF] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in g[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return dist


def bellman(n, edges, src):
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    return dist


def floyd(n, edges):
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF:
                continue
            di = d[i]
            for j in range(n):
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    return d


def dist_line(dist):
    return " ".join("-1" if x == INF or x == -1 else str(x) for x in dist)


def grid_neighbours(r, c, R, C):
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C:
            yield nr, nc


def rand_grid(r, R, C, alphabet, weights=None):
    return [[r.choices(alphabet, weights)[0] for _ in range(C)] for _ in range(R)]


# ── traversals ────────────────────────────────────────────────────

def _bfs_traversal(inp):
    n, edges, rest = read_graph(inp)
    src = int(rest[0])
    g = adj_undirected(n, edges)
    seen = [False] * n
    seen[src] = True
    order, q = [], deque([src])
    while q:
        u = q.popleft()
        order.append(u)
        for v in g[u]:
            if not seen[v]:
                seen[v] = True
                q.append(v)
    return " ".join(map(str, order))


def _bfs_traversal_brute(inp):
    # Level by level: nodes at distance d in the order they were discovered from level d-1.
    n, edges, rest = read_graph(inp)
    src = int(rest[0])
    g = adj_undirected(n, edges)
    order, level, seen = [src], [src], {src}
    while level:
        nxt = []
        for u in level:
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    nxt.append(v)
        order += nxt
        level = nxt
    return " ".join(map(str, order))


def _dfs_traversal(inp):
    n, edges, rest = read_graph(inp)
    src = int(rest[0])
    g = adj_undirected(n, edges)
    seen = [False] * n
    order = []
    stack = [(src, 0)]
    seen[src] = True
    order.append(src)
    while stack:
        u, i = stack[-1]
        if i < len(g[u]):
            stack[-1] = (u, i + 1)
            v = g[u][i]
            if not seen[v]:
                seen[v] = True
                order.append(v)
                stack.append((v, 0))
        else:
            stack.pop()
    return " ".join(map(str, order))


def _dfs_traversal_brute(inp):
    import sys
    sys.setrecursionlimit(10000)
    n, edges, rest = read_graph(inp)
    src = int(rest[0])
    g = adj_undirected(n, edges)
    seen, order = set(), []

    def go(u):
        seen.add(u)
        order.append(u)
        for v in g[u]:
            if v not in seen:
                go(v)

    go(src)
    return " ".join(map(str, order))


def _traversal_tests(r):
    yield fmt_graph(1, [], ["0"])
    yield fmt_graph(4, [], ["2"])
    yield fmt_graph(5, [(0, 1), (1, 2), (3, 4)], ["3"])
    yield fmt_graph(6, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 0)], ["0"])
    yield fmt_graph(5, [(0, 1), (1, 2), (2, 3), (3, 4)], ["4"])
    for n, m in ((8, 10), (12, 15), (15, 40)):
        yield fmt_graph(n, gen_pairs(r, n, m), [str(r.randrange(n))])
    yield fmt_graph(1500, gen_pairs(r, 1500, 2200), [str(r.randrange(1500))])


def _provinces(inp):
    ls = lines(inp)
    n = int(ls[0])
    mat = [list(map(int, ls[1 + i].split())) for i in range(n)]
    d = DSU(n)
    for i in range(n):
        for j in range(i + 1, n):
            if mat[i][j]:
                d.union(i, j)
    return str(len({d.find(x) for x in range(n)}))


def _provinces_brute(inp):
    ls = lines(inp)
    n = int(ls[0])
    mat = [list(map(int, ls[1 + i].split())) for i in range(n)]
    seen, count = set(), 0
    for s in range(n):
        if s in seen:
            continue
        count += 1
        stack = [s]
        seen.add(s)
        while stack:
            u = stack.pop()
            for v in range(n):
                if mat[u][v] and v not in seen:
                    seen.add(v)
                    stack.append(v)
    return str(count)


def fmt_matrix(n, edges):
    mat = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for u, v in edges:
        mat[u][v] = mat[v][u] = 1
    return "\n".join([str(n)] + [" ".join(map(str, row)) for row in mat])


def _provinces_tests(r):
    yield fmt_matrix(1, [])
    yield fmt_matrix(4, [])
    yield fmt_matrix(4, [(0, 1), (1, 2), (2, 3)])
    yield fmt_matrix(6, [(0, 5), (1, 4)])
    for n, m in ((7, 4), (10, 8), (12, 5), (20, 18)):
        yield fmt_matrix(n, gen_pairs(r, n, m))
    yield fmt_matrix(90, gen_pairs(r, 90, 70))


# ── grid problems ─────────────────────────────────────────────────

def _flood_fill(inp):
    grid, rest = read_grid(inp)
    sr, sc, color = map(int, rest[0].split())
    R, C = len(grid), len(grid[0])
    old, new = grid[sr][sc], str(color)
    if old != new:
        stack = [(sr, sc)]
        grid[sr][sc] = new
        while stack:
            r, c = stack.pop()
            for nr, nc in grid_neighbours(r, c, R, C):
                if grid[nr][nc] == old:
                    grid[nr][nc] = new
                    stack.append((nr, nc))
    return "\n".join("".join(row) for row in grid)


def _flood_fill_brute(inp):
    grid, rest = read_grid(inp)
    sr, sc, color = map(int, rest[0].split())
    R, C = len(grid), len(grid[0])
    old = grid[sr][sc]
    region = {(sr, sc)}
    changed = True
    while changed:
        changed = False
        for r in range(R):
            for c in range(C):
                if (r, c) not in region and grid[r][c] == old and any(n in region for n in grid_neighbours(r, c, R, C)):
                    region.add((r, c))
                    changed = True
    for r, c in region:
        grid[r][c] = str(color)
    return "\n".join("".join(row) for row in grid)


def _flood_tests(r):
    yield fmt_grid([[5]], ["0 0 5"])
    yield fmt_grid([[1]], ["0 0 3"])
    yield fmt_grid([[0, 0, 0], [0, 0, 0]], ["1 2 0"])
    yield fmt_grid([[1, 2, 1], [2, 1, 2], [1, 2, 1]], ["1 1 7"])
    for R, C in ((4, 5), (6, 6), (8, 10), (5, 12)):
        g = rand_grid(r, R, C, [0, 1, 2], [3, 3, 1])
        yield fmt_grid(g, [f"{r.randrange(R)} {r.randrange(C)} {r.randint(0, 9)}"])
    g = rand_grid(r, 60, 80, [1, 2], [4, 1])
    yield fmt_grid(g, ["30 40 9"])


def _rotting(inp):
    grid, _ = read_grid(inp)
    R, C = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "2":
                q.append((r, c, 0))
            elif grid[r][c] == "1":
                fresh += 1
    minutes = 0
    while q:
        r, c, t = q.popleft()
        minutes = max(minutes, t)
        for nr, nc in grid_neighbours(r, c, R, C):
            if grid[nr][nc] == "1":
                grid[nr][nc] = "2"
                fresh -= 1
                q.append((nr, nc, t + 1))
    return str(minutes if fresh == 0 else -1)


def _rotting_brute(inp):
    grid, _ = read_grid(inp)
    R, C = len(grid), len(grid[0])
    t = 0
    while True:
        rot = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == "1"
               and any(grid[nr][nc] == "2" for nr, nc in grid_neighbours(r, c, R, C))]
        if not rot:
            break
        for r, c in rot:
            grid[r][c] = "2"
        t += 1
    if any("1" in row for row in grid):
        return "-1"
    return str(t)


def _rotting_tests(r):
    yield fmt_grid([[0]])
    yield fmt_grid([[1]])
    yield fmt_grid([[2]])
    yield fmt_grid([[2, 1, 0, 1]])
    yield fmt_grid([[2, 1, 1, 1, 1, 1]])
    for R, C in ((4, 4), (5, 7), (7, 7), (6, 10)):
        yield fmt_grid(rand_grid(r, R, C, [0, 1, 2], [2, 6, 1]))
    yield fmt_grid(rand_grid(r, 70, 90, [0, 1, 2], [1, 12, 1]))


def _nearest_zero(inp):
    grid, _ = read_grid(inp)
    R, C = len(grid), len(grid[0])
    dist = [[-1] * C for _ in range(R)]
    q = deque()
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "0":
                dist[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for nr, nc in grid_neighbours(r, c, R, C):
            if dist[nr][nc] < 0:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return "\n".join(" ".join(map(str, row)) for row in dist)


def _nearest_zero_brute(inp):
    grid, _ = read_grid(inp)
    R, C = len(grid), len(grid[0])
    zeros = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == "0"]
    return "\n".join(" ".join(str(min(abs(r - zr) + abs(c - zc) for zr, zc in zeros)) for c in range(C)) for r in range(R))


def _nearest_zero_tests(r):
    yield fmt_grid([[0]])
    yield fmt_grid([[1, 1, 1, 0]])
    yield fmt_grid([[0, 0], [0, 0]])
    yield fmt_grid([[1, 1, 1], [1, 1, 1], [1, 1, 0]])
    for R, C in ((3, 5), (6, 6), (5, 9), (8, 8)):
        g = rand_grid(r, R, C, [0, 1], [1, 4])
        g[r.randrange(R)][r.randrange(C)] = 0
        yield fmt_grid(g)
    g = rand_grid(r, 40, 50, [0, 1], [1, 30])
    g[0][0] = 0
    yield fmt_grid(g)


def _surrounded(inp):
    grid, _ = read_grid(inp)
    R, C = len(grid), len(grid[0])
    safe = [[False] * C for _ in range(R)]
    stack = [(r, c) for r in range(R) for c in range(C)
             if (r in (0, R - 1) or c in (0, C - 1)) and grid[r][c] == "O"]
    for r, c in stack:
        safe[r][c] = True
    while stack:
        r, c = stack.pop()
        for nr, nc in grid_neighbours(r, c, R, C):
            if grid[nr][nc] == "O" and not safe[nr][nc]:
                safe[nr][nc] = True
                stack.append((nr, nc))
    return "\n".join("".join("O" if grid[r][c] == "O" and safe[r][c] else "X" for c in range(C)) for r in range(R))


def _surrounded_brute(inp):
    grid, _ = read_grid(inp)
    R, C = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    for r in range(R):
        for c in range(C):
            if grid[r][c] != "O":
                continue
            seen, stack, border = {(r, c)}, [(r, c)], False
            while stack:
                x, y = stack.pop()
                if x in (0, R - 1) or y in (0, C - 1):
                    border = True
                for n in grid_neighbours(x, y, R, C):
                    if grid[n[0]][n[1]] == "O" and n not in seen:
                        seen.add(n)
                        stack.append(n)
            if not border:
                out[r][c] = "X"
    return "\n".join("".join(row) for row in out)


def _surrounded_tests(r):
    yield fmt_grid([["O"]])
    yield fmt_grid([["X", "X"], ["X", "X"]])
    yield fmt_grid([list("XXX"), list("XOX"), list("XXX")])
    yield fmt_grid([list("OOO"), list("OOO"), list("OOO")])
    yield fmt_grid([list("XXXXX"), list("XOOOX"), list("XOXOX"), list("XOOOO")])
    for R, C in ((5, 5), (6, 8), (8, 8), (7, 11)):
        yield fmt_grid(rand_grid(r, R, C, ["X", "O"], [3, 2]))
    yield fmt_grid(rand_grid(r, 60, 80, ["X", "O"], [3, 2]))


def _enclaves(inp):
    grid, _ = read_grid(inp)
    R, C = len(grid), len(grid[0])
    stack = [(r, c) for r in range(R) for c in range(C) if (r in (0, R - 1) or c in (0, C - 1)) and grid[r][c] == "1"]
    for r, c in stack:
        grid[r][c] = "0"
    while stack:
        r, c = stack.pop()
        for nr, nc in grid_neighbours(r, c, R, C):
            if grid[nr][nc] == "1":
                grid[nr][nc] = "0"
                stack.append((nr, nc))
    return str(sum(row.count("1") for row in grid))


def _enclaves_brute(inp):
    grid, _ = read_grid(inp)
    R, C = len(grid), len(grid[0])
    count = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] != "1":
                continue
            seen, stack, border = {(r, c)}, [(r, c)], False
            while stack:
                x, y = stack.pop()
                if x in (0, R - 1) or y in (0, C - 1):
                    border = True
                for n in grid_neighbours(x, y, R, C):
                    if grid[n[0]][n[1]] == "1" and n not in seen:
                        seen.add(n)
                        stack.append(n)
            count += not border
    return str(count)


def _enclaves_tests(r):
    yield fmt_grid([[1]])
    yield fmt_grid([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    yield fmt_grid([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    yield fmt_grid([[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]])
    for R, C in ((5, 5), (6, 8), (8, 8), (9, 12)):
        yield fmt_grid(rand_grid(r, R, C, [0, 1], [2, 3]))
    yield fmt_grid(rand_grid(r, 60, 80, [0, 1], [1, 1]))


# ── cycles, bipartite, topological order ─────────────────────────

def _cycle_undirected(inp):
    n, edges, _ = read_graph(inp)
    g = adj_undirected(n, edges)
    seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, -1)]
        while stack:
            u, parent = stack.pop()
            for v in g[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append((v, u))
                elif v != parent:
                    return "true"
    return "false"


def _cycle_undirected_brute(inp):
    # A forest with c components has exactly n - c edges; any extra edge closes a cycle.
    n, edges, _ = read_graph(inp)
    return boolstr(len(edges) > n - components(n, edges))


def _cycle_undirected_tests(r):
    yield fmt_graph(1, [])
    yield fmt_graph(2, [(0, 1)])
    yield fmt_graph(3, [(0, 1), (1, 2), (2, 0)])
    yield fmt_graph(5, [(0, 1), (2, 3), (3, 4)])
    yield fmt_graph(6, [(0, 1), (1, 2), (3, 4), (4, 5), (5, 3)])
    for n in (8, 10, 14):
        yield fmt_graph(n, connected_pairs(r, n, 0))  # trees
    for n, m in ((9, 9), (12, 11), (15, 13)):
        yield fmt_graph(n, gen_pairs(r, n, m))
    yield fmt_graph(1500, connected_pairs(r, 1500, 0))
    yield fmt_graph(1500, connected_pairs(r, 1500, 1))


def _bipartite(inp):
    n, edges, _ = read_graph(inp)
    g = adj_undirected(n, edges)
    color = [-1] * n
    for s in range(n):
        if color[s] >= 0:
            continue
        color[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in g[u]:
                if color[v] < 0:
                    color[v] = color[u] ^ 1
                    q.append(v)
                elif color[v] == color[u]:
                    return "false"
    return "true"


def _bipartite_brute(inp):
    n, edges, _ = read_graph(inp)
    if n <= 12:
        for colors in product((0, 1), repeat=n):
            if all(colors[u] != colors[v] for u, v in edges):
                return "true"
        return "false"
    # Union-find with parity for bigger inputs.
    p, par = list(range(n)), [0] * n

    def find(x):
        if p[x] == x:
            return x, 0
        root, d = find(p[x])
        p[x], par[x] = root, par[x] ^ d
        return root, par[x]

    for u, v in edges:
        (ru, pu), (rv, pv) = find(u), find(v)
        if ru == rv:
            if pu == pv:
                return "false"
        else:
            p[ru], par[ru] = rv, pu ^ pv ^ 1
    return "true"


def _bipartite_tests(r):
    yield fmt_graph(1, [])
    yield fmt_graph(2, [(0, 1)])
    yield fmt_graph(3, [(0, 1), (1, 2), (2, 0)])
    yield fmt_graph(4, [(0, 1), (1, 2), (2, 3), (3, 0)])
    yield fmt_graph(6, [(0, 1), (2, 3), (3, 4), (4, 2)])
    for n, m in ((6, 6), (8, 7), (10, 9), (11, 14)):
        yield fmt_graph(n, gen_pairs(r, n, m))
    # Large bipartite graph (edges only between the two halves) and one with an odd cycle planted.
    n = 1200
    left, right = list(range(0, n, 2)), list(range(1, n, 2))
    es = list({(r.choice(left), r.choice(right)) for _ in range(1800)})
    r.shuffle(es)
    yield fmt_graph(n, es)
    yield fmt_graph(n, es + [(0, 2)] if (0, 2) not in es else es)


def _cycle_directed(inp):
    n, edges, _ = read_graph(inp)
    g = adj_directed(n, edges)
    indeg = [0] * n
    for u, v in edges:
        indeg[v] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return boolstr(seen < n)


def _reach_closure(n, pairs):
    reach = [[False] * n for _ in range(n)]
    for u, v in pairs:
        reach[u][v] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                ri, rk = reach[i], reach[k]
                for j in range(n):
                    if rk[j]:
                        ri[j] = True
    return reach


def _cycle_directed_brute(inp):
    n, edges, _ = read_graph(inp)
    reach = _reach_closure(n, edges)
    return boolstr(any(reach[i][i] for i in range(n)))


def _directed_cycle_tests(r, flip=False):
    def tf(n, es):
        return fmt_graph(n, [(v, u) for u, v in es] if flip else es)

    yield tf(1, [])
    yield tf(1, [(0, 0)])
    yield tf(2, [(0, 1), (1, 0)])
    yield tf(4, [(0, 1), (1, 2), (2, 3)])
    yield tf(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
    for n, m in ((7, 9), (10, 14), (12, 16)):
        yield tf(n, gen_dag(r, n, m))
    for n, m in ((8, 12), (10, 15)):
        yield tf(n, gen_pairs(r, n, m, directed=True))
    big = gen_dag(r, 1500, 2000)
    yield tf(1500, big)
    yield tf(1500, big + [(big[0][1], big[0][0])])


def _topo(inp):
    n, edges, _ = read_graph(inp)
    g = adj_directed(n, edges)
    indeg = [0] * n
    for u, v in edges:
        indeg[v] += 1
    pq = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(pq)
    order = []
    while pq:
        u = heapq.heappop(pq)
        order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(pq, v)
    return " ".join(map(str, order))


def _topo_brute(inp):
    n, edges, _ = read_graph(inp)
    preds = [set() for _ in range(n)]
    for u, v in edges:
        preds[v].add(u)
    placed, order = set(), []
    while len(order) < n:
        nxt = min(v for v in range(n) if v not in placed and preds[v] <= placed)
        placed.add(nxt)
        order.append(nxt)
    return " ".join(map(str, order))


def _topo_tests(r):
    yield fmt_graph(1, [])
    yield fmt_graph(4, [])
    yield fmt_graph(4, [(3, 2), (2, 1), (1, 0)])
    yield fmt_graph(5, [(4, 0), (4, 1), (2, 1), (3, 0)])
    for n, m in ((6, 6), (8, 10), (10, 12), (14, 20)):
        yield fmt_graph(n, gen_dag(r, n, m))
    yield fmt_graph(1500, gen_dag(r, 1500, 2000))


def _course_schedule(inp):
    # Edge "a b" means b must come before a: a cycle anywhere makes it impossible.
    n, edges, _ = read_graph(inp)
    return boolstr(_cycle_directed(fmt_graph(n, [(b, a) for a, b in edges])) == "false")


def _course_schedule_brute(inp):
    n, edges, _ = read_graph(inp)
    reach = _reach_closure(n, [(b, a) for a, b in edges])
    return boolstr(not any(reach[i][i] for i in range(n)))


# ── shortest paths ────────────────────────────────────────────────

def _unweighted_sp(inp):
    n, edges, rest = read_graph(inp)
    return " ".join(map(str, bfs_dist(n, adj_undirected(n, edges), int(rest[0]))))


def _unweighted_sp_brute(inp):
    n, edges, rest = read_graph(inp)
    dist = bellman(n, [(u, v, 1) for u, v in edges] + [(v, u, 1) for u, v in edges], int(rest[0]))
    return dist_line(dist)


def _maze(inp):
    grid, rest = read_grid(inp)
    sr, sc, tr, tc = map(int, rest[0].split())
    R, C = len(grid), len(grid[0])
    if grid[sr][sc] != "1" or grid[tr][tc] != "1":
        return "-1"
    dist = [[-1] * C for _ in range(R)]
    dist[sr][sc] = 0
    q = deque([(sr, sc)])
    while q:
        r, c = q.popleft()
        if (r, c) == (tr, tc):
            return str(dist[r][c])
        for nr, nc in grid_neighbours(r, c, R, C):
            if grid[nr][nc] == "1" and dist[nr][nc] < 0:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return "-1"


def _maze_brute(inp):
    grid, rest = read_grid(inp)
    sr, sc, tr, tc = map(int, rest[0].split())
    R, C = len(grid), len(grid[0])
    if grid[sr][sc] != "1" or grid[tr][tc] != "1":
        return "-1"
    dist = {(sr, sc): 0}
    changed = True
    while changed:
        changed = False
        for r in range(R):
            for c in range(C):
                if grid[r][c] != "1":
                    continue
                best = dist.get((r, c), INF)
                for n in grid_neighbours(r, c, R, C):
                    if n in dist and dist[n] + 1 < best:
                        best = dist[n] + 1
                if best < dist.get((r, c), INF):
                    dist[(r, c)] = best
                    changed = True
    return str(dist.get((tr, tc), -1))


def _maze_tests(r):
    yield fmt_grid([[1]], ["0 0 0 0"])
    yield fmt_grid([[0]], ["0 0 0 0"])
    yield fmt_grid([[1, 0, 1]], ["0 0 0 2"])
    yield fmt_grid([[1, 1, 1], [0, 0, 1], [1, 1, 1]], ["0 0 2 0"])
    for R, C in ((4, 5), (6, 6), (7, 9), (8, 10)):
        g = rand_grid(r, R, C, [0, 1], [1, 3])
        yield fmt_grid(g, [f"{r.randrange(R)} {r.randrange(C)} {r.randrange(R)} {r.randrange(C)}"])
    g = rand_grid(r, 70, 90, [0, 1], [1, 3])
    g[0][0] = g[69][89] = 1
    yield fmt_grid(g, ["0 0 69 89"])


def _word_ladder(inp):
    ls = lines(inp)
    begin, end, k = ls[0], ls[1], int(ls[2])
    words = set(ls[3:3 + k])
    if end not in words:
        return "0"
    buckets = {}
    for w in words | {begin}:
        for i in range(len(w)):
            buckets.setdefault(w[:i] + "*" + w[i + 1:], []).append(w)
    dist = {begin: 1}
    q = deque([begin])
    while q:
        w = q.popleft()
        if w == end:
            return str(dist[w])
        for i in range(len(w)):
            for nxt in buckets.get(w[:i] + "*" + w[i + 1:], []):
                if nxt not in dist and nxt in words:
                    dist[nxt] = dist[w] + 1
                    q.append(nxt)
    return "0"


def _word_ladder_brute(inp):
    ls = lines(inp)
    begin, end, k = ls[0], ls[1], int(ls[2])
    words = list(dict.fromkeys(ls[3:3 + k]))
    if end not in words:
        return "0"

    def adjacent(a, b):
        return sum(x != y for x, y in zip(a, b)) == 1

    dist = {begin: 1}
    frontier = [begin]
    while frontier:
        nxt = []
        for w in frontier:
            for v in words:
                if v not in dist and adjacent(w, v):
                    dist[v] = dist[w] + 1
                    nxt.append(v)
        frontier = nxt
    return str(dist.get(end, 0))


def _ladder_input(begin, end, words):
    return "\n".join([begin, end, str(len(words))] + words)


def _ladder_tests(r):
    yield _ladder_input("aa", "bb", ["ab", "bb"])
    yield _ladder_input("cat", "dog", ["cot", "cog", "dot"])
    yield _ladder_input("hot", "dog", ["hot", "dog"])
    yield _ladder_input("abc", "abd", ["abd"])
    yield _ladder_input("lead", "gold", ["load", "goad", "gold", "lord"])
    for L, k, alpha in ((3, 12, "abc"), (3, 20, "abcd"), (4, 30, "abcd"), (4, 40, "abcde")):
        pool = list({"".join(r.choice(alpha) for _ in range(L)) for _ in range(k * 2)})
        r.shuffle(pool)
        begin, end = pool[0], pool[1]
        words = pool[1:k + 1]
        r.shuffle(words)
        yield _ladder_input(begin, end, words)
    alpha = "abcdef"
    pool = list({"".join(r.choice(alpha) for _ in range(5)) for _ in range(3000)})
    r.shuffle(pool)
    yield _ladder_input(pool[0], pool[1], pool[1:2500])


def _dijkstra(inp):
    n, edges, rest = read_graph(inp)
    return dist_line(dijkstra(n, adj_directed(n, edges, weighted=True), int(rest[0])))


def _dijkstra_brute(inp):
    n, edges, rest = read_graph(inp)
    return dist_line(bellman(n, edges, int(rest[0])))


def weighted(r, pairs, lo, hi):
    return [(u, v, r.randint(lo, hi)) for u, v in pairs]


def _weighted_tests(r, lo=0, hi=50, tail=lambda r, n: [str(r.randrange(n))]):
    yield fmt_graph(1, [], tail(r, 1))
    yield fmt_graph(3, [], tail(r, 3))
    yield fmt_graph(3, [(0, 1, 5), (1, 2, 5), (0, 2, 20)], tail(r, 3))
    yield fmt_graph(4, [(0, 1, 0), (1, 2, 0), (2, 3, 7), (3, 0, 1)], tail(r, 4))
    for n, m in ((6, 10), (8, 14), (10, 20), (12, 18)):
        yield fmt_graph(n, weighted(r, gen_pairs(r, n, m, directed=True), lo, hi), tail(r, n))
    yield fmt_graph(800, weighted(r, gen_pairs(r, 800, 2000, directed=True), lo, hi * 20), tail(r, 800))


def _network_delay(inp):
    n, edges, rest = read_graph(inp)
    dist = dijkstra(n, adj_directed(n, edges, weighted=True), int(rest[0]))
    worst = max(dist)
    return str(-1 if worst == INF else worst)


def _network_delay_brute(inp):
    n, edges, rest = read_graph(inp)
    d = floyd(n, edges)[int(rest[0])]
    worst = max(d)
    return str(-1 if worst == INF else worst)


def _network_tests(r):
    yield fmt_graph(1, [], ["0"])
    yield fmt_graph(2, [(0, 1, 4)], ["1"])
    yield fmt_graph(3, [(0, 1, 2), (0, 2, 9), (1, 2, 3)], ["0"])
    yield fmt_graph(4, [(1, 0, 1), (1, 2, 1), (2, 3, 1)], ["1"])
    for n, extra in ((6, 6), (8, 10), (10, 12)):
        # Directed edges pointing away from node 0 along a random tree, plus extras: all reachable.
        es = []
        for u, v in connected_pairs(r, n, extra):
            es.append((u, v, r.randint(1, 30)))
            es.append((v, u, r.randint(1, 30)))
        yield fmt_graph(n, es, [str(r.randrange(n))])
    for n, m in ((7, 9), (9, 12)):
        yield fmt_graph(n, weighted(r, gen_pairs(r, n, m, directed=True), 1, 20), [str(r.randrange(n))])
    es = []
    for u, v in connected_pairs(r, 100, 300):
        es.append((u, v, r.randint(1, 500)))
        es.append((v, u, r.randint(1, 500)))
    yield fmt_graph(100, es, ["0"])


def _flights(inp):
    n, edges, rest = read_graph(inp)
    src, dst, k = map(int, rest[0].split())
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):
        nxt = dist[:]
        for u, v, w in edges:
            if dist[u] + w < nxt[v]:
                nxt[v] = dist[u] + w
        dist = nxt
    return str(-1 if dist[dst] == INF else dist[dst])


def _flights_brute(inp):
    # best[e][v] = cheapest cost to reach v using exactly e flights.
    n, edges, rest = read_graph(inp)
    src, dst, k = map(int, rest[0].split())
    best = [[INF] * n for _ in range(k + 2)]
    best[0][src] = 0
    for e in range(1, k + 2):
        for u, v, w in edges:
            if best[e - 1][u] + w < best[e][v]:
                best[e][v] = best[e - 1][u] + w
    ans = min(best[e][dst] for e in range(k + 2))
    return str(-1 if ans == INF else ans)


def _flights_tests(r):
    yield fmt_graph(1, [], ["0 0 0"])
    yield fmt_graph(2, [], ["0 1 3"])
    yield fmt_graph(3, [(0, 1, 100), (1, 2, 100), (0, 2, 500)], ["0 2 0"])
    yield fmt_graph(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 10)], ["0 3 1"])
    for n, m in ((6, 12), (8, 16), (10, 25), (12, 30)):
        yield fmt_graph(n, weighted(r, gen_pairs(r, n, m, directed=True), 1, 100),
                        [f"{r.randrange(n)} {r.randrange(n)} {r.randint(0, 4)}"])
    yield fmt_graph(200, weighted(r, gen_pairs(r, 200, 1800, directed=True), 1, 1000), ["0 199 5"])


def _bf_negative(inp):
    n, edges, rest = read_graph(inp)
    src = int(rest[0])
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return "NEGATIVE CYCLE"
    return " ".join("INF" if d == INF else str(d) for d in dist)


def _bf_negative_brute(inp):
    n, edges, rest = read_graph(inp)
    src = int(rest[0])
    d = floyd(n, edges)
    if any(d[src][v] != INF and d[v][v] < 0 for v in range(n)):
        return "NEGATIVE CYCLE"
    return " ".join("INF" if x == INF else str(x) for x in d[src])


def _bf_tests(r):
    yield fmt_graph(1, [], ["0"])
    yield fmt_graph(3, [(0, 1, -2), (1, 2, -3)], ["0"])
    yield fmt_graph(3, [(0, 1, 1), (1, 2, -1), (2, 1, -1)], ["0"])
    # Negative cycle that the source can't reach: distances are still well defined.
    yield fmt_graph(5, [(0, 1, 4), (1, 2, -1), (3, 4, -5), (4, 3, 2)], ["0"])
    yield fmt_graph(4, [(1, 0, -3), (2, 3, 6)], ["0"])
    for n, m in ((6, 9), (8, 12), (10, 15)):
        # DAG with negative weights: never a negative cycle.
        yield fmt_graph(n, weighted(r, gen_dag(r, n, m), -20, 30), [str(r.randrange(n))])
    for n, m in ((6, 10), (8, 14)):
        yield fmt_graph(n, weighted(r, gen_pairs(r, n, m, directed=True), -5, 25), [str(r.randrange(n))])
    es = weighted(r, gen_dag(r, 300, 1200), -50, 100)
    yield fmt_graph(300, es, ["0"])


def _floyd_solve(inp):
    n, edges, _ = read_graph(inp)
    d = floyd(n, edges)
    return "\n".join(dist_line(row) for row in d)


def _floyd_brute(inp):
    n, edges, _ = read_graph(inp)
    g = adj_directed(n, edges, weighted=True)
    return "\n".join(dist_line(dijkstra(n, g, s)) for s in range(n))


def _floyd_tests(r):
    yield fmt_graph(1, [])
    yield fmt_graph(3, [])
    yield fmt_graph(3, [(0, 1, 4), (1, 2, 1), (0, 2, 9), (2, 0, 2)])
    yield fmt_graph(4, [(0, 1, 0), (1, 2, 0), (2, 3, 0)])
    for n, m in ((5, 8), (7, 12), (9, 20), (10, 15)):
        yield fmt_graph(n, weighted(r, gen_pairs(r, n, m, directed=True), 0, 40))
    yield fmt_graph(60, weighted(r, gen_pairs(r, 60, 900, directed=True), 1, 999))


def _mst(inp):
    n, edges, _ = read_graph(inp)
    d = DSU(n)
    total = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if d.union(u, v):
            total += w
    return str(total)


def _mst_brute(inp):
    n, edges, _ = read_graph(inp)
    best = [[INF] * n for _ in range(n)]
    for u, v, w in edges:
        best[u][v] = best[v][u] = min(best[u][v], w)
    in_tree = [False] * n
    key = [INF] * n
    key[0] = 0
    total = 0
    for _ in range(n):
        u = min((i for i in range(n) if not in_tree[i]), key=lambda i: key[i])
        in_tree[u] = True
        total += key[u]
        for v in range(n):
            if not in_tree[v] and best[u][v] < key[v]:
                key[v] = best[u][v]
    return str(total)


def _mst_tests(r):
    yield fmt_graph(1, [])
    yield fmt_graph(2, [(0, 1, 7)])
    yield fmt_graph(3, [(0, 1, 1), (1, 2, 1), (0, 2, 1)])
    yield fmt_graph(4, [(0, 1, 10), (1, 2, 1), (2, 3, 1), (3, 0, 1), (0, 2, 3)])
    for n, extra in ((6, 4), (8, 8), (10, 15), (12, 20)):
        yield fmt_graph(n, weighted(r, connected_pairs(r, n, extra), 1, 50))
    yield fmt_graph(600, weighted(r, connected_pairs(r, 600, 1300), 1, 10000))


def _connect_network(inp):
    n, edges, _ = read_graph(inp)
    if len(edges) < n - 1:
        return "-1"
    d = DSU(n)
    for u, v in edges:
        d.union(u, v)
    return str(len({d.find(x) for x in range(n)}) - 1)


def _connect_network_brute(inp):
    n, edges, _ = read_graph(inp)
    if len(edges) < n - 1:
        return "-1"
    return str(_count_comps_bfs(n, adj_undirected(n, edges)) - 1)


def _count_comps_bfs(n, g):
    seen, count = [False] * n, 0
    for s in range(n):
        if not seen[s]:
            count += 1
            for v, d in enumerate(bfs_dist(n, g, s)):
                if d >= 0:
                    seen[v] = True
    return count


def _connect_tests(r):
    yield fmt_graph(1, [])
    yield fmt_graph(3, [(0, 1)])
    yield fmt_graph(4, [(0, 1), (0, 2), (1, 2)])
    yield fmt_graph(6, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)])
    yield fmt_graph(5, [(0, 1), (1, 2), (2, 0), (3, 4)])
    for n, m in ((7, 6), (10, 12), (12, 11), (15, 20)):
        yield fmt_graph(n, gen_pairs(r, n, m))
    yield fmt_graph(1500, gen_pairs(r, 1500, 1800))


GRAPH_INPUT = """The first line has `n` and `m` — the number of nodes (numbered `0` to `n − 1`) and edges. Each of the next `m` lines has an edge"""

PROBLEMS = [
    Problem(
        title="BFS Traversal of a Graph",
        difficulty="EASY",
        topics=["Graph", "BFS"],
        description=f"""Breadth-first search explores a graph in rings: first the start node, then everything one edge away, then everything two edges away, and so on.

Run BFS on an **undirected** graph from node `s` and print the nodes in the order they are visited. Whenever a node's neighbours are added to the queue, add them in **increasing order**. Nodes that can't be reached from `s` are not printed.

**Input:** {GRAPH_INPUT} `u v`. The last line has the start node `s`.

**Output:** the visited nodes in BFS order, space-separated.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "no repeated edges or self-loops"],
        solve=_bfs_traversal,
        brute=_bfs_traversal_brute,
        examples=[
            ("5 4\n0 1\n0 2\n1 3\n2 4\n0", "From 0 visit 1 and 2, then their neighbours 3 and 4."),
            ("4 2\n2 3\n0 1\n2", "Only 3 is reachable from 2."),
        ],
        tests=_traversal_tests,
    ),
    Problem(
        title="DFS Traversal of a Graph",
        difficulty="EASY",
        topics=["Graph", "DFS"],
        description=f"""Depth-first search follows one path as deep as it can before backing up to try the next branch.

Run a recursive DFS on an **undirected** graph from node `s`: visit a node, then recurse into each unvisited neighbour in **increasing order**. Print the nodes in the order they are first visited. Unreachable nodes are not printed.

**Input:** {GRAPH_INPUT} `u v`. The last line has the start node `s`.

**Output:** the visited nodes in DFS order, space-separated.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "no repeated edges or self-loops"],
        solve=_dfs_traversal,
        brute=_dfs_traversal_brute,
        examples=[
            ("5 4\n0 1\n0 2\n1 3\n2 4\n0", "0 → 1 → 3, back up, then 2 → 4."),
            ("4 3\n0 3\n0 1\n1 3\n0", "From 0 go to 1 first (smaller), then 1 → 3."),
        ],
        tests=_traversal_tests,
    ),
    Problem(
        title="Number of Provinces",
        difficulty="MEDIUM",
        topics=["Graph", "DFS", "Union Find"],
        description="""There are `n` cities. City `i` and city `j` are directly connected when `M[i][j] = 1`. Cities connected directly or through other cities form one **province**.

Given the connection matrix `M`, print the number of provinces.

**Input:** the first line has `n`. Each of the next `n` lines has `n` space-separated values `0` or `1`. The matrix is symmetric and `M[i][i] = 1`.

**Output:** the number of provinces.""",
        constraints=["1 <= n <= 100"],
        solve=_provinces,
        brute=_provinces_brute,
        examples=[
            ("3\n1 1 0\n1 1 0\n0 0 1", "Cities 0 and 1 are one province; city 2 is alone."),
            ("3\n1 0 0\n0 1 0\n0 0 1", "Nobody is connected: three provinces."),
        ],
        tests=_provinces_tests,
    ),
    Problem(
        title="Flood Fill",
        difficulty="EASY",
        topics=["Graph", "DFS", "Matrix"],
        description="""An image is a grid of single-digit colors. Starting from pixel `(sr, sc)`, repaint it and every pixel connected to it **up, down, left or right** through pixels of the **same original color** with the new color `k`.

Print the image after the fill. If `k` equals the starting pixel's color, nothing changes.

**Input:** the first line has `r c`. Each of the next `r` lines has `c` digits with no spaces. The last line has `sr sc k`.

**Output:** the `r` rows of the filled image, digits with no spaces.""",
        constraints=["1 <= r, c <= 100", "0 <= k <= 9"],
        solve=_flood_fill,
        brute=_flood_fill_brute,
        examples=[
            ("3 3\n111\n110\n101\n1 1 2", "Every 1 connected to the centre turns into 2; the bottom-right 1 is cut off."),
            ("2 3\n000\n000\n0 0 0", "New color equals the old one, so the image is unchanged."),
        ],
        tests=_flood_tests,
    ),
    Problem(
        title="Rotting Oranges",
        difficulty="MEDIUM",
        topics=["Graph", "BFS", "Matrix"],
        description="""Each cell of a grid is `0` (empty), `1` (fresh orange) or `2` (rotten orange). Every minute, each fresh orange that is directly up, down, left or right of a rotten orange becomes rotten.

Print the minimum number of minutes until no fresh orange is left, or `-1` if some fresh orange can never rot. If there are no fresh oranges at the start, the answer is `0`.

**Input:** the first line has `r c`. Each of the next `r` lines has `c` digits with no spaces.

**Output:** the number of minutes, or `-1`.""",
        constraints=["1 <= r, c <= 100"],
        solve=_rotting,
        brute=_rotting_brute,
        examples=[
            ("3 3\n211\n110\n011", "The rot spreads from the top-left corner and reaches the last orange after 4 minutes."),
            ("3 3\n211\n011\n101", "The bottom-left orange is isolated, so it never rots."),
        ],
        tests=_rotting_tests,
    ),
    Problem(
        title="Distance to Nearest Zero",
        difficulty="MEDIUM",
        topics=["Graph", "BFS", "Matrix"],
        description="""Given a grid of `0`s and `1`s, find for every cell the distance to the nearest `0`, moving one step up, down, left or right at a time. Cells that are `0` have distance `0`. The grid has at least one `0`.

Running a BFS from every cell is slow. Start one BFS from **all zeros at once** instead.

**Input:** the first line has `r c`. Each of the next `r` lines has `c` digits with no spaces.

**Output:** `r` lines, each with `c` space-separated distances.""",
        constraints=["1 <= r, c <= 100", "the grid contains at least one 0"],
        solve=_nearest_zero,
        brute=_nearest_zero_brute,
        examples=[
            ("3 3\n000\n010\n111", "The bottom-middle cell is 2 steps from the nearest 0."),
            ("1 4\n1101", "Distances along the row: 2 1 0 1."),
        ],
        tests=_nearest_zero_tests,
    ),
    Problem(
        title="Surrounded Regions",
        difficulty="MEDIUM",
        topics=["Graph", "DFS", "Matrix"],
        description="""A board is made of `X` and `O` cells. A group of `O`s connected up, down, left or right is **captured** if none of its cells lies on the border of the board. Captured groups are flipped to `X`.

Print the board after flipping every captured group.

Tip: instead of checking each group, start from the `O`s on the border and mark everything they reach — whatever is left unmarked gets captured.

**Input:** the first line has `r c`. Each of the next `r` lines has `c` characters (`X` or `O`) with no spaces.

**Output:** the `r` rows of the resulting board.""",
        constraints=["1 <= r, c <= 100"],
        solve=_surrounded,
        brute=_surrounded_brute,
        examples=[
            ("4 4\nXXXX\nXOOX\nXXOX\nXOXX", "The middle group is enclosed and flips; the bottom O touches the border and stays."),
            ("2 2\nOO\nOX", "Every O is on the border."),
        ],
        tests=_surrounded_tests,
    ),
    Problem(
        title="Number of Enclaves",
        difficulty="MEDIUM",
        topics=["Graph", "BFS", "Matrix"],
        description="""In a grid, `1` is land and `0` is sea. From a land cell you can walk to an adjacent land cell (up, down, left, right), and you can walk off the grid from any land cell on the border.

Print the number of land cells from which it is **impossible** to walk off the grid.

**Input:** the first line has `r c`. Each of the next `r` lines has `c` digits with no spaces.

**Output:** the number of enclosed land cells.""",
        constraints=["1 <= r, c <= 100"],
        solve=_enclaves,
        brute=_enclaves_brute,
        examples=[
            ("4 4\n0000\n1010\n0110\n0000", "The three 1s in the middle are boxed in; the 1 on the left edge can walk off."),
            ("3 3\n010\n010\n010", "The column touches the top and bottom borders."),
        ],
        tests=_enclaves_tests,
    ),
    Problem(
        title="Detect Cycle in an Undirected Graph",
        difficulty="MEDIUM",
        topics=["Graph", "DFS", "Union Find"],
        description=f"""Print `true` if an **undirected** graph contains a cycle, otherwise `false`. The graph can be disconnected.

During a DFS or BFS, reaching an already-visited node that isn't the one you came from means you have found a cycle.

**Input:** {GRAPH_INPUT} `u v`.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "no repeated edges or self-loops"],
        solve=_cycle_undirected,
        brute=_cycle_undirected_brute,
        examples=[
            ("4 4\n0 1\n1 2\n2 3\n3 1", "1 → 2 → 3 → 1 is a cycle."),
            ("4 2\n0 1\n2 3", "Two separate edges, no cycle."),
        ],
        tests=_cycle_undirected_tests,
    ),
    Problem(
        title="Is Graph Bipartite",
        difficulty="MEDIUM",
        topics=["Graph", "BFS", "DFS"],
        description=f"""An **undirected** graph is bipartite if its nodes can be split into two groups so that every edge connects nodes from different groups — equivalently, if you can color each node with one of two colors so no edge joins two nodes of the same color.

Print `true` if the graph is bipartite, otherwise `false`. The graph can be disconnected.

**Input:** {GRAPH_INPUT} `u v`.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "no repeated edges or self-loops"],
        solve=_bipartite,
        brute=_bipartite_brute,
        examples=[
            ("4 4\n0 1\n1 2\n2 3\n3 0", "Color 0 and 2 one way, 1 and 3 the other."),
            ("3 3\n0 1\n1 2\n2 0", "A triangle needs three colors."),
        ],
        tests=_bipartite_tests,
    ),
    Problem(
        title="Detect Cycle in a Directed Graph",
        difficulty="MEDIUM",
        topics=["Graph", "DFS", "Topological Sort"],
        description=f"""Print `true` if a **directed** graph contains a cycle (a path that leads from a node back to itself), otherwise `false`. A self-loop counts as a cycle.

One way: run Kahn's algorithm — repeatedly remove nodes with no incoming edges. If some nodes can never be removed, they sit on a cycle.

**Input:** {GRAPH_INPUT} `u v` going from `u` to `v`.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "no repeated edges"],
        solve=_cycle_directed,
        brute=_cycle_directed_brute,
        examples=[
            ("4 4\n0 1\n1 2\n2 3\n3 1", "1 → 2 → 3 → 1."),
            ("4 4\n0 1\n0 2\n1 3\n2 3", "Two paths to 3 but no way back: no cycle."),
        ],
        tests=_directed_cycle_tests,
    ),
    Problem(
        title="Topological Sort",
        difficulty="MEDIUM",
        topics=["Graph", "Topological Sort", "Heap"],
        description=f"""A topological order of a **directed acyclic graph** lists every node so that each edge `u → v` has `u` before `v`.

Many orders can be valid, so print the **lexicographically smallest** one: whenever several nodes are ready (all their predecessors are placed), take the smallest. Kahn's algorithm with a min-heap does exactly this.

**Input:** {GRAPH_INPUT} `u v` going from `u` to `v`. The graph has no cycles.

**Output:** the topological order, space-separated.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "the graph is acyclic"],
        solve=_topo,
        brute=_topo_brute,
        examples=[
            ("6 6\n5 2\n5 0\n4 0\n4 1\n2 3\n3 1", "1, 2 and 3 must wait; 4 is the smallest node free at the start."),
            ("3 0", "No edges: every order is valid, the smallest is 0 1 2."),
        ],
        tests=_topo_tests,
    ),
    Problem(
        title="Course Schedule",
        difficulty="MEDIUM",
        topics=["Graph", "Topological Sort"],
        description="""There are `n` courses numbered `0` to `n − 1`. A prerequisite pair `a b` means you must finish course `b` before course `a`.

Print `true` if it is possible to finish every course, otherwise `false`. It's impossible exactly when the prerequisites form a cycle.

**Input:** the first line has `n` and `m` (the number of prerequisite pairs). Each of the next `m` lines has a pair `a b`.

**Output:** `true` or `false`.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "no repeated pairs"],
        solve=_course_schedule,
        brute=_course_schedule_brute,
        examples=[
            ("2 1\n1 0", "Take 0, then 1."),
            ("2 2\n1 0\n0 1", "Each course needs the other first."),
        ],
        tests=lambda r: _directed_cycle_tests(r, flip=True),
    ),
    Problem(
        title="Shortest Path in an Unweighted Graph",
        difficulty="MEDIUM",
        topics=["Graph", "BFS", "Shortest Path"],
        description=f"""In an **undirected** graph where every edge has length 1, find the shortest distance from node `s` to every node. BFS finds these distances in `O(n + m)`.

**Input:** {GRAPH_INPUT} `u v`. The last line has the source `s`.

**Output:** `n` space-separated distances, where the `i`-th is the distance from `s` to node `i`, or `-1` if `i` is unreachable.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "no repeated edges or self-loops"],
        solve=_unweighted_sp,
        brute=_unweighted_sp_brute,
        examples=[
            ("6 6\n0 1\n0 2\n1 3\n2 3\n3 4\n4 5\n0", "Node 5 is four edges away: 0 → 1 → 3 → 4 → 5."),
            ("3 1\n0 1\n1", "Node 2 can't be reached."),
        ],
        tests=_traversal_tests,
    ),
    Problem(
        title="Shortest Path in a Binary Maze",
        difficulty="MEDIUM",
        topics=["Graph", "BFS", "Matrix", "Shortest Path"],
        description="""A maze is a grid where `1` is an open cell and `0` is a wall. From an open cell you can step to an adjacent open cell up, down, left or right.

Print the minimum number of steps from `(sr, sc)` to `(tr, tc)`, or `-1` if the target can't be reached (including when the start or target is a wall).

**Input:** the first line has `r c`. Each of the next `r` lines has `c` digits with no spaces. The last line has `sr sc tr tc`.

**Output:** the minimum number of steps, or `-1`.""",
        constraints=["1 <= r, c <= 100"],
        solve=_maze,
        brute=_maze_brute,
        examples=[
            ("3 4\n1101\n1111\n1011\n0 0 2 3", "Go down, then right along the middle row, then down: 5 steps."),
            ("2 2\n10\n01\n0 0 1 1", "The two open cells only touch diagonally."),
        ],
        tests=_maze_tests,
    ),
    Problem(
        title="Word Ladder Length",
        difficulty="HARD",
        topics=["Graph", "BFS"],
        description="""You can turn a word into another by changing **one letter at a time**, and every word you pass through (including the final one) must be in the given word list. The starting word doesn't need to be in the list.

Print the number of words in the shortest such sequence from `begin` to `end`, counting both `begin` and `end`. Print `0` if no sequence exists. All words have the same length and use lowercase letters, and `begin` differs from `end`.

**Input:** the first line has `begin`, the second `end`, the third the number of words `k`, followed by `k` lines with one word each.

**Output:** the length of the shortest sequence, or `0`.""",
        constraints=["1 <= word length <= 10", "1 <= k <= 5000"],
        solve=_word_ladder,
        brute=_word_ladder_brute,
        examples=[
            ("hit\ncog\n6\nhot\ndot\ndog\nlot\nlog\ncog", "hit → hot → dot → dog → cog is 5 words."),
            ("hit\ncog\n5\nhot\ndot\ndog\nlot\nlog", "cog isn't in the list, so it can't be reached."),
        ],
        tests=_ladder_tests,
    ),
    Problem(
        title="Dijkstra's Shortest Paths",
        difficulty="MEDIUM",
        topics=["Graph", "Shortest Path", "Heap"],
        description=f"""Find the shortest distance from node `s` to every node in a **directed** graph with non-negative edge weights.

Dijkstra's algorithm repeatedly takes the closest unfinished node from a min-heap and relaxes its outgoing edges, in `O((n + m) log n)`.

**Input:** {GRAPH_INPUT} `u v w` going from `u` to `v` with weight `w`. The last line has the source `s`.

**Output:** `n` space-separated distances, where the `i`-th is the distance from `s` to node `i`, or `-1` if `i` is unreachable.""",
        constraints=["1 <= n <= 1000", "0 <= m <= 3000", "0 <= w <= 10^4"],
        solve=_dijkstra,
        brute=_dijkstra_brute,
        examples=[
            ("4 5\n0 1 4\n0 2 1\n2 1 2\n1 3 1\n2 3 5\n0", "0 → 2 → 1 costs 3, cheaper than the direct edge of 4."),
            ("3 1\n1 2 7\n0", "Edges only leave node 1, so nothing is reachable from 0."),
        ],
        tests=_weighted_tests,
    ),
    Problem(
        title="Network Delay Time",
        difficulty="MEDIUM",
        topics=["Graph", "Shortest Path", "Heap"],
        description=f"""A signal starts at node `k` and travels along **directed** edges, each taking `w` time units. Print how long it takes until **every** node has received the signal, or `-1` if some node never receives it.

That's the largest shortest-path distance from `k`.

**Input:** {GRAPH_INPUT} `u v w` going from `u` to `v` with travel time `w`. The last line has `k`.

**Output:** the time for all nodes to receive the signal, or `-1`.""",
        constraints=["1 <= n <= 100", "0 <= m <= 6000", "1 <= w <= 1000"],
        solve=_network_delay,
        brute=_network_delay_brute,
        examples=[
            ("4 3\n1 0 1\n1 2 1\n2 3 1\n1", "Node 3 is the last to hear the signal, after 2 units."),
            ("2 1\n0 1 1\n1", "From node 1 the signal can't reach node 0."),
        ],
        tests=_network_tests,
    ),
    Problem(
        title="Cheapest Flights Within K Stops",
        difficulty="MEDIUM",
        topics=["Graph", "Shortest Path"],
        description=f"""Cities are connected by one-way flights with prices. Find the cheapest way to fly from `src` to `dst` with **at most `k` stops** in between (that is, at most `k + 1` flights). Print `-1` if there's no such route. Flying from a city to itself costs `0`.

Plain Dijkstra ignores the stop limit. Run Bellman-Ford for `k + 1` rounds instead, updating from a copy of the previous round's costs.

**Input:** {GRAPH_INPUT} `u v p`: a flight from `u` to `v` costing `p`. The last line has `src dst k`.

**Output:** the cheapest price, or `-1`.""",
        constraints=["1 <= n <= 200", "0 <= m <= 2000", "1 <= p <= 10^4", "0 <= k <= 10"],
        solve=_flights,
        brute=_flights_brute,
        examples=[
            ("4 5\n0 1 100\n1 2 100\n2 0 100\n1 3 600\n2 3 200\n0 3 1", "0 → 1 → 3 costs 700. The cheaper 0 → 1 → 2 → 3 needs two stops."),
            ("3 3\n0 1 100\n1 2 100\n0 2 500\n0 2 0", "With no stops only the direct flight works."),
        ],
        tests=_flights_tests,
    ),
    Problem(
        title="Bellman-Ford with Negative Cycle Detection",
        difficulty="HARD",
        topics=["Graph", "Shortest Path"],
        description=f"""Edge weights in a **directed** graph can be negative. Find the shortest distance from `s` to every node with Bellman-Ford: relax every edge `n − 1` times. If any edge can still be relaxed afterwards, a **negative cycle** is reachable from `s` and shortest paths don't exist.

A negative cycle that `s` can't reach doesn't matter.

**Input:** {GRAPH_INPUT} `u v w` going from `u` to `v` with weight `w`. The last line has the source `s`.

**Output:** `NEGATIVE CYCLE` if a negative cycle is reachable from `s`. Otherwise `n` space-separated distances, using `INF` for unreachable nodes.""",
        constraints=["1 <= n <= 500", "0 <= m <= 2000", "-10^4 <= w <= 10^4"],
        solve=_bf_negative,
        brute=_bf_negative_brute,
        examples=[
            ("4 4\n0 1 4\n0 2 5\n2 1 -3\n1 3 2\n0", "0 → 2 → 1 costs 2, which beats the direct edge."),
            ("3 3\n0 1 1\n1 2 -1\n2 1 -1\n0", "1 → 2 → 1 has total weight −2 and is reachable."),
        ],
        tests=_bf_tests,
    ),
    Problem(
        title="Floyd-Warshall All Pairs",
        difficulty="MEDIUM",
        topics=["Graph", "Shortest Path"],
        description=f"""Find the shortest distance between **every pair** of nodes in a **directed** graph with non-negative weights.

Floyd-Warshall tries each node `k` as a midpoint: `dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])`, in `O(n³)`.

**Input:** {GRAPH_INPUT} `u v w` going from `u` to `v` with weight `w`.

**Output:** `n` lines with `n` space-separated values each: row `i`, column `j` is the distance from `i` to `j`, `0` when `i = j`, or `-1` if `j` is unreachable from `i`.""",
        constraints=["1 <= n <= 100", "0 <= m <= 3000", "0 <= w <= 1000"],
        solve=_floyd_solve,
        brute=_floyd_brute,
        examples=[
            ("3 3\n0 1 4\n1 2 1\n2 0 2", "0 → 1 → 2 costs 5; 2 → 0 → 1 costs 6."),
            ("2 0", "No edges: only the diagonal is reachable."),
        ],
        tests=_floyd_tests,
    ),
    Problem(
        title="Minimum Spanning Tree Weight",
        difficulty="MEDIUM",
        topics=["Graph", "Minimum Spanning Tree", "Union Find", "Greedy"],
        description=f"""A spanning tree of a connected, **undirected**, weighted graph is a set of `n − 1` edges that connects all nodes. Print the smallest possible total weight of a spanning tree.

Kruskal's algorithm sorts the edges by weight and adds each one that joins two different components (tracked with union-find). Prim's algorithm grows the tree from one node instead.

**Input:** {GRAPH_INPUT} `u v w`. The graph is connected.

**Output:** the total weight of a minimum spanning tree.""",
        constraints=["1 <= n <= 1000", "n − 1 <= m <= 3000", "1 <= w <= 10^4", "no repeated edges or self-loops"],
        solve=_mst,
        brute=_mst_brute,
        examples=[
            ("4 5\n0 1 10\n0 2 6\n0 3 5\n1 3 15\n2 3 4", "Take 4, 5 and 10 for a total of 19."),
            ("1 0", "A single node needs no edges."),
        ],
        tests=_mst_tests,
    ),
    Problem(
        title="Number of Operations to Connect the Network",
        difficulty="MEDIUM",
        topics=["Graph", "Union Find"],
        description=f"""`n` computers are linked by `m` cables, each joining two computers. In one operation you can unplug any cable and plug it between two other computers.

Print the minimum number of operations needed so that every computer can reach every other, or `-1` if there aren't enough cables (a connected network needs at least `n − 1`).

If there are enough cables, the answer is the number of separate groups minus one: each redundant cable can join two groups.

**Input:** {GRAPH_INPUT} (cable) `u v`.

**Output:** the minimum number of operations, or `-1`.""",
        constraints=["1 <= n <= 2000", "0 <= m <= 3000", "no repeated cables or self-loops"],
        solve=_connect_network,
        brute=_connect_network_brute,
        examples=[
            ("4 3\n0 1\n0 2\n1 2", "Move the redundant cable 1–2 to connect computer 3."),
            ("6 4\n0 1\n0 2\n0 3\n1 2", "Only 4 cables for 6 computers."),
        ],
        tests=_connect_tests,
    ),
]
