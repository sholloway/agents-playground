# Installs my preferred tooling for working on this project.

# We need to make sure that the correct version of python is installed.
# https://github.com/NixOS/nixpkgs/issues/9682
# https://lazamar.co.uk/nix-versions

{pkgs ? import <nixpkgs> {}}:

let
  pkgs = import (builtins.fetchGit {
      name = "agent-playground-python";                                                 
      url = "https://github.com/NixOS/nixpkgs/";                       
      ref = "refs/heads/nixpkgs-unstable";                     
      rev = "8ad5e8132c5dcf977e308e7bf5517cc6cc0bf7d8"; # Python 3.11.2                                       
  }) {}; 
in 
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