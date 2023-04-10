import cv2

url = 0 # 'http://192.168.1.8:4747/video'

cap_camera = cv2.VideoCapture(url, cv2.CAP_V4L)

cap_camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)

while True:
    ret, frame = cap_camera.read()
    if not ret:
        print("Error: failed to capture frame")
        break

    cv2.imshow("IP STREAM VIDEO", frame)
    if cv2.waitKey(1) == ord("q"):
        break

cap_camera.release()
cv2.destroyAllWindows()
