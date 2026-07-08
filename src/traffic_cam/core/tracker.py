import cv2
import numpy as np
import time
from traffic_cam.io_utils.camera import ThreadedCamera
from traffic_cam.logging_config import get_logger
from traffic_cam.ui.interactive import UIHandler
from traffic_cam.core.metrics import MetricsTracker

logger = get_logger("tracker")


def run_tracking_pipeline(args, main_logger):
    camera = ThreadedCamera(src=args.source, target_width=args.width, target_height=args.height).start()
    time.sleep(0.5)

    orb = cv2.ORB_create(nfeatures=args.features)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    mask = None
    if args.mask:
        mask = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE)
        if mask is not None:
            mask = cv2.resize(mask, (camera.width, camera.height))
            logger.info(f"Маска {args.mask} применена.")
        else:
            logger.warning("Не удалось загрузить маску!")

    window_name = 'TrafficCam Tracker'
    cv2.namedWindow(window_name)

    ui = UIHandler(window_name, target_points=args.points)
    cv2.setMouseCallback(window_name, ui.mouse_callback)
    metrics_tracker = MetricsTracker()

    ref_descriptors = None
    ref_keypoints = None
    initial_zone = None
    mode = 'preview'

    while True:
        metrics_tracker.start_loop()

        t0 = time.perf_counter()
        ret, frame = camera.read()
        fetch_time = (time.perf_counter() - t0) * 1000

        if not ret:
            logger.info("Поток данных завершен.")
            break

        current_metrics = {'Fetch': fetch_time, 'Analysis': 0.0, 'Compensate': 0.0, 'Render': 0.0}

        if mode == 'preview':
            cv2.putText(frame, "Aim & Press SPACE to lock ref", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255),
                        2)

            key = cv2.waitKey(30) & 0xFF
            if key == ord(' '):
                t1 = time.perf_counter()
                ref_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ref_keypoints, ref_descriptors = orb.detectAndCompute(ref_gray, mask)
                current_metrics['Analysis'] = (time.perf_counter() - t1) * 1000

                ui.frame_copy = frame.copy()
                mode = 'setup'
                logger.info(f"Эталон захвачен. Ожидается ввод {args.points} точек.")
            elif key == ord('q'):
                break

        elif mode == 'setup':
            frame = ui.frame_copy.copy()
            cv2.putText(frame, f"Click {args.points} points to set zone", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 0), 2)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

            if ui.setup_done:
                initial_zone = np.float32([ui.points])
                mode = 'tracking'

        elif mode == 'tracking':
            t1 = time.perf_counter()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            keypoints, descriptors = orb.detectAndCompute(gray_frame, mask)

            if descriptors is not None and len(descriptors) > 0 and ref_descriptors is not None:
                matches = bf.match(ref_descriptors, descriptors)
                matches = sorted(matches, key=lambda x: x.distance)
                good_matches = matches[:50]
            current_metrics['Analysis'] = (time.perf_counter() - t1) * 1000

            t2 = time.perf_counter()
            if 'good_matches' in locals() and len(good_matches) >= 4:
                src_pts = np.float32([ref_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if matrix is not None:
                    transformed_zone = cv2.perspectiveTransform(initial_zone, matrix)
                    cv2.polylines(frame, [np.int32(transformed_zone)], True, (0, 255, 0), 3)
            current_metrics['Compensate'] = (time.perf_counter() - t2) * 1000

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        t3 = time.perf_counter()
        metrics_tracker.update_and_draw(frame, current_metrics, mode)
        cv2.imshow(window_name, frame)
        current_metrics['Render'] = (time.perf_counter() - t3) * 1000

    camera.stop()
    metrics_tracker.close()
    cv2.destroyAllWindows()