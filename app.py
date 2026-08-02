from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import load_demo,read_uploaded_csv,INDICATOR_COLUMNS
from src.indices import DOMAIN_INDICATORS,development_index,sensitivity_analysis,cluster_regions,gini,theil
from src.reporting import regional_report_html

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="Ghana Regional Development Explorer",page_icon="🇬🇭",layout="wide",initial_sidebar_state="expanded")
st.markdown('''<style>
:root{--forest:#0b5e45;--ink:#17231c;--gold:#d5a52e;--cream:#f7f3e8;--mint:#e8f5ef}
.stApp{background:linear-gradient(180deg,#fbfcf8 0%,#edf5ef 100%);color:var(--ink)}
[data-testid="stSidebar"]{background:#102d24}.hero{padding:2.3rem 2.5rem;border-radius:24px;background:linear-gradient(120deg,#082d24,#0b6b50 62%,#c69b2d);color:white;box-shadow:0 18px 55px rgba(11,94,69,.18);margin-bottom:1rem}.hero h1{font-size:3rem;line-height:1.03;margin:.35rem 0 .8rem}.eyebrow{letter-spacing:.17em;text-transform:uppercase;font-size:.78rem;opacity:.82}.hero p{max-width:900px;font-size:1.06rem;opacity:.93}.badge{display:inline-block;padding:.34rem .68rem;border-radius:999px;background:rgba(255,255,255,.15);margin:.35rem .35rem 0 0;font-size:.8rem}.note{padding:1rem 1.2rem;border-left:4px solid #d5a52e;background:#fff9e8;border-radius:10px;margin:.7rem 0}.panel{background:white;border:1px solid #dce8df;padding:1rem 1.1rem;border-radius:16px}
</style>''',unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Explorer controls")
    source=st.radio("Data source",["Bundled demonstration","Upload regional CSV"])
    upload=st.file_uploader("Regional indicators CSV",type=["csv"],disabled=source!="Upload regional CSV")
    st.download_button("Download upload template",(ROOT/"data"/"schemas"/"regional_upload_template.csv").read_bytes(),"regional_upload_template.csv","text/csv")
    st.divider(); st.markdown("### Composite-index weights")
    weights={d:st.slider(d,0.0,3.0,1.0,0.1) for d in DOMAIN_INDICATORS}
    st.caption("Weights change the comparative index only; no weighting scheme is uniquely correct.")

if source=="Upload regional CSV" and upload is not None:
    try:data=read_uploaded_csv(upload)
    except Exception as exc:st.error(str(exc));st.stop()
else:data=load_demo(ROOT)
df=data.frame

st.markdown('''<div class="hero"><div class="eyebrow">Census analytics · regional inequality · public data</div><h1>Ghana Regional Development & Census Explorer</h1><p>Explore population change, urbanisation, education, employment, housing and essential-service access across Ghana's 16 regions—then examine how transparent methodological choices alter composite development rankings.</p><span class="badge">2021 PHC context</span><span class="badge">Regional profiles</span><span class="badge">PCA & clustering</span><span class="badge">Sensitivity analysis</span></div>''',unsafe_allow_html=True)
if data.demonstration:
    st.markdown('<div class="note"><b>Data boundary:</b> the population baseline reproduces Ghana’s 2010/2021 regional census totals. The remaining development indicators are calibrated demonstration values designed to exercise the analytical product. Upload official GSS StatsBank extracts before using results for policy or research claims.</div>',unsafe_allow_html=True)

idx=development_index(df,weights); merged=df.merge(idx,on="region",how="left")
country_pop=int(df.population_2021.sum()); growth=(df.population_2021.sum()/df.population_2010.sum()-1)*100
c1,c2,c3,c4,c5=st.columns(5)
c1.metric("2021 population",f"{country_pop:,}");c2.metric("Regions",len(df));c3.metric("Growth since 2010",f"{growth:.1f}%");c4.metric("Urban share",f"{np.average(df.urban_share_percent,weights=df.population_2021):.1f}%" if 'urban_share_percent' in df else '—');c5.metric("Most populous",df.loc[df.population_2021.idxmax(),'region'])

tabs=st.tabs(["National overview","Regional profiles","Development index","Clusters & inequality","Methodology & export"])
with tabs[0]:
    metric_options={"Population":"population_2021","Population density":"density_2021","2010–2021 growth":"growth_2010_2021_percent","Urban share":"urban_share_percent","Literacy":"literacy_percent","Electricity access":"electricity_access_percent","Multidimensional poverty":"multidimensional_poverty_percent","Development score":"development_score"}
    choice=st.selectbox("Map indicator",list(metric_options));metric=metric_options[choice]
    fig=px.scatter_map(merged,lat="latitude",lon="longitude",size="population_2021",color=metric,hover_name="region",hover_data={"capital":True,"population_2021":':,',metric:':.1f',"latitude":False,"longitude":False},zoom=5.4,center={"lat":7.9,"lon":-1.1},height=520,map_style="open-street-map",title=f"Regional atlas · {choice}")
    st.plotly_chart(fig,use_container_width=True)
    a,b=st.columns([1.3,1])
    with a:
        rank=merged.sort_values(metric,ascending=metric=="multidimensional_poverty_percent")
        bar=px.bar(rank,x=metric,y="region",orientation="h",title=f"Regional comparison · {choice}")
        bar.update_layout(height=520,yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(bar,use_container_width=True)
    with b:
        st.markdown("### Census story")
        st.write("Greater Accra and Ashanti dominate population size, while density and service access reveal a different geography. The explorer keeps totals, rates and composite scores separate so that large populations are not automatically interpreted as better outcomes.")
        display_cols=["region","population_2021","growth_2010_2021_percent","density_2021","development_score","rank"]
        st.dataframe(merged[display_cols].sort_values("rank"),hide_index=True,use_container_width=True)

with tabs[1]:
    region=st.selectbox("Select a region",sorted(df.region.unique()))
    compare=st.multiselect("Compare with",[r for r in sorted(df.region.unique()) if r!=region],default=["Ghana average"] if False else [])
    row=merged.loc[merged.region==region].iloc[0]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Population",f"{int(row.population_2021):,}");c2.metric("Growth",f"{row.growth_2010_2021_percent:.1f}%");c3.metric("Density",f"{row.density_2021:,.1f}/km²");c4.metric("Development rank",f"{int(row['rank'])} of {len(df)}")
    radar_cols=[c for c in ["literacy_percent","employed_share_percent","improved_water_percent","basic_sanitation_percent","electricity_access_percent","internet_use_percent","health_insurance_percent"] if c in df]
    labels=[c.replace('_percent','').replace('_',' ').title() for c in radar_cols]
    fig=go.Figure(); vals=[row[c] for c in radar_cols]
    fig.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=labels+[labels[0]],fill='toself',name=region))
    national=[np.average(df[c],weights=df.population_2021) for c in radar_cols]
    fig.add_trace(go.Scatterpolar(r=national+[national[0]],theta=labels+[labels[0]],name="Population-weighted national average"))
    for comp in compare[:3]:
        cr=merged.loc[merged.region==comp].iloc[0];v=[cr[c] for c in radar_cols]
        fig.add_trace(go.Scatterpolar(r=v+[v[0]],theta=labels+[labels[0]],name=comp))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),height=520,title="Regional capability profile")
    st.plotly_chart(fig,use_container_width=True)
    report=regional_report_html(row,idx.loc[idx.region==region].iloc[0],data.source_label)
    st.download_button("Download regional profile (HTML)",report,f"{region.lower().replace(' ','_')}_regional_profile.html","text/html")

with tabs[2]:
    st.markdown("### Transparent composite development index")
    st.write("Indicators are standardized across regions, reversed where lower values are preferable, averaged within domains, and combined using the sidebar weights. Scores are rescaled from 0 to 100 for communication; ranks are relative to the current dataset.")
    chart=px.bar(idx.sort_values("development_score"),x="development_score",y="region",orientation="h",color="development_score",title="Composite development score under current weights")
    chart.update_layout(height=570,coloraxis_showscale=False);st.plotly_chart(chart,use_container_width=True)
    n=st.slider("Sensitivity simulations",100,1500,500,100)
    sens=sensitivity_analysis(df,weights,n_iter=n)
    a,b=st.columns([1.3,1])
    with a:st.dataframe(sens,hide_index=True,use_container_width=True)
    with b:
        fig=px.scatter(sens,x="mean_rank",y="rank_std",size="top_quartile_probability",hover_name="region",title="Ranking stability under plausible weight variation")
        fig.update_xaxes(autorange="reversed");st.plotly_chart(fig,use_container_width=True)
    st.download_button("Download index and ranks",idx.to_csv(index=False),"ghana_regional_development_index.csv","text/csv")

with tabs[3]:
    k=st.slider("Number of regional clusters",2,6,4)
    clusters,loadings,meta=cluster_regions(df,k)
    cluster_df=merged.merge(clusters,on="region")
    c1,c2,c3=st.columns(3);c1.metric("Silhouette score",f"{meta['silhouette']:.3f}");c2.metric("PC1 explained variance",f"{meta['explained_variance'][0]*100:.1f}%");c3.metric("PC2 explained variance",f"{meta['explained_variance'][1]*100:.1f}%")
    fig=px.scatter(cluster_df,x="PC1",y="PC2",color="cluster",size="population_2021",text="region",hover_data=["development_score","urban_share_percent","multidimensional_poverty_percent"],title="Regional development profiles in PCA space")
    fig.update_traces(textposition="top center");fig.update_layout(height=570);st.plotly_chart(fig,use_container_width=True)
    a,b=st.columns(2)
    with a:
        st.markdown("### Inequality diagnostics")
        measures=[]
        for c,label in [("population_2021","Population"),("density_2021","Density"),("development_score","Development score"),("internet_use_percent","Internet use")]:
            if c in merged:measures.append({"measure":label,"gini":gini(merged[c]),"theil":theil(merged[c])})
        st.dataframe(pd.DataFrame(measures),hide_index=True,use_container_width=True)
        q=px.scatter(merged,x="urban_share_percent",y="multidimensional_poverty_percent",size="population_2021",color="development_score",hover_name="region",title="Urbanisation and multidimensional poverty")
        st.plotly_chart(q,use_container_width=True)
    with b:
        st.markdown("### PCA loadings")
        st.dataframe(loadings.sort_values("PC1_loading",key=abs,ascending=False),hide_index=True,use_container_width=True)
        st.caption("Clusters describe similarity, not a hierarchy. Different indicator choices or standardization methods can produce different groupings.")

with tabs[4]:
    st.markdown("### Data provenance and responsible use")
    st.write("The project is designed around Ghana Statistical Service 2021 Population and Housing Census dissemination products and StatsBank categories. The bundled file is intentionally hybrid: exact regional population baselines are paired with calibrated demonstration indicators so the complete application can run without restricted or manually downloaded extracts.")
    st.warning("Do not publish the bundled education, employment, service, health or poverty values as official regional statistics. Replace them with validated GSS exports for evidential analysis.")
    st.markdown("### Index limitations")
    st.write("Composite indices compress multidimensional outcomes and necessarily embed normative choices. They can support comparison and exploration, but should not be treated as absolute truth, a funding formula or a causal explanation.")
    export={"source":data.source_label,"demonstration_data":data.demonstration,"regions":len(df),"population_2021":country_pop,"weights":weights,"index":idx.to_dict(orient="records")}
    st.download_button("Download analysis summary (JSON)",json.dumps(export,indent=2),"ghana_regional_analysis_summary.json","application/json")
    st.download_button("Download dataset used",df.to_csv(index=False),"ghana_regional_dataset_used.csv","text/csv")
    st.markdown("### Recommended official replacement sources")
    st.write("GSS StatsBank PHC 2021 tables, the 2021 PHC General Report Volumes 3A–3N, and the GSS Microdata Catalog documentation. Source links and field mapping guidance are included in the repository documentation.")
