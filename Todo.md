
Next Steps
- [ ] Change the SceneBuilder to only use the default_agent module.
- [ ] Clean up SceneBuilder (324 lines, 260 code)
  - [ ] Replace the parse methods (e.g. parse_cell_size) with the composite pattern like the ProjectLoader.
  - [ ] Break the scene_builder module into multiple files. 
  - [ ] Clean up the hasattr checks with the funcs module.
  - [ ] Replace the for loops with list expansions.
- [ ] Change the three demos to implement Agent extensions if needed.
- [ ] Remove Agent and its related classes from the project.
- [ ] Rename AgentLike to Agent. Consider renaming the other spec classes.