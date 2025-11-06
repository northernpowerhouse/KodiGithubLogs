# Kodi Log Uploader (Kodi 21)

This is a Kodi addon (script) that reads Kodi logs and uploads them to a GitHub repository using the GitHub OAuth Device Authorization flow.

## Key Features

- ✅ Authorize using GitHub Device Flow (secure, no password needed)
- ✅ List repositories you have push access to and pick a target repo
- ✅ Navigate repository folders and choose the target folder
- ✅ **Create new folders** in the repository via the UI
- ✅ Upload logs named `kodilogYYYYMMDDHHMM.txt`
- ✅ Choose log level: **regular/debug/trace**
- ✅ Option to include older rotated logs (`kodi.old`)
- ✅ Option to **exclude startup logs** (filters initialization noise)
- ✅ Improved startup trimming with multi-pattern heuristics

## Installation

### Option 1: Install via Repository (Recommended)

1. Download the latest `repository.kodiloguploader.zip` from [Releases](https://github.com/northernpowerhouse/KodiGithubLogs/releases)
2. In Kodi: **Add-ons → Install from zip file** → Select the repository zip
3. Wait for the installation notification
4. Go to **Add-ons → Install from repository → Kodi Log Uploader Repository**
5. Select **Program add-ons → Kodi Log Uploader**
6. Click **Install**

### Option 2: Direct Installation

1. Download the latest `script.kodiloguploader-X.X.X.zip` from [Releases](https://github.com/northernpowerhouse/KodiGithubLogs/releases)
2. In Kodi: **Add-ons → Install from zip file** → Select the addon zip

## Setup & Usage

### 1. Authorize with GitHub

The addon includes a default GitHub OAuth App client_id, so you can start using it immediately:

1. Open the addon in Kodi (Programs → Kodi Log Uploader)
2. Select **Authorize GitHub**
3. Follow the on-screen instructions:
   - Visit the URL shown (e.g., https://github.com/login/device)
   - Enter the user code displayed
   - Authorize the app
4. The addon will automatically save the access token

> **Advanced**: If you prefer to use your own OAuth App, create one at https://github.com/settings/developers and enter the client_id in addon settings or update `FALLBACK_CLIENT_ID` in the code.

### 2. Select Repository and Folder

1. Select **Select repository** from the main menu
2. Choose a repository you have write access to
3. Select **Select folder** to navigate the repository
   - Use `. (select this folder)` to choose the current location
   - Use `+ (create new folder)` to create a new folder
   - Navigate into folders or use `.. (up)` to go back

### 3. Configure Log Options

1. Select **Settings** from the main menu
2. Configure:
   - **Log level**: regular (default), debug, or trace
   - **Include older rotated logs**: Include `kodi.old` log file
   - **Exclude startup logs**: Trim initialization/startup portion of logs

### 4. Upload Logs

1. Select **Upload logs now** from the main menu
2. The addon will:
   - Read the Kodi logs based on your settings
   - Filter by log level (regular/debug/trace)
   - Optionally trim startup logs
   - Upload to GitHub with filename `kodilogYYYYMMDDHHMM.txt`
3. You'll see a confirmation when the upload completes

## Log Level Filtering

- **Regular**: Filters out lines containing `DEBUG` or `TRACE` (clean log)
- **Debug**: Includes `DEBUG` lines, filters out `TRACE` (detailed troubleshooting)
- **Trace**: Includes all log lines (maximum verbosity)

## Startup Log Trimming

When "Exclude startup logs" is enabled, the addon uses multiple heuristics to detect where the main log content begins:

- Looks for "Starting Kodi", "Kodi started", "Welcome to Kodi"
- Detects "application successfully started", "initialization complete"
- Finds first user action or service start (EventServer, JSON-RPC)
- Fallback: Skips first 15% of log if very long (>200 lines)

This helps exclude skin loading, codec detection, controller initialization, etc.

## Development

### Building Locally

Use the provided build script:

```bash
./scripts/build.sh
```

This will:
- Create `build/script.kodiloguploader-X.X.X.zip`
- Create `build/repository.kodiloguploader.zip`
- Update `repo/addons.xml` and `repo/addons.xml.md5`

### Creating a Release

1. Update version in `addon.xml`
2. Run `./scripts/build.sh`
3. Commit changes:
   ```bash
   git add repo/ addon.xml
   git commit -m "Release v0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```
4. GitHub Actions will automatically create a release with the zip files

### GitHub Actions Workflow

The workflow (`.github/workflows/build.yml`) automatically:
- Builds the addon zip on every push to `main`
- Creates GitHub Releases when tags are pushed (or manually triggered)
- Updates the Kodi repository structure (`repo/addons.xml`, MD5)
- Commits repo updates back to the repository
- Uploads addon and repository zips as release assets

## Technical Details

### Dependencies

- **None!** Uses only Python standard library (works in Kodi's Python environment)

### Security Notes

- Access tokens are stored in Kodi addon settings (password field)
- This is **not a fully secure secret store** - tokens are readable by other addons/processes with access to Kodi settings
- Consider revoking tokens when no longer needed: https://github.com/settings/tokens
- The OAuth App client_id is not secret but should be managed carefully

### API Usage

- GitHub Device Authorization Flow: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#device-flow
- GitHub Contents API: https://docs.github.com/en/rest/repos/contents

## Limitations & Future Improvements

- ⚠️ Maximum file size: GitHub API limits file uploads to 100MB (logs are typically much smaller)
- ⚠️ Token storage is not encrypted in addon settings
- 💡 Potential: Add support for creating GitHub Gists instead of repo files
- 💡 Potential: Add support for pull request-based uploads
- 💡 Potential: Add compression option for very large logs
- 💡 Potential: Add scheduling/automatic upload options

## Contributing

Contributions welcome! Please open issues or pull requests on GitHub.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: https://github.com/northernpowerhouse/KodiGithubLogs/issues
- **Discussions**: https://github.com/northernpowerhouse/KodiGithubLogs/discussions

