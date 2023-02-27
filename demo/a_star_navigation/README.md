# A Star Navigation
- - -
This is an example project that demonstrates A* path finding using a pre-determined
navigation mesh.

## Getting Started
The project is setup following the same pattern as the Agent Playground project.

### Project Setup
1. Install the [Nix Package Manager](https://nixos.org/download.html) (optional)

2. If using Nix, create a Nix shell. This will install Python and Pip. 
Note: If you're on a Mac you'll need to install the [Xcode Command Line Tools](https://mac.install.guide/commandlinetools/index.html) first.
```shell
make nix
```

3. Create the Python Virtual Environment for the Project.
```shell
make setup
```

4. Manually activate the virtual environment.
```shell
source .venv/bin/activate
```

5. Now you should have Poetry bootstrapped into the virtual environment. 
Use poetry to install the project dependencies.
```shell
make init
```

6. Run the project's tests.
```shell
make test
```

### Running the Demo
To run the demo, just launch the _Agent's Playgound_ and use the UI to open the 
project. The UI steps are _Simulation_ -> _Open_
