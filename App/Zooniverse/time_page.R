time_page<-function(selected_boxes){

  renderUI({
    fluidPage(
      titlePanel("Select a site and label to see changes over time."),
      selectizeInput("timeseries_site", "Site", choices = NULL, selected = site_list, multiple = TRUE),
      selectizeInput("timeseries_species", "Species", choices = NULL, multiple = TRUE),
      selectizeInput("timeseries_behavior", "Behavior", choices = NULL, multiple = TRUE),
      plotOutput("site_phenology_plot",height=700)
    )})
}