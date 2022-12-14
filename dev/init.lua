-- disable netrw at the very start of your init.lua (strongly advised)
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1

vim.cmd([[
  set ruler 
  set ignorecase 
  set smartcase 
  set hlsearch 
  set showmatch
  syntax enable
  set expandtab
  set smarttab 
  set lbr 
]])

-- Height of the command bar
vim.opt.cmdheight = 1

-- 1 tab == 2 spaces
vim.opt.shiftwidth=2
vim.opt.tabstop=2

-- Linebreak on 500 characters
vim.opt.tw=500

vim.opt.ai = true
vim.opt.si = true
vim.opt.wrap = true
-- set termguicolors to enable highlight groups
vim.opt.termguicolors = true

-- Setup nvim-tree plugin
require("nvim-tree").setup()

--Setup Which Key Plugin and Bindings
-- let wk = require("which-key")
-- wk.setup()
-- key_mappings = {}

-- wk.register(key_mappings)

-- Time in milliseconds to wait for a mapped sequence to complete.
vim.opt.timeoutlen = 300

-- Key Bindings
-- set(mode, keys, action, options)
-- cntrl + b Toggles the Tree View
vim.keymap.set({'n', 'i'}, '<C-b>', '<CMD>NvimTreeToggle<CR>') 

--Toggle a Terminal Window
-- ctrl + t -> Toggles a terminal
-- vim.keymap.set({'n', 'i'}, '<C-t>', '<CMD>terminal<CR>') 