from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

DOMAIN_INDICATORS={
    "Education":{"literacy_percent":1,"school_attendance_percent":1},
    "Economic opportunity":{"employed_share_percent":1,"unemployment_rate_percent":-1,"multidimensional_poverty_percent":-1},
    "Basic services":{"improved_water_percent":1,"basic_sanitation_percent":1,"electricity_access_percent":1},
    "Digital inclusion":{"internet_use_percent":1},
    "Health & social protection":{"health_insurance_percent":1},
}
ALL_INDICATORS=[k for group in DOMAIN_INDICATORS.values() for k in group]
DIRECTIONS={k:v for group in DOMAIN_INDICATORS.values() for k,v in group.items()}


def available_indicators(frame: pd.DataFrame):
    return [c for c in ALL_INDICATORS if c in frame.columns and frame[c].notna().sum()>=3]


def indicator_matrix(frame: pd.DataFrame):
    cols=available_indicators(frame)
    if len(cols)<3: raise ValueError("At least three development indicators are needed.")
    x=frame[cols].astype(float).copy()
    x=x.fillna(x.median())
    z=pd.DataFrame(StandardScaler().fit_transform(x),columns=cols,index=frame.index)
    for c in cols: z[c]*=DIRECTIONS.get(c,1)
    return z,cols


def development_index(frame: pd.DataFrame, domain_weights: dict[str,float]|None=None):
    z,cols=indicator_matrix(frame)
    domain_weights=domain_weights or {d:1 for d in DOMAIN_INDICATORS}
    total=sum(max(float(v),0) for v in domain_weights.values()) or 1
    domain_scores={}
    for domain,mapping in DOMAIN_INDICATORS.items():
        active=[c for c in mapping if c in cols]
        if active: domain_scores[domain]=z[active].mean(axis=1)
    raw=sum(domain_scores[d]*(max(float(domain_weights.get(d,0)),0)/total) for d in domain_scores)
    span=float(raw.max()-raw.min())
    score=pd.Series(50.0,index=raw.index) if span==0 else 100*(raw-raw.min())/span
    out=frame[["region"]].copy()
    out["development_score"]=score
    out["rank"]=out["development_score"].rank(ascending=False,method="min").astype(int)
    for domain,s in domain_scores.items(): out[domain.lower().replace(" ","_").replace("&","and")]=s
    return out.sort_values("rank").reset_index(drop=True)


def sensitivity_analysis(frame: pd.DataFrame, base_weights: dict[str,float], n_iter=500, seed=42):
    rng=np.random.default_rng(seed); domains=list(DOMAIN_INDICATORS)
    z,cols=indicator_matrix(frame)
    domain_vectors=[]
    for domain,mapping in DOMAIN_INDICATORS.items():
        active=[c for c in mapping if c in cols]
        domain_vectors.append(z[active].mean(axis=1).to_numpy() if active else np.zeros(len(frame)))
    matrix=np.column_stack(domain_vectors)
    base=np.array([max(float(base_weights.get(d,0)),0.001) for d in domains])
    alpha=base/base.sum()*25
    weight_draws=rng.dirichlet(alpha,size=n_iter)
    raw_scores=matrix @ weight_draws.T
    ranks=np.empty_like(raw_scores,dtype=int)
    for j in range(raw_scores.shape[1]):
        order=np.argsort(-raw_scores[:,j],kind="mergesort")
        col=np.empty(len(frame),dtype=int); col[order]=np.arange(1,len(frame)+1); ranks[:,j]=col
    summary=pd.DataFrame({
        "region":frame["region"].to_numpy(),
        "mean_rank":ranks.mean(axis=1),"rank_std":ranks.std(axis=1,ddof=1),
        "best_rank":ranks.min(axis=1),"worst_rank":ranks.max(axis=1),
        "top_quartile_probability":(ranks<=max(1,len(frame)//4)).mean(axis=1)
    })
    return summary.sort_values("mean_rank").reset_index(drop=True)


def cluster_regions(frame: pd.DataFrame, n_clusters=4, seed=42):
    z,cols=indicator_matrix(frame)
    n_clusters=max(2,min(int(n_clusters),len(frame)-1))
    pca=PCA(n_components=2,random_state=seed); pcs=pca.fit_transform(z)
    model=KMeans(n_clusters=n_clusters,random_state=seed,n_init=20); labels=model.fit_predict(z)
    silhouette=float(silhouette_score(z,labels)) if len(set(labels))>1 else float("nan")
    out=frame[["region"]].copy(); out["PC1"]=pcs[:,0]; out["PC2"]=pcs[:,1]; out["cluster"]=[f"Cluster {x+1}" for x in labels]
    loadings=pd.DataFrame(pca.components_.T,index=cols,columns=["PC1_loading","PC2_loading"]).reset_index(names="indicator")
    return out,loadings,{"explained_variance":pca.explained_variance_ratio_.tolist(),"silhouette":silhouette}


def gini(values):
    x=np.asarray(values,dtype=float); x=x[np.isfinite(x)]
    if len(x)==0:return float("nan")
    x=x-x.min() if x.min()<0 else x
    if np.allclose(x.sum(),0):return 0.0
    x=np.sort(x); n=len(x)
    return float((2*np.sum((np.arange(1,n+1))*x)/(n*x.sum()))-(n+1)/n)


def theil(values):
    x=np.asarray(values,dtype=float); x=x[np.isfinite(x)&(x>=0)]
    if len(x)==0 or x.mean()==0:return 0.0
    ratio=x/x.mean(); nz=ratio>0
    return float(np.mean(ratio[nz]*np.log(ratio[nz])))
