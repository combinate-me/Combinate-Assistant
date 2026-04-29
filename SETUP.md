# Getting Started

Welcome to the Combinate Assistant. This guide will walk you through every step of the setup process from scratch.

This will take about 15-20 minutes the first time. You only need to do this once.

---

## Step 1: Install VS Code

VS Code (Visual Studio Code) is a free application made by Microsoft. It is the program you will use to run the Combinate Assistant.

1. Open your web browser and go to **https://code.visualstudio.com**
2. Click the large blue **Download** button in the middle of the page
3. Open the file that downloads (it will appear in your Downloads folder or at the bottom of your browser window)
4. Follow the installer - click **Next** or **Continue** through each screen and accept the default options
5. When the installer finishes, open **VS Code**

You should see a welcome screen with a dark or light background. That means it worked.

---

## Step 2: Install Git

Git is a tool that lets you download files from GitHub (where the Combinate Assistant is stored). You may already have it installed.

**Check if you already have Git:**

1. In VS Code, click **Terminal** in the top menu bar, then click **New Terminal**
2. A panel will open at the bottom of the screen. Click inside it and type the following, then press **Enter**:
   ```
   git --version
   ```
3. If you see something like `git version 2.x.x`, Git is already installed. Skip to Step 3.
4. If you see an error or nothing happens, follow the instructions below.

**Installing Git on Mac:**

A pop-up will usually appear automatically asking you to install developer tools. Click **Install** and follow the prompts. If no pop-up appears, go to **https://git-scm.com/download/mac** and download the installer.

**Installing Git on Windows:**

1. Go to **https://git-scm.com/download/win**
2. The download will start automatically - open the file when it finishes
3. Click **Next** through all the installer screens, accepting the default settings
4. When finished, close and reopen VS Code

---

## Step 3: Set Up a Claude Account

Claude Code is the AI engine that powers this assistant. You need a Claude account to use it.

1. Go to **https://claude.ai** and create an account if you don't have one
2. You will need a **Claude Pro** subscription (or a Team account) - ask Shane if you are unsure which applies to you
3. Once your account is set up, keep the tab open - you will need it in the next step

---

## Step 4: Install the Claude Code Extension

1. In VS Code, look at the left side of the screen. You will see a vertical toolbar with icons. Click the icon that looks like **four small squares** (this is the Extensions panel)
2. A search box will appear at the top. Type **Claude Code** and press Enter
3. In the results, click on **Claude Code** (published by Anthropic)
4. Click the blue **Install** button
5. Once installed, a new **Claude icon** will appear in the left toolbar
6. Click the Claude icon, then click **Sign In** and follow the prompts to connect your Claude account

---

## Step 5: Download the Combinate Assistant

Now you will download the Combinate Assistant files to your computer.

1. In VS Code, click **View** in the top menu bar, then click **Command Palette**
   - On Mac you can also press **Cmd + Shift + P**
   - On Windows you can also press **Ctrl + Shift + P**
2. A search box will appear at the top of the screen. Type **Git: Clone** and click the result that says **Git: Clone**
3. Another box will appear asking for a URL. Paste the following and press **Enter**:
   ```
   https://github.com/combinate-me/Executive-Assistant.git
   ```
4. A window will open asking where to save the folder. Choose a location you can find easily, such as your **Documents** folder. Click **Select Repository Location** (or **Select as Repository Destination** on Windows)
5. VS Code will download the files - this takes about 30 seconds
6. When it finishes, a pop-up will appear asking **"Would you like to open the cloned repository?"** - click **Open**

You should now see a list of files in the left panel, including files like `CLAUDE.md`, `SETUP.md`, and `.env.example`.

---

## Step 6: Set Up Your API Keys

API keys are passwords that allow the assistant to connect to tools like Teamwork and the Combinate intranet. You will need to create a personal settings file and fill these in.

**Create your settings file:**

1. In the left panel, find the file called **`.env.example`** and click on it to open it
2. You will see a list of settings, most of which already have values
3. Go to **File** in the top menu bar and click **Save As...**
4. In the filename box at the top, change `.env.example` to `.env` (just remove the word "example" and the dot before it, so it reads exactly `.env`)
5. Make sure the save location is still the **Combinate-Assistant** folder (it should be by default)
6. Click **Save**

The new `.env` file will now appear in the left panel.

**Fill in your keys:**

7. Click on `.env` in the left panel to open it
8. Find the lines that have nothing after the `=` sign - these are the ones you need to fill in. For example:
   ```
   TEAMWORK_API_KEY=
   ```
   becomes:
   ```
   TEAMWORK_API_KEY=your_key_here
   ```
9. Fill in the following keys:

| Key | How to get it |
|-----|--------------|
| `TEAMWORK_API_KEY` | Log in to Teamwork > click your profile picture > Edit Profile > API & Mobile > copy your API token |
| `COMBINATE_INTRANET_KEY` | Log in to the Combinate intranet > Integrations > Insites API Key |
| `COMBINATE_INTRANET_ADMIN_UUID` | Log in to the Combinate intranet > CRM > find your own contact record > the UUID is in the URL bar (the long string of letters and numbers at the end of the address) |

The other lines (URLs and site addresses) are already filled in and do not need to be changed.

10. When you have filled in your keys, press **Cmd + S** (Mac) or **Ctrl + S** (Windows) to save the file

> **Important:** Never share your `.env` file with anyone or attach it to an email. It contains your personal API keys. It is automatically excluded from any git updates so it will never be uploaded to GitHub.

---

## Step 7: Launch the Assistant

1. In VS Code, click **Terminal** in the top menu bar, then click **New Terminal**
2. A panel will open at the bottom of the screen
3. Click inside the panel and type the following, then press **Enter**:
   ```
   claude
   ```
4. The assistant will start up. The first time may take a moment to load.
5. Once you see a prompt (a blinking cursor or input box), type the following and press **Enter**:
   ```
   Set me up
   ```
6. The assistant will ask you a few questions about your name, role, and current priorities. Answer each one and press Enter. This takes about 2 minutes.

When it is done, you are set up and ready to use the Combinate Assistant.

---

## Using the Assistant Day-to-Day

Each time you want to use the assistant:

1. Open **VS Code**
2. If the Combinate-Assistant folder is not already open, go to **File > Open Folder** and select the **Combinate-Assistant** folder
3. Open the terminal: **Terminal > New Terminal**
4. Type `claude` and press **Enter**

---

## Keeping Up to Date

Shane regularly updates the shared files (context, skills, and settings). To get the latest updates:

1. Open VS Code with the Combinate-Assistant folder open
2. Open the terminal and type the following, then press **Enter**:
   ```
   git pull
   ```

Your personal files (`.env`, `context/me.md`, `context/current-priorities.md`) will never be overwritten by an update.

---

## What Gets Shared vs What Stays Private

| File | Shared with the team | Private to you |
|------|---------------------|----------------|
| `context/work.md` | Yes | |
| `context/team.md` | Yes | |
| `context/goals.md` | Yes | |
| `context/me.md` | | Yes - created during setup |
| `context/current-priorities.md` | | Yes - created during setup |
| `.env` | | Yes - your API keys, never shared |
| `CLAUDE.local.md` | | Yes - personal preferences |

---

## Getting Help

If you get stuck at any point, ask Shane.
