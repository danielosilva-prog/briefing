// Test template for custom charts report
#let data = json("data.json")

= Custom Charts Test Report

#for (name, svg) in data.charts {
  [== #name]
  // Chart would be rendered here
}
