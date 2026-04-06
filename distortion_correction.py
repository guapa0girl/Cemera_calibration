import cv2 as cv
import numpy as np

# 1. 데이터 로드
try:
    data = np.load("calibration_data.npz")
    mtx = data['mtx']
    dist = data['dist']
except:
    print("Calibration data not found. Run camera_calibration.py first.")
    exit()

cap = cv.VideoCapture(0)
w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

# 최적의 카메라 매트릭스 계산 (왜곡 보정 후 잘림 방지)
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# 비디오 저장 설정
fourcc = cv.VideoWriter_fourcc(*'mp4v')
out = cv.VideoWriter('corrected_video.mp4', fourcc, 20.0, (w * 2, h)) # 원본+보정본 가로 배치

print("Recording... Press ESC to stop.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv.flip(frame, 1)

    # 2. 왜곡 보정 수행
    undistorted = cv.undistort(frame, mtx, dist, None, newcameramtx)

    # (선택) ROI에 맞게 자르기
    # x, y, w_roi, h_roi = roi
    # undistorted = undistorted[y:y+h_roi, x:x+w_roi]
    # undistorted = cv2.resize(undistorted, (w, h))

    # 비교를 위해 원본과 보정본을 가로로 결합
    combined = np.hstack((frame, undistorted))
    
    # 가이드 텍스트
    cv.putText(combined, "Original", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv.putText(combined, "Undistorted", (w + 10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv.imshow("Lens Distortion Correction", combined)
    out.write(combined)

    if cv.waitKey(1) & 0xFF == 27:
        break

cap.release()
out.release()
cv.destroyAllWindows()