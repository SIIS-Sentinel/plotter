import pstats
from pstats import SortKey

p = pstats.Stats("results")

p.sort_stats(SortKey.TIME)
p.print_stats()
