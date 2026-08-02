from pathlib import Path
import pandas as pd
from src.data import load_demo
from src.indices import development_index,sensitivity_analysis,cluster_regions,gini,theil
ROOT=Path(__file__).resolve().parents[1]

def test_demo_has_16_regions_and_official_total():
    df=load_demo(ROOT).frame
    assert len(df)==16
    assert int(df.population_2021.sum())==30_832_019

def test_growth_is_positive():
    df=load_demo(ROOT).frame
    assert (df.growth_2010_2021_percent>0).all()

def test_index_range_and_unique_regions():
    df=load_demo(ROOT).frame; idx=development_index(df)
    assert idx.development_score.between(0,100).all()
    assert idx.region.nunique()==16

def test_weights_change_index():
    df=load_demo(ROOT).frame
    a=development_index(df,{"Education":3,"Economic opportunity":0.2,"Basic services":0.2,"Digital inclusion":0.2,"Health & social protection":0.2})
    b=development_index(df,{"Education":0.2,"Economic opportunity":3,"Basic services":0.2,"Digital inclusion":0.2,"Health & social protection":0.2})
    assert not a.set_index('region').development_score.equals(b.set_index('region').development_score)

def test_sensitivity_rows():
    df=load_demo(ROOT).frame;s=sensitivity_analysis(df,{d:1 for d in ["Education","Economic opportunity","Basic services","Digital inclusion","Health & social protection"]},100)
    assert len(s)==16 and s.mean_rank.between(1,16).all()

def test_clustering_output():
    df=load_demo(ROOT).frame;c,l,m=cluster_regions(df,4)
    assert len(c)==16 and c.cluster.nunique()==4 and len(l)>=3
    assert -1<=m['silhouette']<=1

def test_inequality_metrics():
    assert 0<=gini([1,2,3,4])<=1
    assert theil([1,2,3,4])>=0
