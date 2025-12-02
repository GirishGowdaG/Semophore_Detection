import cv2

print("Testing camera indices...")
for i in range(5):
    print(f"\nTrying camera index {i}...")
    
    # Try different backends
    for backend_name, backend in [("DirectShow", cv2.CAP_DSHOW), 
                                   ("Media Foundation", cv2.CAP_MSMF),
                                   ("Default", cv2.CAP_ANY)]:
        try:
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"  ✓ SUCCESS with {backend_name}: Camera {i} works!")
                    print(f"    Resolution: {frame.shape[1]}x{frame.shape[0]}")
                    cap.release()
                    break
                else:
                    print(f"  × {backend_name}: Opened but cannot read frame")
                    cap.release()
            else:
                print(f"  × {backend_name}: Cannot open")
        except Exception as e:
            print(f"  × {backend_name}: Error - {e}")

print("\n\nTest complete!")
