local wezterm = require("wezterm")
local config = wezterm.config_builder()

-- Font
config.font = wezterm.font_with_fallback({
  "Lilex Nerd Font",
  "Symbols Nerd Font Mono",
})
config.font_size = 12.0

-- otop palette (see otop.md at the repo root)
config.colors = {
  foreground    = "#ffffff",
  background    = "#000000",

  cursor_bg     = "#ffff55",
  cursor_fg     = "#000000",
  cursor_border = "#ffff55",

  selection_fg  = "#ffffff",
  selection_bg  = "#555555",

  ansi = {
    "#000000",  -- black
    "#f05050",  -- red
    "#50f095",  -- green
    "#f0c050",  -- yellow
    "#4897d4",  -- blue
    "#ff40b6",  -- magenta
    "#5f8787",  -- cyan (teal)
    "#bcbcbc",  -- white (text)
  },

  brights = {
    "#555555",  -- bright black (grey)
    "#ff5555",  -- bright red
    "#90ff90",  -- bright green
    "#ffe080",  -- bright yellow
    "#8080ff",  -- bright blue
    "#ff80ff",  -- bright magenta
    "#87afaf",  -- bright cyan
    "#ffffff",  -- bright white
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

-- Window
config.window_background_opacity = 0.92
config.text_background_opacity    = 1.0
config.window_padding = {
  left = 8, right = 8, top = 8, bottom = 8,
}

-- Tab bar
config.enable_tab_bar            = true
config.hide_tab_bar_if_only_one_tab = true
config.use_fancy_tab_bar         = false
config.tab_max_width             = 32

-- Cursor
config.cursor_blink_rate  = 500
config.cursor_thickness   = 2
config.default_cursor_style = "BlinkingBar"

-- Shell
config.default_prog = { "/usr/bin/fish", "-l" }

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

  -- Pane resize
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
