def levenshtein(s, t):
    n = len(s)
    m = len(t)

    if n == 0:
        return m
    if m == 0:
        return n

    prev = [i for i in range(m + 1)]
    curr = [0 for i in range(m + 1)]

    for i in range(n):
        curr[0] = i + 1
        for j in range(m):
            cost = 1 if s[i] != t[j] else 0
            curr[j + 1] = min(
                curr[j] + 1,  # cell above + 1 (deletion)
                prev[j + 1] + 1,  # cell on the left + 1 (insertion)
                # cell diagonal above and left + cost (substitution)
                prev[j] + cost,
            )
        prev, curr = curr, prev

    return prev[m]


def similarity(s, t):
    lev_dist = levenshtein(s, t)
    max_len = max(len(s), len(t))
    if max_len == 0:
        return 1
    return 1 - float(lev_dist) / float(max_len)
