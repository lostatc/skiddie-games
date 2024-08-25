# skiddie

skiddie is a collection of minigames that can be played in the terminal and are
meant to emulate Hollywood-style "hacking." They're just silly little puzzle
games themed around the hacking scenes found in many movies.

![GUI Screenshot](images/gui.png)

## Features

* No knowledge of programming or cybersecurity required
* Multiple difficulty levels for each game
* Create your own difficulty presets
* Tracks your scores in a leaderboard

## Installation

To install skiddie, [install
uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```shell
uvx --from git+https://github.com/lostatc/skiddie skiddie
```

## Usage

skiddie has a terminal-based graphical user interface. To launch it, just run
`skiddie` in your terminal. You can use `Up`, `Down`, and `Tab` to navigate,
`Enter` to select, and `q` to quit.

skiddie also has a command-line interface. For more information, run `skiddie
--help`.

## Games

Game | Description | Screenshot
--- | --- | ---
**database_querier** | [Description](skiddie/descriptions/database_querier.md) | [Screenshot](images/database_querier.png)
**hash_cracker** | [Description](skiddie/descriptions/hash_cracker.md) | [Screenshot](images/hash_cracker.png)
**hex_editor** | [Description](skiddie/descriptions/hex_editor.md) | [Screenshot](images/hex_editor.png)
**pattern_finder** | [Description](skiddie/descriptions/pattern_finder.md) | [Screenshot](images/pattern_finder.png)
**port_scanner** | [Description](skiddie/descriptions/port_scanner.md) | [Screenshot](images/port_scanner.png)
**shell_scripter** | [Description](skiddie/descriptions/shell_scripter.md) | [Screenshot](images/shell_scripter.png)
**tree_builder** | [Description](skiddie/descriptions/tree_builder.md) | [Screenshot](images/tree_builder.png)
