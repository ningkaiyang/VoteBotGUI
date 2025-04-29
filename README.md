# voteBot

VoteBot is a JavaScript-based bot designed for automated voting on [Poll.fm/](https://poll.fm/). It utilizes Puppeteer with enhancements for stealth and efficiency.

## Project Structure

```
.
├── voteBot/
│   ├── voteBot.js        # The main Node.js bot script
│   ├── runVoteBot.bat    # Windows script to run the bot
│   └── runVoteBot.sh     # Linux/macOS script to run the bot
├── voteBot_gui.py        # Optional Python GUI for managing bot instances
├── package.json          # Project dependencies and scripts
├── LICENSE               # Project license file
└── README.md             # This file
```

**Features:**
*   Uses `puppeteer-extra` with the stealth plugin to appear more like a regular browser.
*   Implements human-like behavior with randomized short pauses between actions.
*   Randomizes delays between votes to avoid predictable patterns.
*   Randomizes browser User Agent strings for each new page.
*   Randomizes browser viewport dimensions for every voting session.
*   Creates new browser pages for each vote (reusing the main browser instance) for efficient resource usage.
*   Supports using an HTTP/HTTPS proxy via an environment variable.
*   Configurable via environment variables.
*   Includes graceful shutdown handling when Ctrl+C is pressed.
*   Features increased timeout values for better reliability on slower connections.

## How to Use

1.  [Download and install Node.js](https://nodejs.org/).
2.  Clone or download this repository.
3.  Open a terminal or command prompt in the bot's main directory (`voteBot`).
4.  Install dependencies by running:
    ```bash
    npm install
    ```
    or using **yarn**:
    ```bash
    yarn install
    ```
    or using **pnpm**:
    ```bash
    pnpm install
    ```
    This will install `puppeteer`, `puppeteer-extra`, and `puppeteer-extra-plugin-stealth`. Puppeteer will download a compatible Chromium browser instance.

5.  **Set Environment Variables:** The bot requires configuration via environment variables. How you set these depends on your OS:
    *   **Linux/macOS (Terminal):**
        ```bash
        export POLLURL="YOUR_POLL_URL_HERE"
        export ANSWERID="YOUR_ANSWER_ID_HERE"
        # Optional:
        # export PROXY_URL="http://yourproxy:port"
        # export MIN_DELAY="10" # Min delay in seconds (default 5)
        # export MAX_DELAY="30" # Max delay in seconds (default 20)
        ```
    *   **Windows (Command Prompt):**
        ```cmd
        set POLLURL="YOUR_POLL_URL_HERE"
        set ANSWERID="YOUR_ANSWER_ID_HERE"
        rem Optional:
        rem set PROXY_URL="http://yourproxy:port"
        rem set MIN_DELAY="10"
        rem set MAX_DELAY="30"
        ```
    *   **Windows (PowerShell):**
        ```powershell
        $env:POLLURL="YOUR_POLL_URL_HERE"
        $env:ANSWERID="YOUR_ANSWER_ID_HERE"
        # Optional:
        # $env:PROXY_URL="http://yourproxy:port"
        # $env:MIN_DELAY="10"
        # $env:MAX_DELAY="30"
        ```
    *   Replace `"YOUR_POLL_URL_HERE"` with the full URL of the poll page.
    *   Replace `"YOUR_ANSWER_ID_HERE"` with the ID of the radio button/checkbox input element for your desired answer. You can find this using your browser's "Inspect Element" tool. It usually looks like `PDI_answerXXXXXXXX`.
    *   `PROXY_URL` is optional. If set, traffic will be routed through this proxy.
    *   `MIN_DELAY` and `MAX_DELAY` control the random wait time (in seconds) between vote attempts.

6.  **Run the Bot:** Navigate into the `voteBot` sub-directory (where `voteBot.js` is located) in your terminal/command prompt and execute the script directly:
    ```bash
    node voteBot.js
    ```
    Alternatively, you can use the provided wrapper scripts (ensure they are executable on Linux/macOS: `chmod +x runVoteBot.sh`):
    *   Windows: `runVoteBot.bat`
    *   Linux/macOS: `./runVoteBot.sh`

    The bot will now run continuously, printing logs to the console. Press `Ctrl+C` to stop it gracefully.

## Graphical User Interface (GUI)

Alternatively to running `node voteBot.js` directly, you can use the Python-based GUI (`voteBot_gui.py`) to manage multiple bot instances simultaneously.\n
**Prerequisites:**
*   Python 3 installed.
*   The `tkinter` library (usually included with standard Python installations).

**How to Use the GUI:**

1.  Ensure you have followed steps 1-4 in the "How to Use" section above to install Node.js and the `voteBot` dependencies (`npm install`).
2.  Open a terminal or command prompt in the main directory (where `voteBot_gui.py` is located).
3.  Run the GUI script:
    ```bash
    python voteBot_gui.py
    ```
    On some systems, you might need to use `python3`.
4.  The GUI window will open.
5.  Enter the required information in the input fields:
    *   **Poll URL:** The full URL of the poll page (corresponds to `POLLURL`).
    *   **Answer ID:** The ID of the answer element (corresponds to `ANSWERID`).
    *   **Proxy URL (Optional):** An HTTP/HTTPS proxy (corresponds to `PROXY_URL`).
    *   **Delays (sec) - Min/Max:** The random delay range between votes (corresponds to `MIN_DELAY` and `MAX_DELAY`).
6.  Click the "Launch Instance" button to start a new bot process in the background. The GUI will show a panel for each running instance.
7.  Use the buttons on each instance panel:
    *   **Show Log:** Opens a separate window displaying the real-time output (logs) of that specific bot process.
    *   **Stop:** Gracefully stops the corresponding bot process.

The GUI allows you to launch multiple instances with different configurations if needed.

## System Requirements

*   Node.js installed.
*   Sufficient RAM (4GB+ recommended, depends on system usage). Puppeteer can be memory-intensive.
*   A reasonably modern CPU.
*   Internet connection.

## Warnings

*   **Resource Usage:** While this version is efficient by reusing the browser instance and creating new pages for each vote, running Puppeteer still consumes significant CPU and RAM. The bot is designed to clean up properly after each voting attempt to minimize resource buildup.
*   **Terms of Service:** Using automated voting scripts may violate the terms of service of the target website (Poll.fm). This can lead to IP bans or other consequences. Use this bot responsibly and ethically, respecting the website's policies. The developers of this bot are not responsible for misuse.
*   **IP Blocking:** Websites often implement measures to block excessive voting from a single IP address. Even with randomized delays, pauses, and stealth measures, your IP might get blocked after a certain number of votes. Using a rotating proxy service (via the `PROXY_URL` variable) can help mitigate this issue.
*   **Bot Detection:** While efforts have been made to make the bot less detectable (stealth plugin, randomization, human-like pauses), sophisticated anti-bot systems might still identify it. There is no guarantee of undetectability.

## Contributors

*   [Moderatuh](https://github.com/Moderatuh) - Significant refactoring for stealth, efficiency, and maintainability.
*   Original structure/concept by [pomodori92](https://github.com/pomodori92).

## Issues and Requests

If you encounter any bugs, please report them by creating a [new issue](https://github.com/pomodori92/voteBot/issues).

Feel free to submit [pull requests](https://github.com/pomodori92/voteBot/pulls). They are highly encouraged!