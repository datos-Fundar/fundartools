from .utils import mapper, Mapper, Range, Indexable, BoundedInt, BoundedFloat, Max
from typing import TypeVar

A = TypeVar('A')
B = TypeVar('B')

N = TypeVar('N', float, float)
M = TypeVar('M', float, float)

normaliser: Mapper[[Range[0, 1]], ...] = mapper(0, 1)
"""
Normaliza un valor en el rango [0, 1].

Uso:
    normaliser(x, n, m) -> y
    Donde:
        x es es un numero que está entre [n, m]
        y es un número que está entre [0, 1]
"""

inverse_normaliser: Mapper[[Range[1, 0]], ...] = mapper(1, 0)
"""
Normaliza un valor en el rango [1, 0].

Uso:
    inverse_normaliser(x, n, m) -> y
    Donde:
        x es es un numero que está entre [n, m]
        y es un número que está entre [1, 0]
"""

def levenshtein_distance(a: Indexable[A], b: Indexable[A]) -> BoundedInt[0, Max[N, M]]:
    """
    Calcula la distancia de Levenshtein entre dos elementos. La distancia de Levenshtein es el número mínimo de
    operaciones requeridas para transformar una cadena en otra. 
    Las operaciones permitidas son inserción, eliminación y sustitución.

    Args:
        a: Indexable[A], donde len(a) = N
        b: Indexable[A], donde len(b) = M
        resultado: BoundedInt[0, max(N, M)]
    """
    n = len(a)
    m = len(b)

    matrix = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        matrix[i][0] = i

    for j in range(m + 1):
        matrix[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,  # deletion
                matrix[i][j - 1] + 1,  # insertion
                matrix[i - 1][j - 1] + cost  # substitution
            )

    # The bottom-right cell contains the minimum edit distance
    return matrix[n][m]

def normalized_levenshtein_similarity(a: Indexable[A], b: Indexable[A], mapper: Mapper[[Range[N, M]], ...] = None) -> BoundedFloat[N, M]:
    """
    Calcula la distancia de Levenshtein entre dos elementos y la normaliza en un rango.
    Si se usa el rango predefinido, el resultado estará en el rango [0, 1].
    Donde,
        0 significa que las cadenas son completamente distintas.
        1 significa que las cadenas son exactamente iguales.

    Args:
        a: Indexable[A]
        b: Indexable[B]
        mapper: Mapper[[N, M], ...], default = None
        resultado: BoundedFloat[N, M]
    """
    mapper = mapper or inverse_normaliser
    
    max_len = max(len(a), len(b))
    distance = levenshtein_distance(a,b)
    normalised_distance = mapper(distance, 0, max_len)
    
    return normalised_distance

def jaccard_similarity(a: set[A], b: set[A]) -> BoundedFloat[0, 1]:
    """
    Calcula la similitud de Jaccard entre dos conjuntos.
    La similitud de Jaccard es, intuitivamente, la proporción de elementos en común entre dos conjuntos.
    En particular, es el cociente entre los tamaños de la intersección y la unión de los conjuntos.

    El resultado es un número entre 0 y 1, donde:
        0 significa que los conjuntos son completamente disjuntos.
        1 significa que los conjuntos son exactamente iguales.

    Args:
        a: set[A]
        b: set[A]
        resultado: BoundedFloat[0, 1]
    """
    intersect_n = len(a & b)
    union_n = len(a | b)
    return intersect_n / union_n