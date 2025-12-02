import streamlit as st
import cv2
import numpy as np
import time
from collections import deque

# Try to import MediaPipe, handle if not available
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None

# Page configuration
st.set_page_config(
    page_title="Semaphore Recognition",
    page_icon="🪖",
    layout="wide"
)

# Initialize MediaPipe only if available
if MEDIAPIPE_AVAILABLE:
    @st.cache_resource
    def initialize_mediapipe():
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose()
        return mp_pose, pose

    mp_pose, pose = initialize_mediapipe()
else:
    st.error("⚠️ MediaPipe is not available. This app requires MediaPipe for pose detection, which is currently not compatible with the Python version on Streamlit Cloud. Please run this app locally for full functionality.")
    mp_pose = None
    pose = None

# Semaphore dictionary
semaphore_dict = {
    ((165, 175), (-145, -135)): 'A',
    ((165, 175), (-95, -85)): 'B',
    ((165, 175), (-45, -35)): 'C',
    ((165, 175), (-5, 5)): 'D',
    ((35, 45), (-175, -165)): 'E',
    ((85, 95), (-175, -165)): 'F',
    ((135, 145), (-175, -165)): 'G',
    ((-145, -135), (-95, -85)): 'H',
    ((-35, -25), (-145, -135)): 'I',
    ((85, 95), (-5, 5)): 'J',
    ((-5, 5), (-145, -135)): 'K',
    ((25, 35), (-145, -135)): 'L',
    ((85, 95), (-145, -135)): 'M',
    ((135, 145), (-145, -135)): 'N',
    ((-35, -25), (-95, -85)): 'O',
    ((-5, 5), (-95, -85)): 'P',
    ((25, 35), (-95, -85)): 'Q',
    ((85, 95), (-95, -85)): 'R',
    ((125, 135), (-95, -85)): 'S',
    ((-5, 5), (-35, -25)): 'T',
    ((25, 35), (-35, -25)): 'U',
    ((135, 145), (-5, 5)): 'V',
    ((85, 95), (45, 55)): 'W',
    ((135, 145), (55, 65)): 'X',
    ((85, 95), (25, 35)): 'Y',
    ((85, 95), (135, 145)): 'Z',
    ((-165, -165), (165, 165)): ' '
}

def calculate_shoulder_angle_signed(shoulder, wrist):
    """Calculate signed angle from vertical axis"""
    dx = wrist[0] - shoulder[0]
    dy = shoulder[1] - wrist[1]
    angle_rad = np.arctan2(dx, dy)
    angle_deg = np.degrees(angle_rad)
    return round(angle_deg)

def match_letter(l_angle, r_angle):
    """Match angle pair to letter based on range dictionary"""
    for (l_range, r_range), letter in semaphore_dict.items():
        if l_range[0] <= l_angle <= l_range[1] and r_range[0] <= r_angle <= r_range[1]:
            return letter
    return None

# Initialize session state
if 'decoded_message' not in st.session_state:
    st.session_state.decoded_message = ""
if 'camera_running' not in st.session_state:
    st.session_state.camera_running = False
if 'angle_buffer' not in st.session_state:
    st.session_state.angle_buffer = deque(maxlen=10)
if 'pose_hold_start' not in st.session_state:
    st.session_state.pose_hold_start = None
if 'last_letter' not in st.session_state:
    st.session_state.last_letter = None
if 'current_left_angle' not in st.session_state:
    st.session_state.current_left_angle = 0
if 'current_right_angle' not in st.session_state:
    st.session_state.current_right_angle = 0

# Title and description
st.title("🪖 Real-Time Semaphore Decoder")
st.markdown("**Decodes naval semaphore signals using body pose detection**")

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    
    camera_index = st.number_input("Camera Index", min_value=0, max_value=5, value=0, 
                                   help="Try different values (0, 1, 2) if camera doesn't work")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎥 Start Camera", disabled=st.session_state.camera_running, use_container_width=False):
            st.session_state.camera_running = True
            st.session_state.decoded_message = ""
            st.session_state.angle_buffer.clear()
            st.session_state.pose_hold_start = None
            st.session_state.last_letter = None
    
    with col2:
        if st.button("🛑 Stop Camera", disabled=not st.session_state.camera_running, use_container_width=False):
            st.session_state.camera_running = False
    
    if st.button("🗑️ Clear Message"):
        st.session_state.decoded_message = ""
        st.session_state.last_letter = None
    
    st.divider()
    st.header("Info")
    st.markdown("""
    **How to use:**
    1. Click 'Start Camera'
    2. Hold a semaphore pose
    3. Keep steady for 1.5 seconds
    4. Letter will be added to message
    
    **Tips:**
    - Stand in good lighting
    - Keep your full body visible
    - Hold poses steady
    """)

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Camera Feed")
    video_placeholder = st.empty()
    
with col2:
    st.subheader("Detection Info")
    angle_left_placeholder = st.empty()
    angle_right_placeholder = st.empty()
    st.divider()
    st.subheader("Decoded Message")
    message_placeholder = st.empty()

# Camera processing
if st.session_state.camera_running:
    try:
        # Try to open camera with different backends
        cap = None
        for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
            try:
                cap = cv2.VideoCapture(camera_index, backend)
                if cap.isOpened():
                    # Test if we can actually read a frame
                    ret, _ = cap.read()
                    if ret:
                        break
                    else:
                        cap.release()
                        cap = None
                else:
                    if cap:
                        cap.release()
                    cap = None
            except:
                if cap:
                    cap.release()
                cap = None
        
        if cap is None or not cap.isOpened():
            st.error(f"❌ Could not open camera at index {camera_index}. Try a different camera index (0, 1, or 2).")
            video_placeholder.error(f"Camera Error: Index {camera_index} not available")
            st.session_state.camera_running = False
        else:
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Continuous frame processing loop
            while st.session_state.camera_running:
                success, frame = cap.read()
                
                if not success:
                    st.error("❌ Failed to read from camera")
                    st.session_state.camera_running = False
                    break
                
                # Process frame
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
                
                if results.pose_landmarks:
                    lm = results.pose_landmarks.landmark
                    
                    # Get keypoints
                    ls = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                          lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    lw = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    rs = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    rw = [lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                          lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    
                    # Calculate angles
                    left_angle = calculate_shoulder_angle_signed(ls, lw)
                    right_angle = calculate_shoulder_angle_signed(rs, rw)
                    
                    st.session_state.current_left_angle = left_angle
                    st.session_state.current_right_angle = right_angle
                    
                    # Display angles on frame
                    cv2.putText(image, f"Left: {left_angle}°", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(image, f"Right: {right_angle}°", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Add to buffer
                    st.session_state.angle_buffer.append((left_angle, right_angle))
                    
                    # Check if angles are steady
                    if all(abs(a[0] - left_angle) < 8 and abs(a[1] - right_angle) < 8 
                           for a in st.session_state.angle_buffer):
                        if st.session_state.pose_hold_start is None:
                            st.session_state.pose_hold_start = time.time()
                        
                        hold_time = time.time() - st.session_state.pose_hold_start
                        
                        # Show hold progress
                        progress = min(hold_time / 1.5, 1.0)
                        cv2.putText(image, f"Hold: {progress*100:.0f}%", (10, 90),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        
                        if hold_time > 1.5:
                            letter = match_letter(left_angle, right_angle)
                            if letter and letter != st.session_state.last_letter:
                                st.session_state.decoded_message += letter
                                st.session_state.last_letter = letter
                    else:
                        st.session_state.pose_hold_start = None
                        st.session_state.last_letter = None
                
                # Display frame (update the same placeholder)
                video_placeholder.image(image, channels="RGB", use_container_width=True)
                
                # Update angle displays
                angle_left_placeholder.metric("Left Arm Angle", f"{st.session_state.current_left_angle}°")
                angle_right_placeholder.metric("Right Arm Angle", f"{st.session_state.current_right_angle}°")
                
                # Display decoded message
                if st.session_state.decoded_message:
                    message_placeholder.success(f"**{st.session_state.decoded_message}**")
                else:
                    message_placeholder.info("Hold a pose for 1.5 seconds to decode...")
                
                # Small delay for frame rate control
                time.sleep(0.03)  # ~30 FPS
            
            cap.release()
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.session_state.camera_running = False
else:
    video_placeholder.info("📹 Click 'Start Camera' in the sidebar to begin")
    angle_left_placeholder.metric("Left Arm Angle", "0°")
    angle_right_placeholder.metric("Right Arm Angle", "0°")
    if st.session_state.decoded_message:
        message_placeholder.success(f"**{st.session_state.decoded_message}**")
    else:
        message_placeholder.info("No message decoded yet")
