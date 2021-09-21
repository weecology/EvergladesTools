landing_page<-function(selected_boxes){
  renderUI({
    fluidPage(
      sidebarPanel(leafletOutput("map",height=900)),
      mainPanel(h2("Zooniverse Summary"),
                p(textOutput("summary")),
                plotOutput("zooniverse_anotation"),
                
                plotOutput("totals_plot",height=400),
                h2("Select Sites"),
                selectizeInput("landing_site", "Site", choices = NULL, multiple = TRUE),
                plotOutput("site_totals_plot",height=400),
                
                h2("View Annotations"),
                selectizeInput("selected_image", "Site", choices = NULL),
                leafletOutput("colony_map",height=1000)
      )
    )})
}