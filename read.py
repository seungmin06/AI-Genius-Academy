import serial
import csv
import keyboard
import time
import os

arduino = serial.Serial('/dev/ttyCH341USB0', 9600, timeout=1)

csv_file_path = './posture.csv'
file_exists = os.path.isfile(csv_file_path)

weight = input("몸무게 (kg): ")
height = input("키 (cm): ")
posture_number = 1

saving_enabled = False  

def save_to_csv(sensor_data, weight, posture_number):
    global file_exists
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            headers = ['Weight', 'Height', 'Posture_Number'] + list(sensor_data.keys())
            writer.writerow(headers)
            file_exists = True

        row = [weight, height, posture_number] + list(sensor_data.values())
        writer.writerow(row)

def read_sensor_data():
    data = arduino.readline().decode('latin-1').strip()
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

print("토글 / 누르기 : s 저장")
print("누르기 : n 자세 바꾸기")
print("q 나가기")

while True:
    sensor_data = read_sensor_data()

    if sensor_data:
        print(f"Posture: {posture_number}, Sensor Data: {sensor_data}")

        if keyboard.is_pressed('s'):
            if not saving_enabled:
                saving_enabled = True
                print("데이터 저장시작")
            else:
                saving_enabled = False
                print("데이터 저장끝")
            time.sleep(0.5)  

        if keyboard.is_pressed('n'):
            posture_number += 1
            print(f"현재포즈 번호 {posture_number}")
            time.sleep(0.5) 

        if keyboard.is_pressed('q'):
            print("끝내는중")
            break

        if saving_enabled:
            save_to_csv(sensor_data, weight, posture_number)

    time.sleep(0.1) 