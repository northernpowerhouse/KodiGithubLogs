# Quick Start Guide

## Installation (3 minutes)

### Step 1: Install the Repository
1. Download [repository.kodigithublogs.zip](https://github.com/northernpowerhouse/KodiGithubLogs/releases/latest)
2. In Kodi: **Add-ons** → **Install from zip file** → Select the zip
3. Wait for "Repository installed" notification

### Step 2: Install the Addon
1. **Add-ons** → **Install from repository**
2. **KodiGithubLogs Repository**
3. **Program add-ons** → **KodiGithubLogs**
4. Click **Install**

## First Use (5 minutes)

### Authorize in Kodi
1. Open **Kodi Log Uploader** (Programs)
2. Select **Authorize GitHub**
3. Visit the URL shown on screen
4. Enter the code displayed
5. Authorize the app in your browser
6. Return to Kodi (authorization completes automatically)

> **Note**: A default OAuth client_id is included, so no setup needed! Advanced users can create their own at https://github.com/settings/developers

### Upload Your First Log
1. Select **Select repository** → Choose a repo
2. Select **Select folder** → Navigate or create folder
3. Select **Upload logs now**
4. Done! Check GitHub to see your log file

## Settings

Access via main menu → **Settings**:

- **Log level**: regular (clean), debug (detailed), or trace (everything)
- **Include older logs**: Also include kodi.old rotated log file
- **Exclude startup logs**: Remove initialization/skin loading noise

## Tips

- Create a dedicated repo for logs (e.g., `username/kodi-logs`)
- Use folders to organize by date or device
- Regular logs are usually sufficient; use debug/trace only when troubleshooting
- Exclude startup logs to focus on runtime issues
- Revoke tokens when done: https://github.com/settings/tokens

## Support

- Issues: https://github.com/northernpowerhouse/KodiGithubLogs/issues
- Source: https://github.com/northernpowerhouse/KodiGithubLogs
