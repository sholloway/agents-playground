# Installs my preferred tooling for working on this project.
# Neovim and Plugins
# Git
# Python and Dependencies

# To run:
# nix-shell shell.nix

{pkgs ? import <nixpkgs> {}}:

let 
  myNeovim = pkgs.neovim.override {
    configure = {
      customRC = "execute 'source ./dev/init.lua'";
      packages.myVimPackage = with pkgs.vimPlugins; {
        start = [ 
          nvim-tree-lua 
          onedark-vim
        ];
        opt = [ ];
      }; 
    };     
  };
in
pkgs.mkShell {
  name = "dev";
  buildInputs = [ 
    myNeovim
  ];
}