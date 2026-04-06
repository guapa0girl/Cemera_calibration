import cv2 as cv
import numpy as np

# 체스판 설정 (가로 칸 수 - 1, 세로 칸 수 - 1)
# 보통 A4 출력용은 9x6 또는 7x10 등 다양하니 본인의 출력물에 맞게 수정하세요.
CHESSBOARD_SIZE = (9, 6) 
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 3D 실제 좌표 준비 (0,0,0), (1,0,0), ..., (8,5,0)
objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)

objpoints = [] # 실제 세계의 3D 점
imgpoints = [] # 이미지 상의 2D 점

cap = cv.VideoCapture(0)

print("Space: 이미지 캡처 (최소 10-20장 필요), ESC: 종료 및 계산")

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv.flip(frame, 1) # 거울 모드
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # 체스판 코너 찾기
    ret_chess, corners = cv.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

    display_frame = frame.copy()
    if ret_chess:
        # 코너 정밀화 및 그리기
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        cv.drawChessboardCorners(display_frame, CHESSBOARD_SIZE, corners2, ret_chess)

    cv.imshow('Calibration - Capture', display_frame)
    
    key = cv.waitKey(1) & 0xFF
    if key == 32 and ret_chess: # Space 바를 눌러 저장
        objpoints.append(objp)
        imgpoints.append(corners2)
        print(f"Captured! Total: {len(objpoints)}")
    elif key == 27: # ESC 종료
        break

cap.release()
cv.destroyAllWindows()

# 캘리브레이션 수행
if len(objpoints) > 10:
    print("Calculating calibration... please wait.")
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    # 결과 저장
    np.savez("calibration_data.npz", mtx=mtx, dist=dist)
    
    print("\n[Calibration Results]")
    print(f"RMS Error: {ret}")
    print(f"Camera Matrix (mtx):\n{mtx}")
    print(f"Distortion Coefficients (dist):\n{dist}")
    print("\nData saved to 'calibration_data.npz'")
else:
    print("Not enough images captured. Min 10 required.")