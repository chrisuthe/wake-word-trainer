# GitHub Setup Instructions

## Pushing to GitHub

### 1. Create a New Repository on GitHub

1. Go to https://github.com/new
2. Enter repository name: `wake-word-trainer` (or your preferred name)
3. **Do NOT** initialize with README, .gitignore, or license (we already have these)
4. Make it **Public** (recommended for open source)
5. Click "Create repository"

### 2. Push Your Local Repository

After creating the GitHub repository, run these commands:

```bash
cd "C:\Users\chris\Downloads\wake-word-trainer-webapp\wake-word-trainer"

# Add GitHub as remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/wake-word-trainer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Verify on GitHub

Visit your repository URL:
```
https://github.com/YOUR_USERNAME/wake-word-trainer
```

You should see all your files, the README, and the MIT license!

## Post-Upload Tasks

### Update README Links

After uploading, update the placeholder URLs in README.md:

```markdown
# Change this:
https://github.com/yourusername/wake-word-trainer

# To:
https://github.com/YOUR_ACTUAL_USERNAME/wake-word-trainer
```

Commit and push the changes:

```bash
git add README.md
git commit -m "Update repository URLs in README"
git push
```

### Enable GitHub Features

1. **Discussions**: Go to Settings → Features → Enable Discussions
2. **Issues**: Already enabled by default
3. **Topics**: Add topics like:
   - `home-assistant`
   - `wake-word`
   - `esphome`
   - `tensorflow`
   - `pytorch`
   - `voice-assistant`
   - `microcontroller`
   - `esp32`

### Add Repository Description

In your GitHub repository page:
- Click on the ⚙️ gear icon next to "About"
- Description: "GPU-accelerated wake word trainer for Home Assistant and ESPHome devices"
- Website: (optional) Link to your Home Assistant instance or documentation
- Add topics as listed above
- Check "Releases" and "Packages" if needed
- Save changes

## Making Future Changes

### Workflow

```bash
# Make changes to your code
# ...

# Stage changes
git add .

# Commit with message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

### Creating Releases

When you're ready to create a release:

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: "v1.0.0 - Initial Release"
5. Description: List features and improvements
6. Click "Publish release"

## Optional: Add GitHub Actions

Create `.github/workflows/docker-build.yml` for automated Docker builds:

```yaml
name: Docker Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build Docker images
      run: docker-compose build
```

## Sharing Your Project

### Home Assistant Community

Share on:
- [Home Assistant Community Forum](https://community.home-assistant.io/)
- [ESPHome Discord](https://discord.gg/KhZZ9gcKpk)
- [/r/homeassistant subreddit](https://www.reddit.com/r/homeassistant/)

### Social Media

Post about it:
- Twitter/X with hashtags: #HomeAssistant #ESPHome #WakeWord
- LinkedIn for technical audience
- Dev.to or Hashnode for technical blog post

## Support

If you need help:
- Check GitHub [docs on creating repositories](https://docs.github.com/en/get-started/quickstart/create-a-repo)
- See [pushing to GitHub](https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository)

---

Good luck with your project! 🚀
