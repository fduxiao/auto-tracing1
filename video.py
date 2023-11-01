import cv2


class VideoCapture:
    def __init__(self, device=None, api_preference=cv2.CAP_ANY):
        if not isinstance(device, int):
            device = str(device)
        self.device = device
        self.cap = cv2.VideoCapture()

        if device is not None:
            self.open(device, api_preference)

    def __repr__(self):
        return f"VideoCapture('{self.device}')"

    def open(self, device, api_reference):
        self.cap.open(device, api_reference)

    def release(self):
        self.cap.release()

    def set(self, width=None, height=None, fps=None, brightness=None, contrast=None, saturation=None,
            hue=None, exposure=None, fourcc=None):

        relation_map = {
            cv2.CAP_PROP_FRAME_WIDTH: width,
            cv2.CAP_PROP_FRAME_HEIGHT: height,
            cv2.CAP_PROP_FPS: fps,
            cv2.CAP_PROP_BRIGHTNESS: brightness,
            cv2.CAP_PROP_CONTRAST: contrast,
            cv2.CAP_PROP_SATURATION: saturation,
            cv2.CAP_PROP_HUE: hue,
            cv2.CAP_PROP_EXPOSURE: exposure,
            cv2.CAP_PROP_FOURCC: fourcc,
        }

        for key, value in relation_map.items():
            if value is not None:
                self.cap.set(key, value)
        return self

    @property
    def opened(self):
        return self.cap.isOpened()

    def read(self):
        """
        read a frame

        :return: (bool, np.ndarray)
        """
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
        return ret, frame
