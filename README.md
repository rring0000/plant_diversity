# Plant Diversity
## Overview
The Plant Diversity project utilises Cai et al. plant diversity dataset, generated using machine learning techniques, to map out diversity of plants on WWF ecoregions. The main goal is to identify ecoregional plant diversity hotspots. 
## Project goal
The main goal of the project is to visualize predicted plant species richness across WWF ecoregions and identify areas with high plant diversity
## Data + Sources 
### Plant species richness
Plant species richness data were obtained from Cai et al. (2022). The dataset provides global predictions of plant species richness on a 7774 km² hexagonal grid

Source: https://nph.onlinelibrary.wiley.com/doi/full/10.1111/nph.18533

### WWF ecoregions 

WWF terrestrial ecoregions dataset depicts 825 terrestrial ecoregions on the globe. Ecoregions are relatively large units of land containing distinct assemblages of natural communities and species, with boundaries that approximate the original extent of natural communities prior to major land-use change

Source: https://www.arcgis.com/home/item.html?id=1c898239f8234ace82bf41302811916f#overview

## how to run: 
run either src/visualisation/plant_diversity_map.py or src/visualisation/plant_diversity_chao_map.py for map 

## the chao1 thing
I tried to run the cai et al datset through chao1 to filter out the possible sampling bias. I yet don't know, with what degree of success. 