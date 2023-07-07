# gpyt

### GPT in your terminal.


> **Note**
> WIP

<img src="https://img.shields.io/badge/dynamic/json.svg?label=downloads&url=https%3A%2F%2Fpypistats.org%2Fapi%2Fpackages%2Fgpyt%2Frecent&query=data.last_month&colorB=brightgreen&suffix=%2FMonth"/>
<img src="https://img.shields.io/pypi/v/gpyt.svg"/>

---

Try out the new (experimental and buggy) **FREE** model using [GPT4Free](https://github.com/xtekky/gpt4free):

`$ gpyt --free`

^ NO API KEY required

OR Try out PaLM 2 (requires Google MakerSuite API KEY)

`$ gpyt --palm`

If you have access, you can try out GPT4

`$ gpyt --gpt4`

Uses [Textual](https://textual.textualize.io).

## Demo

![gpyt demo](https://github.com/JustinStitt/gpyt/blob/master/media/gpyt-show-1.gif?raw=true)



### Markdown Support

![markdown support](https://github.com/JustinStitt/gpyt/blob/master/media/md-support.png?raw=true)

![markdown support (showing table)](https://github.com/JustinStitt/gpyt/blob/master/media/md-support-2.png?raw=true)


### Installation & Usage
1) `$ pip install gpyt`

2) add `OPENAI_API_KEY="<your_openai_api_key>"` in a `.env` at $HOME or `export OPENAI_API_KEY=<your_key>`

3) `$ gpyt`

Or try this *optional* method for running **gpyt** if you don't have an api key:

4) `$ gpyt --free`

Or try this *optional* method for running **PaLM 2**, Google's premier LLM:

5) `$ gpyt --palm`
     - Be sure to set an api key at `~/.env` with the field `PALM_API_KEY`

### Keybindings

* `ctrl-b` -> Toggle Dark/Light Mode
* `ctrl-n` -> Open Past Conversations Sidebar
* `ctrl-c` -> Quit
* `ctrl-o` -> Model Selection Menu


### TODO

- [ ] `copy` to copy GPT's response to clipboard
- [ ] add gpt jailbreaks (DAN-esque)
- [ ] add special flags like -t (terse) or -v (verbose) or -d (detailed) or -i
- [ ] (informal) or -f (for file input) or --dan (for jailbreak)
- [ ] model select CLI
- [ ] add API_KEY from CLI
- [ ] gpt4free integration (~~for 3.5~~ and 4)
- [ ] refactor the f**k out of `app.py`
- [ ] copy/pasting with mouse
