# The Agents Playground
- - -
Hello. You've stumbled onto my little hobby project. The codebase is a 2D game 
engine of sorts. It's not designed to build games with but rather a rapid prototyping
environment for experimenting with autonomous agents. This is something I'm 
building for fun and isn't intended for general use. That said, it's open source
and if you find a use for it feel free to use the code. If you're interested in
this sort of thing, I'm journaling my work on [my blog](https://samuelholloway.com/tags/agent-playground/).

## Project Status and Roadmap
_Status_: Initial Development 
The codebase is useable but is currently in the initial development phases as 
the core features are being flushed out. The intention is to eventual build an 
installable Python Wheel and have versioned releases. At the moment, since I'm 
just working on this for me, the application is run using the project's [Makefile](./Makefile).

A [GitIssues project](https://github.com/sholloway/agents-playground/projects/1) 
is used for tracking the ongoing work. A features file is used to summarize the 
completed features.

## Getting Started
The project is bootstrapped using the [Nix package manager](https://nixos.org/).
Nix is responsible for installing Python 3.11 and Pip. Once that is bootstrapped 
then the project's Makefile is used to create a virtual environment. In the virtual
environment, [Poetry](https://python-poetry.org/) is installed. Poetry is then 
used to install the various 3rd party dependencies and is used by the Makefile 
for all application life cycle activities.

Note: You don't have to use Nix to work with the code base. If you have Python
3.11 and Pip installed already you can just use the Makefile to do the additional 
setup steps.

### Project Setup
1. Install the [Nix Package Manager](https://nixos.org/download.html) (optional)

2. Clone the repo.
```shell
git clone git@github.com:sholloway/agents-playground.git
```

3. If using Nix, create a Nix shell. This will install Python and Pip. 
Note: If you're on a Mac you'll need to install the [Xcode Command Line Tools](https://mac.install.guide/commandlinetools/index.html) first.
```shell
make nix
```

4. Create the Python Virtual Environment for the Project.
Note: If you're using Nix, on some M1 based Macs I've run into an issue with installing
one of the dev dependencies due to Nix getting confused about where MacOS puts 
the C libraries. My work around is to run `make setup` and then exit out of the Nix
shell, activate the virtual env `source .venv/bin/activate`, and run 
`pip install -r requirements.txt` a second time.
```shell
make setup
```

5. Now you should have Poetry bootstrapped into the virtual environment. 
Use poetry to install the project dependencies.
```shell
make init
```

### Running the Application
The application can be run in production mode or dev mode.
```shell
# Production Mode (faster)
make run

# Development Mode (enables logging and asserts but runs slower)
make dev
```

### Development Tools
There are additional Make targets to help simplify development activities. 
They are listed in the table below. They're all run with the pattern `make <target name>`.

| Target | Description                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------------- |
| test   | Run the unit tests.                                                                                           |
| check  | Perform static type checking on the project.                                                                  |
| debug  | Launches pudb debugger in the terminal if there are any breakpoints. You can also use the VSCode debugger. ;) |
| flame  | Launch's py-spy profiler and generates an interactive flame graph.                                            |
| top    | Display a running list of the top most expensive functions while the app is running.                          |
| shell  | Launches an instance of the bpython shell with the application loaded.                                        |
| cov | Calculates code coverage. |
| doc | Generates the code documentation. |
| profile_function | Use line-profiler to profile a function. To profile a function, it must be annotated with the @profile decorator. |
| size | Run cloc to measure the size of the project. | 

## Working with the Codebase

## Exploration

What I'm interested in trying in this code base.
Expand my maze's A\* agent to possible have:

- Traits
- Characteristics
- A personal history that influence decision making (probability weights).
- NPCs and machines that do work.
  - Complex tasks
    - Example:
      1.  Assign workers to harvest raw materials: iron ore, coal, trees, water
      2.  Assign workers to transport raw materials to a processing machine. Workers carry their amount to a place and leave it.
      3.  A machine converts raw material into something else. Iron Ore -> Iron Bars
    - A machine as available inputs, outputs. Throughput rate.
- Configuration based AI or other things could possibly be created/represented
  using a Node based UI (boxes and lines).
- Support loading "scenes" to enable rapidly trying out AI in specific scenarios.

Possible Approaches

- HTN
- Hierarchical state machines

## Goals

This code repo is going to accomplish:

- A desktop app that generates a multi-screen sized environment that agents can
  navigate in (i.e. path finding).
- Algorithms like path finding, decision making, etc will be frame budget based.
  Each systems shall have a budget for how much time they can take. Profiling
  needs to be a consideration from the start. Need to identify the profiling
  tooling early. Add python debugging to this.
- This project should be a workshop app that enables trying out planning
  algorithms, new state machine designs and what not.
- Concurrency needs to be an early consideration.
- Transportation of things is interesting. Trains, Mine Cars, teleporter, etc...

## Use Cases/Scenes

- A\* Path finding of a single agent.
- A\* Path finding of 1000 agents.
- Passing events from agents by proximity?
- JPS+ evaluation

### To Run The App

```bash
make run
```

### Perform Static Type Checking

```bash
make check
```

## Additional Documentation

- [Dependencies](./docs/dependencies.md)
- [Debugging](./docs/debugging.md)
- [Decision Log](./docs/decisions_log.md)
- [Profiling](./docs/profiling.md)
- [Testing](./docs/testing.md)
