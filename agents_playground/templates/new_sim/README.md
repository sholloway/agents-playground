# Agent Playground Project
- - -
This is a new project for working with the Agent Playground.

## Getting Started
The project is setup following the same pattern as the Agent Playground project.

### Project Setup
1. Install [Devbox](https://www.jetify.com/devbox/docs/quickstart/) (optional)

2. If using Devbox, create a Devbox shell. This will install Python and Pip. 
Note: If you're on a Mac you'll need to install the [Xcode Command Line Tools](https://mac.install.guide/commandlinetools/index.html) first.
```shell
make env
```

3. Create the Python Virtual Environment for the Project.
```shell
make setup
```

4. Now you should have Poetry bootstrapped into the virtual environment. 
Use poetry to install the project dependencies.
```shell
make init
```

5. Run the project's tests.
```shell
make test
```

### Running the Project
To run the project, just launch the _Agent's Playgound_ and use the UI to open the 
project. The UI steps are _Simulation_ -> _Open_
