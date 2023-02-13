# Installs my preferred tooling for working on this project.
# Neovim and Plugins

# TODO
  # Python and Dependencies
  # Update to Python 3.11
  # Get rid of Poetry and use venv.

# To run:
# make nix

{pkgs ? import <nixpkgs> {}}:

pkgs.mkShell {
  name = "dev";
  buildInputs = [ 
    pkgs.git
    pkgs.gnumake
    pkgs.cloc
    (pkgs.python311.withPackages (ps:
      with ps; [
        pip
      ])) 
  ];
}

