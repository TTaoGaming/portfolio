"""Data-only 425-operation seed; not executable candidate code.
Change the literal recipe, never the frozen evaluator or target.
DEFERRED entries are (tail_segment_index, left_exponent, right_exponent).
"""
# EVOLVE-BLOCK-START
SMALL = [(1,1),(2,2),(1,4),(4,5),(4,9),(9,13),(5,22),(22,27),(1,49),(9,50),(4,59),(22,49)]
PREFIX_BASE = 63
PREFIX_SHIFTS = [6,12,24,48,96]
DEFERRED = [(2,1,50)]
TAIL = [(6,49),(5,27),(9,51),(5,59),(12,50),(2,50),(8,27),(7,71),(4,71),(7,59),(4,59),(10,13),(10,27),(7,50),(8,71),(4,27),(7,5),(8,59),(4,13),(7,59),(8,59),(11,50),(6,50),(3,27),(8,51),(10,51),(2,126),(4,5),(6,49)]
# EVOLVE-BLOCK-END
