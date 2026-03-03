# Demo Guide

This guide explains how to create compelling demos, videos, and GIFs for the LLM Red Teaming Platform.

## Table of Contents

1. [Quick Demo Scenarios](#quick-demo-scenarios)
2. [Creating Screen Recordings](#creating-screen-recordings)
3. [Making GIFs](#making-gifs)
4. [Demo Script Templates](#demo-script-templates)
5. [Best Practices](#best-practices)
6. [Sample Screenshots](#sample-screenshots)

## Quick Demo Scenarios

### Scenario 1: Basic Vulnerability Scan (2 minutes)

**Objective**: Show how to run a simple red team scan

**Steps**:
1. Launch application: `streamlit run app.py`
2. Navigate to **Configure** page
3. Select models:
   - Target: `gpt-4`
   - Attacker: `gpt-3.5-turbo`
4. Go to **Attack Lab** page
5. Select vulnerabilities:
   - ✅ Robustness
   - ✅ Jailbreak
6. Set "Attacks Per Vulnerability": 3
7. Click **Run Red Team Scan**
8. Show progress indicators
9. Navigate to **Results** page
10. Display scan metrics and test cases
11. Generate PDF report

**Key Points to Highlight**:
- Easy configuration
- Real-time progress monitoring
- Clear results presentation
- Professional PDF reports

### Scenario 2: Custom Attack Testing (3 minutes)

**Objective**: Demonstrate custom prompt testing

**Steps**:
1. Navigate to **Custom Attack** tab
2. Select vulnerability type: "Jailbreak"
3. Choose jailbreak strategy: "DAN (Do Anything Now)"
4. Enter target model: `gpt-4`
5. Click **Execute Custom Attack**
6. Show real-time response
7. Display vulnerability score
8. Demonstrate different strategies

**Key Points to Highlight**:
- Flexible custom testing
- Multiple jailbreak strategies
- Immediate feedback
- Score interpretation

### Scenario 3: Static Attack Library (90 seconds)

**Objective**: Show pre-built attack library

**Steps**:
1. Go to **Static Attack** tab
2. Browse attack categories
3. Select "Ignore Previous Instructions"
4. Run against target model
5. Show response and analysis
6. Try different prompts from library

**Key Points to Highlight**:
- Ready-to-use attack prompts
- Organized by category
- Quick testing capability

## Creating Screen Recordings

### Recommended Tools

#### Windows
- **OBS Studio** (Free)
  - Download: https://obsproject.com/
  - Best for: Full-featured recordings
  
- **ShareX** (Free)
  - Download: https://getsharex.com/
  - Best for: Quick captures

- **Camtasia** (Paid)
  - Professional editing features
  - Best for: Polished demos

#### macOS
- **QuickTime Player** (Built-in)
  - Screen Recording feature
  
- **ScreenFlow** (Paid)
  - Professional quality

#### Linux
- **OBS Studio**
- **SimpleScreenRecorder**
- **Kazam**

### Recording Settings

```
Resolution: 1920x1080 (1080p)
Frame Rate: 30 FPS
Bitrate: 5000-8000 kbps
Audio: 128 kbps (if narrating)
Format: MP4 (H.264)
```

### Recording Tips

1. **Prepare Your Environment**
   ```bash
   # Clean logs
   rm logs/*.log
   
   # Reset database (optional)
   rm red_teaming.db
   python migrate_db.py
   
   # Set up demo API keys
   export OPENAI_API_KEY=demo_key
   ```

2. **Browser/Window Setup**
   - Close unnecessary tabs
   - Hide personal information
   - Use incognito/private mode
   - Disable notifications
   - Set zoom to 100%

3. **Smooth Performance**
   - Close background applications
   - Use a local development environment
   - Pre-warm the application
   - Have example data ready

## Making GIFs

### Tools

- **ScreenToGif** (Windows) - https://www.screentogif.com/
- **GIPHY Capture** (macOS) - Free on App Store
- **Peek** (Linux) - https://github.com/phw/peek

### GIF Best Practices

```
Dimensions: 800x600 or 1024x768
Frame Rate: 15-20 FPS
Duration: 5-15 seconds max
File Size: < 10 MB
Colors: Optimized palette
```

### Converting Video to GIF

#### Using FFmpeg
```bash
# Install FFmpeg
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: apt-get install ffmpeg

# Convert with optimization
ffmpeg -i demo.mp4 -vf "fps=15,scale=800:-1:flags=lanczos" \
  -c:v gif demo.gif

# Add subtitles
ffmpeg -i demo.mp4 -vf "fps=15,scale=800:-1:flags=lanczos,\
  drawtext=text='Running vulnerability scan':fontcolor=white:\
  fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)-50" \
  -c:v gif demo_subtitle.gif
```

#### Using GIPHY
1. Upload video to https://giphy.com/create/gifmaker
2. Trim to 5-15 seconds
3. Add captions if needed
4. Download optimized GIF

### GIF Ideas

1. **scan-execution.gif**
   - Show scan starting and completing
   - Display progress bar
   - Caption: "Running red team scan in 10 seconds"

2. **results-view.gif**
   - Navigate through results
   - Highlight key metrics
   - Caption: "View detailed test results"

3. **custom-attack.gif**
   - Execute custom attack
   - Show response
   - Caption: "Test custom jailbreak prompts"

4. **pdf-report.gif**
   - Generate and preview report
   - Caption: "Professional PDF reports"

## Demo Script Templates

### Script 1: Product Demo (5 minutes)

```markdown
# LLM Red Teaming Platform Demo

## Opening (30 seconds)
"Hi, I'm going to show you the LLM Red Teaming Platform, 
a security testing tool for Large Language Models."

## Problem Statement (30 seconds)
"LLMs are vulnerable to attacks like jailbreaks, prompt 
injections, and adversarial prompts. Testing these manually 
is time-consuming and inconsistent."

## Solution Overview (1 minute)
"Our platform automates security testing by:
- Generating adversarial attacks
- Testing multiple vulnerability types
- Providing detailed reports
- Supporting all major LLM providers"

## Live Demo (2 minutes)
1. "Let's start by configuring our test..."
2. "I'll select GPT-4 as the target model..."
3. "And choose several vulnerability types..."
4. "Watch as it runs 30 different attacks..."
5. "The results show which attacks succeeded..."

## Results & Reports (1 minute)
"We can see:
- Overall security score
- Individual test results
- Attack prompts and responses
- Professional PDF reports for stakeholders"

## Closing (30 seconds)
"The platform helps security teams identify vulnerabilities 
before deployment. It's open-source and available on GitHub."
```

### Script 2: Technical Walkthrough (10 minutes)

```markdown
# Technical Deep Dive

## Architecture (2 minutes)
- Show architecture diagram
- Explain component interaction
- Discuss technology stack

## Configuration (2 minutes)
- Environment setup
- API key management
- Provider configuration

## Running Tests (3 minutes)
- Vulnerability selection
- Attack configuration
- Execution and monitoring

## Results Analysis (2 minutes)
- Interpreting scores
- Understanding failures
- Reviewing attack prompts

## Customization (1 minute)
- Custom attacks
- Integration possibilities
- Extension points
```

## Best Practices

### Visual Quality

✅ **Do**:
- Use high-resolution screen capture
- Maintain consistent window sizing
- Use clear, readable fonts
- Highlight important UI elements
- Add annotations for clarity

❌ **Don't**:
- Record at odd resolutions
- Show cluttered desktop
- Use tiny fonts
- Include personal data
- Skip setup context

### Narration Tips

1. **Speak Clearly**
   - Moderate pace (not too fast)
   - Avoid filler words ("um", "uh")
   - Pause between sections

2. **Explain Actions**
   ```
   ❌ "I'll click here..."
   ✅ "I'll click 'Run Scan' to start the vulnerability test..."
   ```

3. **Provide Context**
   ```
   ❌ "Now we see the results..."
   ✅ "The results show 85% of attacks were blocked, 
       indicating good security..."
   ```

### Editing

1. **Trim Dead Time**
   - Remove long loading screens
   - Speed up repetitive actions
   - Cut mistakes and restarts

2. **Add Enhancements**
   - Highlight mouse cursor
   - Add zoom effects for details
   - Include text overlays
   - Background music (subtle)

3. **Professional Touches**
   - Intro/outro slides
   - Transitions between sections
   - Consistent branding
   - Call-to-action at end

## Sample Screenshots

### Must-Have Screenshots

Create these key screenshots for README and documentation:

1. **dashboard.png**
   - Main dashboard with overview metrics
   - Show multiple scans in history

2. **configuration.png**
   - Configure page with model selection
   - Display multiple providers

3. **attack-lab.png**
   - Attack Lab with vulnerability checkboxes
   - Show scan in progress

4. **results.png**
   - Results page with charts
   - Display test case details

5. **report-preview.png**
   - PDF report preview
   - Show professional formatting

6. **custom-attack.png**
   - Custom attack interface
   - Show strategy selection

### Screenshot Guidelines

```python
# Preparing for screenshots
1. Populate with realistic data
2. Use professional-looking model names
3. Include variety in results
4. Show both successes and failures
5. Ensure UI is polished
```

### Taking Screenshots

**Windows**: Win + Shift + S  
**macOS**: Cmd + Shift + 4  
**Linux**: Shift + PrtScn (or Screenshot tool)

### Optimizing Images

```bash
# Install ImageMagick
# Convert to PNG with optimization
convert screenshot.png -resize 1920x1080 -quality 90 optimized.png

# Add border
convert optimized.png -bordercolor "#333333" -border 2 final.png
```

## Publishing Demos

### GitHub README
```markdown
## Demo

![Demo](docs/demo/demo.gif)

### Features in Action

<table>
  <tr>
    <td><img src="docs/screenshots/dashboard.png" width="400"/></td>
    <td><img src="docs/screenshots/results.png" width="400"/></td>
  </tr>
  <tr>
    <td align="center">Dashboard</td>
    <td align="center">Results</td>
  </tr>
</table>
```

### YouTube
1. Upload to YouTube
2. Add timestamps in description
3. Create playlist for different demos
4. Enable closed captions

### Social Media
- Twitter: 2:20 max, optimized for mobile
- LinkedIn: Professional tone, 3-10 minutes
- Reddit: Direct, technical, community-friendly

## Demo Checklist

Before recording:
- [ ] Clean environment (no personal data)
- [ ] Test run-through
- [ ] Prepare script
- [ ] Check audio levels
- [ ] Close unnecessary applications
- [ ] Set appropriate window size
- [ ] Have demo data ready
- [ ] Test API connectivity

After recording:
- [ ] Review for errors
- [ ] Add annotations
- [ ] Include captions
- [ ] Optimize file size
- [ ] Test playback on different devices
- [ ] Add to documentation
- [ ] Share with team for feedback

---

**Last Updated**: February 2026

Need help creating demos? Check out the [Contributing Guidelines](CONTRIBUTING.md) or reach out to the team!
