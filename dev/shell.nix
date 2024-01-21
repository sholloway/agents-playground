# Installs my preferred tooling for working on this project.

# We need to make sure that the correct version of python is installed.
# https://github.com/NixOS/nixpkgs/issues/9682
# https://lazamar.co.uk/nix-versions
# https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md

{pkgs ? import <nixpkgs> {}}:

let
  pkgs = import (builtins.fetchGit {
      name = "agent-playground-python";                                                 
      url = "https://github.com/NixOS/nixpkgs/";                       
      ref = "refs/heads/nixpkgs-unstable";                     
      rev = "9957cd48326fe8dbd52fdc50dd2502307f188b0d"; # Python 3.11.4          
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