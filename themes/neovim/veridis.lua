-- Veridis — Neovim Colorscheme
-- Warm-black dark palette. Electric mint accent. Named after Daft Punk's Veridis Quo.
-- Install: copy to ~/.config/nvim/colors/veridis.lua
-- Usage:   :colorscheme veridis  |  vim.cmd.colorscheme("veridis")

vim.cmd("hi clear")
if vim.fn.exists("syntax_on") then vim.cmd("syntax reset") end
vim.g.colors_name   = "veridis"
vim.o.termguicolors = true
vim.o.background    = "dark"

local c = {
  bg      = "#000000",
  bg1     = "#0f0e0d",
  bg2     = "#1a1715",
  surface = "#141210",
  overlay = "#2a2623",
  text    = "#f2efec",
  subtle  = "#b1a8a2",
  dim     = "#817771",
  mint    = "#00ffb2",
  cyan    = "#00e0a0",
  green   = "#4de8c0",
  teal    = "#00c490",
  jade    = "#7adec8",
  aqua    = "#a8f0de",
  emerald = "#00a878",
  lime    = "#d0f7ec",
  none    = "NONE",
}

local function hi(group, opts)
  vim.api.nvim_set_hl(0, group, opts)
end

-- ── Editor UI ────────────────────────────────────────────────────────────────
hi("Normal",        { fg = c.text,   bg = c.bg })
hi("NormalNC",      { fg = c.text,   bg = c.bg })
hi("NormalFloat",   { fg = c.text,   bg = c.surface })
hi("FloatBorder",   { fg = c.bg2,    bg = c.surface })
hi("FloatTitle",    { fg = c.mint,   bg = c.surface, bold = true })
hi("Pmenu",         { fg = c.subtle, bg = c.surface })
hi("PmenuSel",      { fg = c.mint,   bg = c.overlay, bold = true })
hi("PmenuSbar",     { bg = c.bg1 })
hi("PmenuThumb",    { bg = c.overlay })

hi("CursorLine",    { bg = c.bg1 })
hi("CursorLineNr",  { fg = c.subtle, bg = c.bg, bold = true })
hi("LineNr",        { fg = c.dim,    bg = c.bg })
hi("SignColumn",    { fg = c.dim,    bg = c.bg })
hi("ColorColumn",   { bg = c.bg1 })
hi("Cursor",        { fg = c.bg,     bg = c.mint })
hi("CursorIM",      { fg = c.bg,     bg = c.mint })
hi("TermCursor",    { fg = c.bg,     bg = c.mint })

hi("Visual",        { bg = c.overlay })
hi("VisualNOS",     { bg = c.overlay })
hi("Search",        { fg = c.bg,     bg = c.mint })
hi("IncSearch",     { fg = c.bg,     bg = c.mint, bold = true })
hi("CurSearch",     { fg = c.bg,     bg = c.mint })
hi("Substitute",    { fg = c.bg,     bg = c.cyan })

hi("StatusLine",    { fg = c.subtle, bg = c.bg1 })
hi("StatusLineNC",  { fg = c.dim,    bg = c.bg1 })
hi("TabLine",       { fg = c.dim,    bg = c.bg1 })
hi("TabLineFill",   { bg = c.bg1 })
hi("TabLineSel",    { fg = c.mint,   bg = c.bg,  bold = true })
hi("WinBar",        { fg = c.subtle, bg = c.bg })
hi("WinBarNC",      { fg = c.dim,    bg = c.bg })
hi("WinSeparator",  { fg = c.bg2 })

hi("Folded",        { fg = c.dim,    bg = c.bg1, italic = true })
hi("FoldColumn",    { fg = c.dim,    bg = c.bg })
hi("EndOfBuffer",   { fg = c.bg1 })
hi("NonText",       { fg = c.bg2 })
hi("Whitespace",    { fg = c.overlay })
hi("SpecialKey",    { fg = c.overlay })
hi("MatchParen",    { fg = c.mint,   bg = c.overlay, bold = true })

hi("MsgArea",       { fg = c.subtle })
hi("MsgSeparator",  { fg = c.bg2,    bg = c.bg })
hi("MoreMsg",       { fg = c.mint })
hi("Question",      { fg = c.mint })
hi("ErrorMsg",      { fg = c.lime,   bg = c.emerald })
hi("WarningMsg",    { fg = c.aqua })

hi("Directory",     { fg = c.mint })
hi("Title",         { fg = c.mint,   bold = true })
hi("VertSplit",     { fg = c.bg2 })

hi("DiffAdd",       { fg = c.mint,   bg = c.bg1 })
hi("DiffChange",    { fg = c.jade,   bg = c.bg1 })
hi("DiffDelete",    { fg = c.emerald, bg = c.bg1 })
hi("DiffText",      { fg = c.aqua,   bg = c.bg2, bold = true })

hi("SpellBad",      { sp = c.emerald, undercurl = true })
hi("SpellCap",      { sp = c.aqua,   undercurl = true })
hi("SpellLocal",    { sp = c.jade,   undercurl = true })
hi("SpellRare",     { sp = c.subtle, undercurl = true })

-- ── Syntax ───────────────────────────────────────────────────────────────────
hi("Comment",       { fg = c.dim,    italic = true })
hi("Constant",      { fg = c.jade })
hi("String",        { fg = c.lime })
hi("Character",     { fg = c.lime })
hi("Number",        { fg = c.aqua })
hi("Float",         { fg = c.aqua })
hi("Boolean",       { fg = c.jade })

hi("Identifier",    { fg = c.text })
hi("Function",      { fg = c.cyan })

hi("Statement",     { fg = c.jade })
hi("Conditional",   { fg = c.jade })
hi("Repeat",        { fg = c.jade })
hi("Label",         { fg = c.teal })
hi("Operator",      { fg = c.teal })
hi("Keyword",       { fg = c.jade })
hi("Exception",     { fg = c.jade })

hi("PreProc",       { fg = c.jade })
hi("Include",       { fg = c.jade })
hi("Define",        { fg = c.jade })
hi("Macro",         { fg = c.jade })
hi("PreCondit",     { fg = c.jade })

hi("Type",          { fg = c.mint })
hi("StorageClass",  { fg = c.jade })
hi("Structure",     { fg = c.mint })
hi("Typedef",       { fg = c.mint })

hi("Special",       { fg = c.teal })
hi("SpecialChar",   { fg = c.aqua })
hi("Tag",           { fg = c.mint })
hi("Delimiter",     { fg = c.subtle })
hi("SpecialComment",{ fg = c.dim,  italic = true })
hi("Debug",         { fg = c.aqua })

hi("Underlined",    { fg = c.cyan,  underline = true })
hi("Ignore",        { fg = c.dim })
hi("Error",         { fg = c.lime,  bg = c.emerald })
hi("Todo",          { fg = c.bg,    bg = c.teal, bold = true })

-- ── Treesitter ───────────────────────────────────────────────────────────────
hi("@comment",             { fg = c.dim,    italic = true })
hi("@comment.doc",         { fg = c.subtle, italic = true })
hi("@keyword",             { fg = c.jade })
hi("@keyword.function",    { fg = c.jade })
hi("@keyword.operator",    { fg = c.teal })
hi("@keyword.return",      { fg = c.jade })
hi("@function",            { fg = c.cyan })
hi("@function.builtin",    { fg = c.cyan })
hi("@function.method",     { fg = c.cyan })
hi("@function.call",       { fg = c.cyan })
hi("@method",              { fg = c.cyan })
hi("@method.call",         { fg = c.cyan })
hi("@constructor",         { fg = c.mint })
hi("@type",                { fg = c.mint })
hi("@type.builtin",        { fg = c.jade })
hi("@type.qualifier",      { fg = c.jade })
hi("@variable",            { fg = c.text })
hi("@variable.builtin",    { fg = c.aqua })
hi("@variable.parameter",  { fg = c.aqua })
hi("@field",               { fg = c.cyan })
hi("@property",            { fg = c.cyan })
hi("@string",              { fg = c.lime })
hi("@string.escape",       { fg = c.aqua })
hi("@string.regex",        { fg = c.green })
hi("@number",              { fg = c.aqua })
hi("@float",               { fg = c.aqua })
hi("@boolean",             { fg = c.jade })
hi("@constant",            { fg = c.jade })
hi("@constant.builtin",    { fg = c.jade })
hi("@operator",            { fg = c.teal })
hi("@punctuation",         { fg = c.subtle })
hi("@punctuation.bracket", { fg = c.subtle })
hi("@punctuation.delimiter",{ fg = c.subtle })
hi("@punctuation.special", { fg = c.teal })
hi("@tag",                 { fg = c.mint })
hi("@tag.attribute",       { fg = c.jade })
hi("@tag.delimiter",       { fg = c.subtle })
hi("@namespace",           { fg = c.jade })
hi("@include",             { fg = c.jade })
hi("@error",               { fg = c.lime, bg = c.emerald })

-- Markdown / notetaking
hi("@text",                { fg = c.text })
hi("@text.title",          { fg = c.mint,   bold = true })
hi("@text.title.1.marker", { fg = c.dim })
hi("@text.title.2.marker", { fg = c.dim })
hi("@text.title.3.marker", { fg = c.dim })
hi("@text.strong",         { fg = c.text,   bold = true })
hi("@text.emphasis",       { fg = c.subtle, italic = true })
hi("@text.strike",         { fg = c.dim,    strikethrough = true })
hi("@text.uri",            { fg = c.cyan,   underline = true })
hi("@text.reference",      { fg = c.mint })
hi("@text.raw",            { fg = c.jade })
hi("@text.literal",        { fg = c.jade,   bg = c.surface })
hi("@text.quote",          { fg = c.subtle, italic = true })
hi("@text.todo",           { fg = c.bg,     bg = c.teal, bold = true })
hi("@text.note",           { fg = c.bg,     bg = c.cyan })
hi("@text.warning",        { fg = c.bg,     bg = c.aqua })
hi("@text.danger",         { fg = c.bg,     bg = c.emerald })
hi("@text.diff.add",       { fg = c.mint })
hi("@text.diff.delete",    { fg = c.emerald })

-- ── LSP ──────────────────────────────────────────────────────────────────────
hi("DiagnosticError",           { fg = c.emerald })
hi("DiagnosticWarn",            { fg = c.aqua })
hi("DiagnosticInfo",            { fg = c.jade })
hi("DiagnosticHint",            { fg = c.dim })
hi("DiagnosticUnderlineError",  { sp = c.emerald, undercurl = true })
hi("DiagnosticUnderlineWarn",   { sp = c.aqua,   undercurl = true })
hi("DiagnosticUnderlineInfo",   { sp = c.jade,   undercurl = true })
hi("DiagnosticUnderlineHint",   { sp = c.dim,    undercurl = true })
hi("LspReferenceText",          { bg = c.overlay })
hi("LspReferenceRead",          { bg = c.overlay })
hi("LspReferenceWrite",         { bg = c.overlay, bold = true })
hi("LspSignatureActiveParameter",{ fg = c.mint, bold = true })

-- ── Gitsigns / Git ────────────────────────────────────────────────────────────
hi("GitSignsAdd",    { fg = c.mint })
hi("GitSignsChange", { fg = c.jade })
hi("GitSignsDelete", { fg = c.emerald })

-- ── Telescope ────────────────────────────────────────────────────────────────
hi("TelescopeNormal",         { fg = c.text,   bg = c.surface })
hi("TelescopeBorder",         { fg = c.bg2,    bg = c.surface })
hi("TelescopeTitle",          { fg = c.mint,   bg = c.surface, bold = true })
hi("TelescopePromptNormal",   { fg = c.text,   bg = c.bg1 })
hi("TelescopePromptBorder",   { fg = c.bg2,    bg = c.bg1 })
hi("TelescopePromptPrefix",   { fg = c.mint })
hi("TelescopeMatching",       { fg = c.mint,   bold = true })
hi("TelescopeSelection",      { fg = c.mint,   bg = c.overlay })
hi("TelescopeMultiSelection", { fg = c.teal,   bg = c.overlay })

-- ── Terminal colors ───────────────────────────────────────────────────────────
vim.g.terminal_color_0  = c.bg1
vim.g.terminal_color_1  = c.emerald
vim.g.terminal_color_2  = c.green
vim.g.terminal_color_3  = c.lime
vim.g.terminal_color_4  = c.cyan
vim.g.terminal_color_5  = c.teal
vim.g.terminal_color_6  = c.jade
vim.g.terminal_color_7  = c.text
vim.g.terminal_color_8  = c.dim
vim.g.terminal_color_9  = c.cyan
vim.g.terminal_color_10 = c.green
vim.g.terminal_color_11 = c.aqua
vim.g.terminal_color_12 = c.mint
vim.g.terminal_color_13 = c.teal
vim.g.terminal_color_14 = c.jade
vim.g.terminal_color_15 = c.text
