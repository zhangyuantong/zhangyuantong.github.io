---
title: "Ordinary Least Squares: Assumptions and Statistical Properties"
date: 2025-10-20
tags: econ, statistics
excerpt: A rigorous derivation of the OLS estimator, its unbiasedness, consistency, and asymptotic normality under classical linear model assumptions.
---

## 1. Model setup

We consider the standard linear regression model in matrix form:

$$
y = X\beta + \varepsilon,
$$

where

- $y \in \mathbb{R}^{n\times 1}$ is the vector of dependent variables,
- $X \in \mathbb{R}^{n\times k}$ is the regressor matrix (assume full column rank $k$),
- $\beta \in \mathbb{R}^{k\times 1}$ is the vector of parameters,
- $\varepsilon \in \mathbb{R}^{n\times 1}$ is the disturbance vector.

## 2. Classical assumptions (Gauss–Markov style)

1. **Linearity.** The data-generating process is $y = X\beta + \varepsilon$.
2. **Full rank.** $\mathrm{rank}(X)=k$, so $X'X$ is invertible.
3. **Exogeneity.** $\mathbb{E}[\varepsilon\mid X]=0$ (zero conditional mean).
4. **Homoskedasticity & No serial correlation.** $\mathrm{Var}(\varepsilon\mid X)=\sigma^2 I_n$.
5. **Finite moments.** $\mathbb{E}[\varepsilon_i^2]<\infty$.
6. **(For large-sample results)** As $n\to\infty$, $\frac{1}{n}X'X \xrightarrow{p} Q$ where $Q$ is positive definite.

## 3. OLS estimator: derivation

The OLS estimator minimizes the residual sum of squares:

$$
\hat\beta = \arg\min_b (y-Xb)'(y-Xb).
$$

Differentiate with respect to $b$ and set the gradient to zero:

$$
\frac{\partial}{\partial b} (y-Xb)'(y-Xb) = -2X'(y-Xb) = 0.
$$

Solving the normal equations yields the closed form:

$$
\boxed{\hat\beta = (X'X)^{-1}X'y.}
$$

Substituting $y=X\beta+\varepsilon$ gives the useful decomposition

$$
\hat\beta = \beta + (X'X)^{-1}X'\varepsilon.
$$

## 4. Unbiasedness

Take expectations conditional on $X$:

$$
\mathbb{E}[\hat\beta\mid X] = \beta + (X'X)^{-1}X'\mathbb{E}[\varepsilon\mid X] = \beta.
$$

Therefore

$$
\boxed{\mathbb{E}[\hat\beta]=\beta,}
$$

so $\hat\beta$ is unbiased under the zero conditional mean assumption.

## 5. Variance of $\hat\beta$

Starting from the OLS estimator:

$$
\hat\beta = \beta + (X'X)^{-1}X'\varepsilon.
$$

Because $\beta$ is non-random (or we condition on $X$), the sampling variability of $\hat\beta$ comes from the term $(X'X)^{-1}X'\varepsilon$. Compute its conditional variance given $X$:

$$
\begin{aligned}
\mathrm{Var}(\hat\beta\mid X)
&= \mathrm{Var}\!\left((X'X)^{-1}X'\varepsilon \;\middle|\; X\right) \\
&= (X'X)^{-1}X'\,\mathrm{Var}(\varepsilon\mid X)\,X(X'X)^{-1}.
\end{aligned}
$$

Under the **homoskedasticity** and **no serial correlation** assumption,

$$
\mathrm{Var}(\varepsilon\mid X)=\sigma^2 I_n,
$$

so

$$
\begin{aligned}
\mathrm{Var}(\hat\beta\mid X)
&= (X'X)^{-1}X'(\sigma^2 I_n)X(X'X)^{-1} \\
&= \sigma^2 (X'X)^{-1}(X'X)(X'X)^{-1} \\
&= \sigma^2 (X'X)^{-1}.
\end{aligned}
$$

Hence, conditional on $X$,

$$
\boxed{\mathrm{Var}(\hat\beta\mid X)=\sigma^2 (X'X)^{-1}.}
$$

This is the finite-sample covariance of the OLS estimator. If $X$ is random, this can be interpreted conditionally on the realized design matrix.

### 5.1 Unbiased estimator of $\sigma^2$

Because $\sigma^2$ is usually unknown, we estimate it from the residuals. Define

$$
\hat\varepsilon = y - X\hat\beta = (I_n - P)y,
\qquad P := X(X'X)^{-1}X'
$$

where $P$ is the **projection matrix** onto the column space of $X$. The residual sum of squares (SSR) is

$$
\mathrm{SSR} = \hat\varepsilon'\hat\varepsilon = y'(I_n - P)y.
$$

Under the model $y = X\beta + \varepsilon$, with $\mathbb{E}[\varepsilon\mid X]=0$, we have

$$
\mathrm{SSR} = \varepsilon'(I_n - P)\varepsilon.
$$

Take expectations conditional on $X$:

$$
\mathbb{E}[\mathrm{SSR}\mid X]
= \mathbb{E}\big[\varepsilon'(I_n-P)\varepsilon \mid X\big]
= \sigma^2\,\mathrm{tr}(I_n - P).
$$

Since $\mathrm{tr}(P)=\mathrm{rank}(P)=k$, we have $\mathrm{tr}(I_n - P)=n-k$. Thus,

$$
\mathbb{E}[\mathrm{SSR}\mid X] = (n-k)\sigma^2.
$$

Therefore, the **unbiased estimator of $\sigma^2$** is

$$
\boxed{\hat\sigma^2 = \frac{\mathrm{SSR}}{n-k} = \frac{\hat\varepsilon'\hat\varepsilon}{n-k},}
$$

and $\mathbb{E}[\hat\sigma^2\mid X] = \sigma^2$.

### 5.2 Estimated covariance and standard errors

Replacing $\sigma^2$ with $\hat\sigma^2$ gives the standard estimated covariance matrix of $\hat\beta$:

$$
\widehat{\mathrm{Var}}(\hat\beta\mid X) = \hat\sigma^2 (X'X)^{-1}.
$$

The estimated standard errors (componentwise) are:

$$
\widehat{\mathrm{se}}(\hat\beta_j) = \sqrt{\hat\sigma^2 \big[(X'X)^{-1}\big]_{jj}}.
$$

## 6. Consistency

From the decomposition

$$
\hat\beta - \beta = (X'X)^{-1}X'\varepsilon
= \left(\tfrac{1}{n}X'X\right)^{-1}\left(\tfrac{1}{n}X'\varepsilon\right).
$$

Under the assumptions:

- $\tfrac{1}{n}X'X \xrightarrow{p} Q$ with $Q$ positive definite,
- $\tfrac{1}{n}X'\varepsilon \xrightarrow{p} 0$ (follows from the law of large numbers under exogeneity and finite second moments),

we apply Slutsky's theorem: the inverse term converges in probability to $Q^{-1}$ and the second factor goes to $0$, hence

$$
\boxed{\hat\beta \xrightarrow{p} \beta.}
$$

Thus $\hat\beta$ is consistent.

*Remark on $\tfrac{1}{n}X'\varepsilon \xrightarrow{p} 0$: if rows $x_i'$ of $X$ and $\varepsilon_i$ satisfy $\mathbb{E}[x_i\varepsilon_i]=0$ and have uniformly bounded second moments, then by the weak law of large numbers the sample average $\frac{1}{n}\sum_i x_i\varepsilon_i$ tends to zero in probability.*

## 7. Asymptotic normality

Start from

$$
\sqrt{n}(\hat\beta-\beta) = \left(\frac{X'X}{n}\right)^{-1}\frac{X'\varepsilon}{\sqrt{n}}.
$$

Assume Lindeberg–Feller (or Liapounov) conditions so that a multivariate CLT applies to the sum $\sum_i x_i\varepsilon_i$. Concretely, if $\{(x_i,\varepsilon_i)\}_{i=1}^n$ are independent (or weakly dependent under appropriate mixing conditions), mean zero with finite second moments, then

$$
\frac{1}{\sqrt{n}}X'\varepsilon = \frac{1}{\sqrt{n}}\sum_{i=1}^n x_i\varepsilon_i \xrightarrow{d} \mathcal{N}(0,\sigma^2 Q),
$$

where $Q=\lim_{n\to\infty}\frac{1}{n}X'X$. By Slutsky's theorem, and since $\frac{1}{n}X'X \xrightarrow{p} Q$, we obtain

$$
\boxed{\sqrt{n}(\hat\beta-\beta)\xrightarrow{d}\mathcal{N}(0,\sigma^2 Q^{-1}).}
$$

Equivalently, for large $n$, approximately

$$
\hat\beta \approx \mathcal{N}\!\left(\beta,\;\frac{\sigma^2}{n}Q^{-1}\right).
$$

## 8. Finite-sample remark (Gauss–Markov)

Under the Gauss–Markov assumptions (in particular conditional homoskedasticity and exogeneity) and treating $X$ as non-random or conditioning on $X$, the OLS estimator is the Best Linear Unbiased Estimator (BLUE): among all linear unbiased estimators $\tilde\beta = A y$ with deterministic $A$ such that $\mathbb{E}[\tilde\beta\mid X]=\beta$, $\hat\beta$ has minimum variance. The classical proof proceeds by writing any such $\tilde\beta$ as $\hat\beta + C\varepsilon$ for some matrix $C$ and showing $\mathrm{Var}(\tilde\beta\mid X)-\mathrm{Var}(\hat\beta\mid X)=\sigma^2 CC'$ is positive semidefinite.
