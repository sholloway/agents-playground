# Installs my preferred tooling for working on this project.
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