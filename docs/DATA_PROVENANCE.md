# Data provenance

## Population baseline
The bundled regional population, 2010 comparison, area and density fields reproduce the Ghana 2021 census regional baseline published in public census summaries. The national 2021 total is 30,832,019 across 16 regions.

Primary context sources:
- Ghana Statistical Service 2021 PHC General Report and press releases
- GSS StatsBank PHC 2021 aggregated data platform
- GSS Microdata Catalog metadata, reference `GHA-GSS-2021PHC-2021-v1.0`

The exact tabular regional baseline was transcribed from an open reproduction that cites GSS 2021 PHC and GADM 4.1. Verify against GSS before formal publication.

## Demonstration indicators
The bundled education, employment, water, sanitation, electricity, internet, health-insurance and multidimensional-poverty indicators are deterministic calibrated demonstration values. They are not official regional estimates. They exist so that the entire analytical product can launch without requiring account-gated microdata or manual StatsBank exports.

## Replacing the demonstration fields
Download regional tables from GSS StatsBank, reshape to one row per region, rename fields to the upload contract in `data/schemas/regional_upload_template.csv`, and upload through the sidebar.
