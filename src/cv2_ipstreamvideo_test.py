import platform
import cv2

url = 0 # 'http://192.168.1.8:4747/video'

if platform.system() == 'Linux':
    cap_camera = cv2.VideoCapture(url, cv2.CAP_V4L)
else: # Windows and others
    cap_camera = cv2.VideoCapture(url, cv2.CAP_ANY)

cap_camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)

while True:
    success, image = cap_camera.read()

    if not success:
        print("Error: failed to capture frame")
        break

    cv2.imshow("IP STREAM VIDEO", image)

    if cv2.waitKey(1) == ord("q"):
        break

cap_camera.release()
cv2.destroyAllWindows()
