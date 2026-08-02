# Methodology

## Regional development index
1. Select available development indicators.
2. Median-impute missing regional values.
3. Standardize each indicator using the cross-regional mean and standard deviation.
4. Reverse indicators where lower values are preferable: unemployment and multidimensional poverty.
5. Average standardized indicators within five domains.
6. Combine domains using user-selected non-negative weights.
7. Rescale the comparative result to 0–100.

The score is relative to the included regions and indicators. It is not an official index.

## Sensitivity analysis
Weight vectors are sampled from a Dirichlet distribution centred on the selected weights. The application reports mean rank, rank volatility, best/worst rank and the probability of appearing in the top quartile.

## PCA and clustering
Direction-adjusted standardized indicators are projected onto two principal components. K-means creates descriptive groups; silhouette score measures separation. Clusters are not a development hierarchy.

## Inequality
The dashboard reports Gini and Theil measures for selected regional distributions. Regional inequality statistics should be interpreted alongside population size and indicator definitions.
