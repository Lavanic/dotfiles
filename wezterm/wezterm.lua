local wezterm = require("wezterm")
local config = wezterm.config_builder()

-- ─────────────────────────────────────────────────────────
--  Font
-- ─────────────────────────────────────────────────────────
config.font = wezterm.font_with_fallback({
  "Lilex Nerd Font",
  "Symbols Nerd Font Mono",
})
config.font_size = 12.0

-- ─────────────────────────────────────────────────────────
--  btop Default Theme (hand-matched from source)
--
--  Background: #000000  (btop main_bg)
--  Foreground: #ffffff  (btop main_fg)
--  Yellow:     #ffff55  (btop title color)
--  Red hi:     #ff5555  (btop hi_fg)
--  CPU green:  #50f095  (btop cpu_start)
--  CPU yellow: #f0c050  (btop cpu_mid)
--  CPU red:    #f05050  (btop cpu_end)
--  Temp blue:  #4897d4  (btop temp_start)
--  Temp purp:  #ff40b6  (btop temp_end)
--  Box teal:   #5f8787  (btop cpu_box)
--  Graph txt:  #bcbcbc  (btop graph_text)
--  Selection:  #555555  (btop selected_bg)
-- ─────────────────────────────────────────────────────────
config.colors = {
  foreground    = "#ffffff",
  background    = "#000000",

  cursor_bg     = "#ffff55",
  cursor_fg     = "#000000",
  cursor_border = "#ffff55",

  selection_fg  = "#ffffff",
  selection_bg  = "#555555",

  -- ANSI 0–7  (normal)
  ansi = {
    "#000000",  -- 0 black
    "#f05050",  -- 1 red      (btop cpu_end / process_end)
    "#50f095",  -- 2 green    (btop cpu_start / free_end)
    "#f0c050",  -- 3 yellow   (btop cpu_mid)
    "#4897d4",  -- 4 blue     (btop temp_start)
    "#ff40b6",  -- 5 magenta  (btop temp_end)
    "#5f8787",  -- 6 cyan     (btop cpu_box / border teal)
    "#bcbcbc",  -- 7 white    (btop graph_text)
  },

  -- ANSI 8–15 (bright)
  brights = {
    "#555555",  -- 8  bright black  (btop meter_bg / inactive_fg)
    "#ff5555",  -- 9  bright red    (btop hi_fg)
    "#90ff90",  -- 10 bright green  (btop free_end)
    "#ffe080",  -- 11 bright yellow (btop available_end)
    "#8080ff",  -- 12 bright blue   (btop download_end)
    "#ff80ff",  -- 13 bright magenta(btop upload_end)
    "#87afaf",  -- 14 bright cyan   (slightly lighter box teal)
    "#ffffff",  -- 15 bright white
  },

  tab_bar = {
    background = "#000000",
    active_tab = {
      bg_color  = "#5f8787",
      fg_color  = "#ffffff",
      intensity = "Bold",
    },
    inactive_tab = {
      bg_color = "#111111",
      fg_color = "#bcbcbc",
    },
    inactive_tab_hover = {
      bg_color = "#333333",
      fg_color = "#ffffff",
    },
    new_tab = {
      bg_color = "#000000",
      fg_color = "#555555",
    },
    new_tab_hover = {
      bg_color = "#333333",
      fg_color = "#ffffff",
    },
  },
}

-- ─────────────────────────────────────────────────────────
--  Window
-- ─────────────────────────────────────────────────────────
config.window_background_opacity = 0.92
config.text_background_opacity    = 1.0
config.window_padding = {
  left = 8, right = 8, top = 8, bottom = 8,
}

-- ─────────────────────────────────────────────────────────
--  Tab bar
-- ─────────────────────────────────────────────────────────
config.enable_tab_bar            = true
config.hide_tab_bar_if_only_one_tab = true
config.use_fancy_tab_bar         = false
config.tab_max_width             = 32

-- ─────────────────────────────────────────────────────────
--  Cursor
-- ─────────────────────────────────────────────────────────
config.cursor_blink_rate  = 500
config.cursor_thickness   = 2
config.default_cursor_style = "BlinkingBar"

-- ─────────────────────────────────────────────────────────
--  Shell
-- ─────────────────────────────────────────────────────────
config.default_prog = { "/usr/bin/fish", "-l" }

-- ─────────────────────────────────────────────────────────
--  Key bindings
--
--  Pane splitting:
--    CTRL+SHIFT+Enter → split RIGHT  (new pane to the right)
--    ALT+Enter        → split DOWN   (new pane below)
--    CTRL+SHIFT+Q     → close current pane
--
--  Pane navigation:
--    CTRL+SHIFT+←/→/↑/↓ → move focus between panes
--
--  Pane resizing:
--    ALT+←/→/↑/↓     → resize current pane
--
--  Tabs:
--    CTRL+T           → new tab
--    CTRL+W           → close tab
--    CTRL+1…9         → jump to tab N
--    CTRL+SHIFT+←/→   → move tab left/right (overloaded with pane nav below)
--
--  Window:
--    F11              → toggle fullscreen
--    CTRL+SHIFT+F     → toggle fullscreen (alt binding)
-- ─────────────────────────────────────────────────────────
config.keys = {
  -- Fullscreen
  { key = "F11",       mods = "",           action = wezterm.action.ToggleFullScreen },
  { key = "F",         mods = "CTRL|SHIFT", action = wezterm.action.ToggleFullScreen },

  -- Pane splits
  { key = "Enter",     mods = "CTRL|SHIFT", action = wezterm.action.SplitHorizontal{ domain = "CurrentPaneDomain" } },
  { key = "Enter",     mods = "ALT",        action = wezterm.action.SplitVertical{   domain = "CurrentPaneDomain" } },
  { key = "q",         mods = "CTRL|SHIFT", action = wezterm.action.CloseCurrentPane{ confirm = true } },

  -- Pane navigation
  { key = "LeftArrow",  mods = "CTRL|SHIFT", action = wezterm.action.ActivatePaneDirection("Left")  },
  { key = "RightArrow", mods = "CTRL|SHIFT", action = wezterm.action.ActivatePaneDirection("Right") },
  { key = "UpArrow",    mods = "CTRL|SHIFT", action = wezterm.action.ActivatePaneDirection("Up")    },
  { key = "DownArrow",  mods = "CTRL|SHIFT", action = wezterm.action.ActivatePaneDirection("Down")  },

  -- Pane resize (ALT + arrow)
  { key = "LeftArrow",  mods = "ALT", action = wezterm.action.AdjustPaneSize{ "Left",  5 }  },
  { key = "RightArrow", mods = "ALT", action = wezterm.action.AdjustPaneSize{ "Right", 5 }  },
  { key = "UpArrow",    mods = "ALT", action = wezterm.action.AdjustPaneSize{ "Up",    5 }  },
  { key = "DownArrow",  mods = "ALT", action = wezterm.action.AdjustPaneSize{ "Down",  5 }  },

  -- Tabs
  { key = "t",  mods = "CTRL",       action = wezterm.action.SpawnTab("CurrentPaneDomain") },
  { key = "w",  mods = "CTRL",       action = wezterm.action.CloseCurrentTab{ confirm = true } },
  { key = "1",  mods = "CTRL",       action = wezterm.action.ActivateTab(0) },
  { key = "2",  mods = "CTRL",       action = wezterm.action.ActivateTab(1) },
  { key = "3",  mods = "CTRL",       action = wezterm.action.ActivateTab(2) },
  { key = "4",  mods = "CTRL",       action = wezterm.action.ActivateTab(3) },
  { key = "5",  mods = "CTRL",       action = wezterm.action.ActivateTab(4) },
  { key = "6",  mods = "CTRL",       action = wezterm.action.ActivateTab(5) },
  { key = "7",  mods = "CTRL",       action = wezterm.action.ActivateTab(6) },
  { key = "8",  mods = "CTRL",       action = wezterm.action.ActivateTab(7) },
  { key = "9",  mods = "CTRL",       action = wezterm.action.ActivateTab(8) },

  -- Font size
  { key = "=",  mods = "CTRL",       action = wezterm.action.IncreaseFontSize },
  { key = "-",  mods = "CTRL",       action = wezterm.action.DecreaseFontSize },
  { key = "0",  mods = "CTRL",       action = wezterm.action.ResetFontSize    },

  -- Search
  { key = "f",  mods = "CTRL",       action = wezterm.action.Search{ CaseInSensitiveString = "" } },

  -- Copy/paste
  { key = "c",  mods = "CTRL|SHIFT", action = wezterm.action.CopyTo("Clipboard")   },
  { key = "v",  mods = "CTRL|SHIFT", action = wezterm.action.PasteFrom("Clipboard") },
}

return config
