# Installs my preferred tooling for working on this project.
# Neovim and Plugins

# TODO
  # Git
  # Python and Dependencies

# To run:
# make nix

{pkgs ? import <nixpkgs> {}}:

let 
  myNeovim = pkgs.neovim.override {
    configure = {
      customRC = "execute 'source ./dev/init.lua'";
      packages.myVimPackage = with pkgs.vimPlugins; {
        start = [ 
          which-key-nvim    # Display's Key Mappings
          nvim-tree-lua     # File Browser
          nvim-web-devicons # Dev Icons
          barbar-nvim       # Tabs
          onedark-vim
          # nightfox-nvim   # Dark Theme
        ];
        opt = [ ];
      }; 
    };     
  };
in
pkgs.mkShell {
  name = "dev";
  buildInputs = [ 
    pkgs.git
    pkgs.gnumake
    pkgs.cloc
    myNeovim
  ];
}