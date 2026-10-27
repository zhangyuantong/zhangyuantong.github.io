---
title: Traffic Jam for Snails
date: 2025-10-19
tags: brain-teaser, probability
excerpt: N snails on a one-way road, each moving at its own number. The expected number of groups is the harmonic series.
---

Suppose there are $N$ snails and we number them through 1 to $N$, and surprisingly their speed is exactly the same as their number: snail No.1 has a speed of 1m/s, snail No.2 has a speed of 2m/s and etc. Then we randomly place them on a one way road and they start moving. If a fast snail encounters a slow snail, the fast one will reduce its speed and they form a group of snails. If a snail has a speed that no snail can chase it and it cannot chase any other snail, then it forms a group of snails by itself. After a really really long time, what is the expected number of groups of snails?

The answer is $\sum_{n=1}^{N} \frac{1}{n}$. Let's break it down step by step.

We just need to consider how many **leaders** there will be, so we can figure out how many groups will finally be formed.

- The first snail (by location) will always lead a group.
- The probability of the second snail leading a group, which is the same as the probability that the second snail is slower than the first one, is $\frac{1}{2}$.
  - Just a probability trick: for any two random numbers $a$ and $b$, the probability that $a$ is greater than $b$ is, by symmetry, $\frac{1}{2}$.
  - Or you can validate this by calculation:
    - If the first snail is No.100, then among all 99 snails left, the probability that the second snail is slower is $99/99$,
    - If the first snail is No.99, then among all 99 snails left, the probability that the second snail is slower is $98/99$,
    - $\cdots$
    - Combine all these cases: the probability that the first snail is No.100 is $1/100$ and that of the second snail is slower is $99/99$, and so on
    - $\sum_{p=1}^{100}\frac{p-1}{99}\cdot\frac{1}{100} = \frac{1}{100}\cdot\frac{1}{99}\sum_{p=0}^{99}p = \frac{1}{100}\cdot\frac{\frac{(0+99)\cdot100}{2}}{99} = \frac{1}{100}\cdot50=0.5$
- The probability of the third snail leading a group, which is the same as the probability that the third snail is slower than the first two, is $\frac{1}{3}$.
  - The rationale is the same, so let's skip the calculation. By intuition, we are actually choosing the smallest number among three random numbers $a$, $b$, and $c$. The probability that $a$ is the smallest is $\frac{1}{3}$.
- $\cdots$
- Combining all these cases, the expected number will be $\sum_{n=1}^{N} \frac{1}{n}$.

A simple Python snippet to validate the result.

```python
import numpy as np

num_of_snails = 100
num_of_trials = 10000000

all_snails = np.array([np.random.permutation(num_of_snails)+1 for _ in range(num_of_trials)])

cum_min = np.minimum.accumulate(all_snails, axis=1)

unique_counts = np.array([len(np.unique(row)) for row in cum_min])

print(np.mean(unique_counts))
```
