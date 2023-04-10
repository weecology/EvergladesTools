library(sf)
library(dplyr)
source('functions.R')

# Set thresholds
min_confidence <- 0.3

#Load data
raw_data <- load_classifications()
selected_boxes <- filter_annotations(raw_data)
colonies <- st_read(
  "data/colonies.csv",
  options = c("X_POSSIBLE_NAMES=longitude","Y_POSSIBLE_NAMES=latitude"))
samples <- st_read(
  "./experiments/field_nest_sample_locations.csv",
  options = c("X_POSSIBLE_NAMES=long", "Y_POSSIBLE_NAMES=lat"),
  crs = 4326)

#Predictions
unzip("data/PredictedBirds.zip", exdir = "data")
df <- st_read("data/PredictedBirds.shp")
df$actualevent = df$event
df <- df %>%
  filter(actualevent == "primary") %>%
  mutate(year = Year, site = Site, date = Date)
df$event <- as.Date(df$date,"%m_%d_%Y")
df$tileset_id <- construct_id(df$site, df$event)
df <- df %>% filter(score > min_confidence)
df <- st_transform(df, 4326)
df <- st_centroid(df)

#Nest predictions
unzip("data/nest_detections_processed.zip", exdir = "data")
nestdf <- st_read("data/nest_detections_processed.shp")
nestdf$first_obs <- as.Date(nestdf$first_obs,"%m_%d_%Y")
nestdf$last_obs <- as.Date(nestdf$last_obs,"%m_%d_%Y")
nestdf <- st_centroid(nestdf)
nestdf <- st_transform(nestdf,4326)
