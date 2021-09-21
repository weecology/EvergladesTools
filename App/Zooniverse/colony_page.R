colony_page<-function(selected_boxes){  
  renderUI({
    fluidPage(
      titlePanel("Visit the colonies!"),
      selectizeInput("colony_selected_image", "Site", choices = NULL),
      leafletOutput("colony_map",height=1000)
    )})
}