# gpyt

> GPT in your terminal.

>> WIP


## Demo

![gpyt demo](https://github.com/JustinStitt/gpyt/blob/master/media/gpyt-show-1.gif?raw=true)

Uses [Textual](https://textual.textualize.io).


### Installation & Usage
1) `$ pip install gpyt`

2) add `OPENAI_API_KEY="<your_openai_api_key>"` in a `.env` at $HOME or `export OPENAI_API_KEY=<your_key>`

3) `$ gpyt`

### Keybindings

* `ctrl-b` -> Toggle Dark/Light Mode
* `ctrl-n` -> Open Past Conversations Sidebar
* `ctrl-c` -> Quit


### TODO

- [ ] `copy` to copy GPT's response to clipboard
- [ ] add gpt jailbreaks (DAN-esque)
- [ ] add special flags like -t (terse) or -v (verbose) or -d (detailed) or -i
- [ ] (informal) or -f (for file input) or --dan (for jailbreak)
- [ ] model select CLI
- [ ] add API_KEY from CLI
- [ ] gpt4free integration (for 3.5 and 4)
- [ ] refactor the f**k out of `app.py`
- [ ] copy/pasting with mouse
