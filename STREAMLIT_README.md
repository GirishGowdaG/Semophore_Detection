# Semaphore Detection - Streamlit Version

## 🚀 Quick Start

The project has been converted to run with **Streamlit** for a modern, interactive web interface!

### Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

### Running the App

Run the Streamlit app using Python:
```bash
python -m streamlit run streamlit_app.py
```

Or if you have streamlit in your PATH:
```bash
streamlit run streamlit_app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

## 🎮 How to Use

1. **Start the app** - The Streamlit interface will load in your browser
2. **Configure camera** - Use the sidebar to select your camera index (try 0, 1, or 2 if default doesn't work)
3. **Start Camera** - Click the "Start Camera" button in the sidebar
4. **Hold poses** - Stand in front of the camera and hold semaphore poses
5. **Wait for detection** - Keep each pose steady for 1.5 seconds
6. **Watch the message** - Letters will be automatically added to the decoded message
7. **Clear message** - Use the "Clear Message" button to start over

## ✨ Features

- **Real-time video processing** with MediaPipe pose detection
- **Live angle display** showing left and right arm angles
- **Progress indicator** while holding a pose
- **Decoded message display** with running text
- **Easy camera control** with start/stop buttons
- **Adjustable camera index** for multiple camera setups
- **Clean, modern UI** built with Streamlit

## 📱 Interface Layout

- **Left Panel**: Live camera feed with angle overlays
- **Right Panel**: 
  - Current arm angles (left and right)
  - Decoded message display
- **Sidebar**: 
  - Camera controls (start/stop)
  - Camera index selector
  - Clear message button
  - Usage instructions

## 🎯 Semaphore Positions

The app recognizes standard naval semaphore positions for letters A-Z and space. Hold your arms in the correct positions and keep steady for 1.5 seconds to register each letter.

## 🔧 Troubleshooting

### Camera not working?
- Try different camera indices (0, 1, 2) in the sidebar
- Make sure no other application is using the camera
- Check that your camera permissions are enabled

### Poor detection?
- Ensure good lighting
- Keep your full body visible in frame
- Stand at a reasonable distance from the camera
- Wear contrasting clothing

### App won't start?
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher
- Try running with: `python -m streamlit run streamlit_app.py`

## 📝 Technical Details

- **Framework**: Streamlit
- **Pose Detection**: MediaPipe
- **Computer Vision**: OpenCV
- **Processing**: NumPy
- **Python Version**: 3.8+

## 🆚 Original Flask Version

The original Flask-based version is still available in `app.py` if you prefer the Flask implementation. The Streamlit version provides a more modern interface with easier deployment and better user experience.

## 🙏 Credits

Original project by Rahul Mirji (@rahul__mirji)
Streamlit conversion completed for improved usability and modern web interface.
