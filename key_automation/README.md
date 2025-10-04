# Key Automation Tool

A comprehensive Python application for automated key spamming and character generation, designed for entertainment purposes.

## Features

### 🎯 Character Generation
- **Letters**: A-Z, a-z
- **Numbers**: 0-9
- **Symbols**: !@#$%^&*()_+-=[]{}|;':",./<>?
- **Arrow Keys**: ↑↓←→
- **Custom Characters**: Define your own character set
- **Exclude Characters**: Remove specific characters from generation

### 🎨 Formatting Options
- **Dashes**: Add dashes every N characters
- **Spaces**: Add spaces every N characters
- **Customizable frequency** for both options

### 🗑️ Deletion Features
- **Auto-delete**: Automatically delete after typing
- **Character deletion**: Delete N characters with backspace
- **Word deletion**: Use Ctrl+Backspace to delete entire words
- **Configurable deletion count** and timing

### ⚙️ Control Modes
- **Hold Mode**: Press and hold activation key to run
- **Toggle Mode**: Press once to start/stop
- **Customizable activation key** (F1-F12, Ctrl, Alt, Shift, etc.)

### 🎮 Advanced Features
- **Visual keyboard layout** window
- **Retry cycles**: Automatically restart after N operations
- **Timing controls**: Adjustable delays for all operations
- **Real-time status** monitoring

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
   - **Character Settings**: Choose which characters to generate
   - **Formatting**: Set up dashes and spaces
   - **Deletion & Timing**: Configure auto-deletion and timing
   - **Controls**: Set activation mode and key binding

3. Use the activation key to start/stop the automation:
   - **Hold Mode**: Hold the activation key to run
   - **Toggle Mode**: Press once to start, press again to stop

## Configuration

### Character Settings
- Enable/disable letters, numbers, symbols, and arrow keys
- Add custom characters
- Exclude specific characters

### Formatting
- Add dashes every N characters
- Add spaces every N characters
- Customize spacing frequency

### Deletion Options
- Auto-delete after typing
- Choose between character or word deletion
- Set deletion count and timing
- Configure retry cycles

### Controls
- Choose between hold or toggle mode
- Select activation key from dropdown
- View keyboard layout for reference

## Safety Features

- **Entertainment purposes only**: This tool is designed for entertainment and demonstration purposes
- **Configurable timing**: All operations have adjustable delays to prevent system overload
- **Error handling**: Robust error handling prevents crashes
- **Easy stop**: Multiple ways to stop the automation

## Technical Details

- Built with Python tkinter for the GUI
- Uses pyautogui for key simulation
- pynput for global key listening
- Threading for non-blocking automation
- Cross-platform compatibility

## Disclaimer

This tool is created for entertainment and educational purposes only. Users are responsible for ensuring they comply with all applicable laws and terms of service of any software or games they use this tool with.
