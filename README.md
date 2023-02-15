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
The codebase is useable but is currently in the initial development phase as 
the core features are currently being flushed out. The intention is to eventual build an 
installable Python Wheel and have versioned releases. At the moment, since I'm 
just working on this for me, the application is run using the project's [Makefile](./Makefile).

[GitHub Issues and Projects](https://github.com/sholloway/agents-playground/projects/1) 
are used for tracking the ongoing work. A [features file](./docs/features.txt) is used to summarize the 
usable features.

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

### Performance Monitoring
The application has real-time hardware monitoring baked in. This is accessible 
through the UI by clicking the _utility_ button on the toolbar while a simulation
is loaded.

A limitation on MacOS prevents some of the hardware sensors from being accessed 
unless run as the root user. To do this launch the app as root.

```shell
sudo make run
```

## Additional Documentation

- [Creating new Simulations](./docs/creating_sims.md)
- [Dependencies](./docs/dependencies.md)
- [Debugging with Pubd](./docs/debugging.md)
- [Decision Log](./docs/decisions_log.md)
- [Profiling](./docs/profiling.md)
- [Testing](./docs/testing.md)
