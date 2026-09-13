# D05 proposal: groups of up to four traversers in average checks

D04 rejects two-player groups: only21% fewer CDF rows. However, across all
eight players the exact global union is692,628 rows versus2,419,357 rows
summed across separate traversers. Investigate whether groups of three or
four capture enough of that overlap within23GB and unchanged batch32.

Use the same frozen saves, common average down sweep, ungated normalized
vectors and bitwise interner. Additionally collect a player-membership mask
for every distinct distribution and every static slot. Histogram these masks;
the union size for any subset is the sum of counts whose mask intersects it.
Verify histogram-derived singleton/pair unions against D04-style explicit
sets. This makes exhaustive partition enumeration inexpensive without hiding
unfavorable groups or requiring another GPU pass for each proposed grouping.

Enumerate every partition with groups of at most four, allowing singletons.
Count full-check CDF rows and static peak allocation; add(max group size-1)
full d_val arenas and probability arrays. Include all group remaps/worklists,
normalized/classification buffers, existing learning maps and driver reserve.
Report the Pareto frontier of work reduction versus memory, natural groups
and the best fitting plan. Do not allocate based on the observed unique row
count: it can change during later checks. Constructor preplanning remains
mandatory to avoid the allocate-before-release peak seen in D04.

Register a protocol before running. Admission threshold remains at least25%
fewer full-check CDF rows, static plan including reserve<=23GB, unchanged
batch32/1024 particles/cache. No learn/update path changes. A successful
inventory merely admits a prototype; all terminal/checkpoint/arena bits,
capture/frozen/forced/zero-reach behavior and complete paired timings still
need to qualify before retention. No numerical shortcuts or speed claims.
