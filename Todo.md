
Next Steps
- [X] Clean up SceneBuilder (324 lines, 260 code)
  - [X] Replace the parse methods (e.g. parse_cell_size) with the composite pattern like the ProjectLoader.
  - [X] Break the scene_builder module into multiple files. 
- [D] Change the SceneBuilder to only use the default_agent module.
- [D] Change the three demos to implement Agent extensions if needed.
- [ ] Remove Agent and its related classes from the project.
- [] Rename AgentLike to Agent. Consider renaming the other spec classes.
- [D] Look at using NamedAgentState in the agent_builder. I've wired this up, but having an instance 
      for each agent by be the wrong thing todo. 
- [ ] Update AgentBuilder to construct a MapAgentActionSelector from the TOML file
      if present.