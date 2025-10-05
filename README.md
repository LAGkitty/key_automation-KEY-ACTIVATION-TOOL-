
# Key Automation Tool

Automated character generation and key spamming tool for Windows, with a modern, compact UI and advanced timing controls.

## Features

### 🎯 Character Generation
- Letters (A-Z, a-z)
- Numbers (0-9)
- Symbols (!@#$%^&*()_+-=[]{}|;':",./<>?)
- Arrow Keys (↑↓←→)
- Custom Characters: define your own set
- Exclude Characters: remove specific characters

### 🎨 Formatting
- Add dashes or spaces every N characters
- Customizable frequency for both options
 - Advanced dash patterns: specify group tokens like `11-11111-1111` or literal tokens like `ABC-1111-XYZ`
 - Per-gap entries: enable one text box per gap and type literal values for each gap (when enabled, the "Characters per gap" control is ignored; use the Pattern field for numeric group sizes)

### 🗑️ Deletion
- Auto-delete: automatically delete after typing
- Character deletion: delete N characters with backspace
- Word deletion: use Ctrl+Backspace to delete whole words
- Configurable deletion count and timing

### ⚙️ Control Modes
- Hold Mode: press and hold activation key to run
- Toggle Mode: press once to start/stop
- Single Mode: press once to type a single sequence (auto-delete is disabled for single runs)
- Customizable activation key (F1-F12, Insert, Home, End, etc.)

### ⚡ Timing & Speed
- Typing speed slider: smooth logarithmic scale up to 10,000 cps
- Per-key delay and timing controls
- Pause between cycles and post-Enter delay
 - Note: very high cps values may be limited by the target application or OS; use the slider to find a stable speed.

### 🖱️ Other Features
- Real-time status monitoring
- Robust error handling

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python key_automation.py
   ```

2. Configure your settings in the tabbed interface:
   - Character Settings: choose which characters to generate
   - Formatting: set up dashes and spaces
   • Advanced: enable Advanced mode to use Pattern and Per-gap entries
   - Deletion: configure auto-deletion and timing
   - Timing: adjust per-key delay, typing speed, pause between cycles, and post-Enter delay
   - Controls: set activation mode and key binding

3. Use the activation key to start/stop the automation:
   - Hold Mode: hold the activation key to run
   - Toggle Mode: press once to start, press again to stop
   - Single Mode: press once to type a single sequence (auto-delete is disabled for single runs)

## Configuration

### Character Settings
- Enable/disable letters, numbers, symbols, and arrow keys
- Add custom characters
- Exclude specific characters

### Formatting
- Add dashes every N characters
- Add spaces every N characters
- Customize spacing frequency
 - Advanced Pattern Tokens:
    • Digit-only tokens are interpreted as numeric placeholders or counts. Example: `1111` → 4 placeholders, `4` → group size 4.
    • Tokens containing letters or symbols are treated as literal strings and will be inserted unchanged.
 - Per-gap Entries:
    • When enabled, a separate text box appears for each gap. Values typed into those boxes are used verbatim for that gap.
    • When Per-gap Entries is enabled, the "Characters per gap" spinner is ignored — put numeric group sizes in the Pattern field (e.g., `4-4-4`) if you need numeric placeholders.

### Deletion
- Auto-delete after typing
- Choose between character or word deletion
- Set deletion count and timing

### Timing
- Typing speed slider (logarithmic, up to 10,000 cps)
- Per-key delay
- Pause between cycles
- Post-Enter delay

### Controls
- Hold, Toggle, or Single mode
- Select activation key from dropdown

## Safety & Disclaimer

- Entertainment purposes only: This tool is designed for entertainment and demonstration purposes
- Configurable timing: All operations have adjustable delays to prevent system overload
- Error handling: Robust error handling prevents crashes
- Easy stop: Multiple ways to stop the automation

**Disclaimer:** This tool is created for entertainment and educational purposes only. Users are responsible for ensuring they comply with all applicable laws and terms of service of any software or games they use this tool with.
