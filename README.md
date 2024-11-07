# Puzzle games for script kiddies

This is a collection of silly little puzzle games you can play in your terminal
that are themed around the hacking scenes found in big Hollywood movies.

This was a project I undertook a number of years ago to practice Python. It's
here for your enjoyment, but I probably won't be updating it.

![GUI Screenshot](images/gui.png)

## Installation

To install the game launcher from git, [install
uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```shell
uv tool install --from git+https://github.com/lostatc/skiddie-games skiddie-games
```

Alternatively, you can run the launcher ad-hoc without installing it:

```shell
uvx --from git+https://github.com/lostatc/skiddie-games skiddie-games
```

## Usage

To play the games in this collection, there's a TUI launcher. The launcher lets
you configure the difficulty and save high scores. Just run `skiddie-games`.
You can use `Up`, `Down`, and `Tab` to navigate, `Enter` to select, and `q` to
quit.

There's also a CLI. For more information, run `skiddie-games --help`.

## Games

Game | Description | Screenshot
--- | --- | ---
**database_querier** | [Description](./src/skiddie/descriptions/database_querier.md) | [Screenshot](./images/database_querier.png)
**hash_cracker** | [Description](./src/skiddie/descriptions/hash_cracker.md) | [Screenshot](./images/hash_cracker.png)
**hex_editor** | [Description](./src/skiddie/descriptions/hex_editor.md) | [Screenshot](./images/hex_editor.png)
**pattern_finder** | [Description](./src/skiddie/descriptions/pattern_finder.md) | [Screenshot](./images/pattern_finder.png)
**port_scanner** | [Description](./src/skiddie/descriptions/port_scanner.md) | [Screenshot](./images/port_scanner.png)
**shell_scripter** | [Description](./src/skiddie/descriptions/shell_scripter.md) | [Screenshot](./images/shell_scripter.png)
**tree_builder** | [Description](./src/skiddie/descriptions/tree_builder.md) | [Screenshot](./images/tree_builder.png)
