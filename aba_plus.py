import numpy as np

NO_RELATION = 3

# in relation_matrix, use 1 for < and 2 for <=
def transitive_closure(relation_matrix):
    n = len(relation_matrix)
    d = np.copy(relation_matrix)

    for k in range(0, n):
        for i in range(0, n):
            for j in range(0, n):
                alt_rel = NO_RELATION
                if not (d[i][k] == NO_RELATION or d[k][j] == NO_RELATION):
                    alt_rel = min(d[i][k], d[k][j])

                d[i][j] = min(d[i][j], alt_rel)

    return d
