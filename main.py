import cv2
from ultralytics import YOLO
import torch  # Make sure torch is imported
import socket
import time
import json
import serial
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

class DataServer:
    def __init__(self, host='0.0.0.0', port=5003):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.arduino = serial.Serial('/dev/ttyCH341USB0', 9600)

        # Initialize RealTimePredictor model
        self.predictor = RealTimePredictor()

        # Load initial training data from CSV
        csv_file = "posture.csv"
        data = pd.read_csv(csv_file)
        X_train = data[['Weight', 'Height', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15', 'A16']].values
        y_train = data['Posture_Number'].values

        # Train the model and scale the data
        self.predictor.train(X_train, y_train)
        self.predictor.scaler.fit(X_train)

        # Load YOLO model
        self.model = YOLO('models/basicv3.onnx')  # Ensure the path to your model is correct
        self.cap = cv2.VideoCapture(0)  # Open webcam
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            exit()

    def read_sensor_data(self):
        data = self.arduino.readline().decode('latin-1').strip()
        if data.startswith("<") and data.endswith(">"):
            data = data[1:-1]
            sensor_values = {}
            readings = data.split(";")
            for reading in readings:
                if reading:
                    sensor_id, value = reading.split(",")
                    sensor_values[sensor_id] = int(value)
            return sensor_values
        return None

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server started: {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Client connected: {client_address}")

            try:
                # Request weight and height from client upon first connection
                client_socket.sendall("Enter your weight and height.".encode('utf-8'))
                user_data = client_socket.recv(1024).decode('utf-8')
                user_info = json.loads(user_data)
                self.weight = float(user_info["weight"])
                self.height = float(user_info["height"])
                print(f"Received user weight: {self.weight}, height: {self.height}")

                while True:
                    sensor_data = self.read_sensor_data()
                    if sensor_data:
                        # Prepare data for prediction
                        sample_data = [
                            self.weight,
                            self.height,
                            *[sensor_data.get(f'A{i}', 0) for i in range(1, 17)]
                        ]
                        
                        # Predict posture
                        prediction = self.predictor.process_data(sample_data)[0]
                        
                        # Capture frame from webcam
                        ret, frame = self.cap.read()
                        if not ret:
                            print("Error: Failed to capture image")
                            break

                        # Perform inference with YOLO
                        results = self.model(frame)

                        # Reset class counts
                        bad_count = 0
                        good_count = 0

                        # Annotate the frame manually to avoid drawing low-confidence detections
                        annotated_frame = frame.copy()

                        # Iterate over each detection
                        for result in results:
                            for box in result.boxes:
                                if box.conf >= 0.85:  # Only consider detections with confidence >= 0.85

                                    # Ensure bounding box values are properly extracted from tensors
                                    bbox = box.xyxy
                                    if isinstance(bbox, torch.Tensor):
                                        bbox = bbox.squeeze().tolist()  # Convert tensor to list

                                    if len(bbox) == 4:
                                        x1, y1, x2, y2 = map(int, bbox)
                                    else:
                                        print(f"Unexpected bbox shape or size: {bbox}")
                                        continue  # Skip processing this box if not valid

                                    class_id = int(box.cls)
                                    class_name = result.names[class_id]

                                    # Count 'bad' and 'good' classes
                                    if class_name == 'bad':
                                        bad_count += 1
                                    elif class_name == 'good':
                                        good_count += 1

                                    # Convert box.conf tensor to a scalar for formatting
                                    confidence = box.conf.item() if isinstance(box.conf, torch.Tensor) else box.conf

                                    # Draw bounding box for high-confidence detections only
                                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                                    cv2.putText(annotated_frame, f'{class_name} {confidence:.2f}', (x1, y1 - 10),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                        # Determine the predicted posture based on conditions
                        if bad_count == 2:
                            predicted_posture = 10  # If bad_count is 2, send 10
                        elif bad_count == 1:
                            if prediction == 2:
                                predicted_posture = 2  # If bad_count is 1 and predicted posture is 2, send 2
                            elif prediction == 3:
                                predicted_posture = 3  # If bad_count is 1 and predicted posture is 3, send 3
                            else:
                                predicted_posture = prediction  # Otherwise, use the model prediction
                        else:
                            predicted_posture = prediction  # Default to model prediction if no special conditions
                        
                        # If sensor values are all in the range 0 to 50, set posture to 0
                        
                        if all(0 <= value <= 50 for value in sensor_data.values()):
                            predicted_posture = 0
                            display_text = "Posture: Invalid (No detection)"
                        else:
                            display_text = f"Posture: {predicted_posture}"
                        if predicted_posture != 0 and predicted_posture != 1 :
                                self.arduino.write(b'motor')  
                                print(predicted_posture)
                        # Display the message on the frame
                        text_color = (0, 0, 0)  # Default color (black)

                        if bad_count > 0 or good_count < 2:
                            display_text = "bad"
                            text_color = (0, 0, 255)  # Red color for "bad"
                        elif good_count >= 2:
                            display_text = "good"
                            text_color = (0, 255, 0)  # Green color for "good"
                        
                        # Show the resulting frame
                        cv2.putText(annotated_frame, display_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
                        cv2.imshow('YOLO Webcam Detection', annotated_frame)

                        # Send predicted posture to the client
                        data = {
                            "timestamp": time.time(),
                            "predicted_posture": int(predicted_posture),  # Send updated posture
                            "sensor_data": sensor_data
                        }
                        
                        message = json.dumps(data) + "\n"
                        client_socket.sendall(message.encode('utf-8'))
                        print(f"Sent: {message.strip()}")

            except Exception as e:
                print(f"Error: {e}")
            finally:
                client_socket.close()
                print("Connection closed")

    def close(self):
        self.arduino.close()
        self.server_socket.close()
        self.cap.release()  # Release the webcam
        cv2.destroyAllWindows()  # Close any OpenCV windows

class RealTimePredictor:
    def __init__(self):
        self.model = SGDClassifier(loss="log_loss")
        self.scaler = StandardScaler()
        self.is_model_trained = False

    def train(self, X, y):
        self.model.fit(X, y)
        self.is_model_trained = True

    def update_model(self, X, y):
        self.model.partial_fit(X, y, classes=[1, 2, 3, 4, 5, 6, 7])

    def predict(self, X):
        return self.model.predict(X)

    def process_data(self, feature_data):
        feature_data = [feature_data]
        feature_data = self.scaler.transform(feature_data)
        prediction = self.predict(feature_data)
        return prediction

        

if __name__ == "__main__":
    try:
        server = DataServer()
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.close()
