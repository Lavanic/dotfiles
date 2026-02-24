# otop

The palette used across this repo. It started as a hand-match of btop's
default theme, but it drifted brighter: only the temp gradient and the black
background survived contact. So it is its own thing now: otop.

## Palette

| Name    | Hex       | ANSI slot        | Used for                          |
| ------- | --------- | ---------------- | --------------------------------- |
| black   | `#000000` | 0                | backgrounds                       |
| red     | `#f05050` | 1                | errors, deletions, hot            |
| green   | `#50f095` | 2                | success, additions, user          |
| yellow  | `#f0c050` | 3                | warnings, directories, mid        |
| blue    | `#4897d4` | 4                | info, git branch, cool            |
| magenta | `#ff40b6` | 5                | accents, gradient ends            |
| teal    | `#5f8787` | 6                | borders, hostname, chrome         |
| text    | `#bcbcbc` | 7                | secondary text                    |
| grey    | `#555555` | 8                | selections, inactive              |
| white   | `#ffffff` | 15               | primary text                      |
| bright red     | `#ff5555` | 9  | highlights                 |
| bright green   | `#90ff90` | 10 | gradient ends              |
| bright yellow  | `#ffe080` | 11 | gradient ends              |
| bright blue    | `#8080ff` | 12 | gradient ends              |
| bright magenta | `#ff80ff` | 13 | gradient ends              |
| bright teal    | `#87afaf` | 14 | hover chrome               |

Window transparency: 0.92 opacity over black, blur on when the compositor
offers it.

## Where it lives

- `wezterm` sets the palette as the terminal's 16 ANSI slots. Anything that
  can render in plain ANSI colors inherits otop for free; prefer a tool's
  "terminal colors" mode before hand-theming it.
- `starship` names the colors once in `[palettes.otop]`.
- `zed` has a theme file at `zed/.config/zed/themes/otop.json`.
- `btop` runs `btop/.config/btop/themes/otop.theme`.

To theme a new tool: try its ANSI/terminal-colors mode first; otherwise copy
hexes from the table.

## For the record: real btop Default values

Where otop deliberately differs from btop's actual source
(src/btop_theme.cpp), in case I ever want to dial the neon back:

| Role         | otop      | real btop |
| ------------ | --------- | --------- |
| cpu_start    | `#50f095` | `#77ca9b` |
| cpu_mid      | `#f0c050` | `#cbc06c` |
| cpu_end      | `#f05050` | `#dc4c4c` |
| hi_fg        | `#ff5555` | `#b54040` |
| main_fg      | `#ffffff` | `#cccccc` |
| boxes        | `#5f8787` | `#556d59` |
| selected_bg  | `#555555` | `#6a2f2f` |
| graph_text   | `#bcbcbc` | `#606060` |
| temp_start   | `#4897d4` | `#4897d4` (match) |
| temp_end     | `#ff40b6` | `#ff40b6` (match) |
