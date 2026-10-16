import serial
import time

# Set up serial communication
arduino_port = "COM7"  # Replace with your Arduino's port
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except serial.SerialException:
    print("Error: Could not open port.")
    exit()

def read_sensor_data():
    try:
        line = ser.readline().decode('utf-8').strip()  # Read a line from the serial port
        sensor_values = [int(value) for value in line.split(",")]  # Parse values
        return sensor_values
    except (ValueError, IndexError):
        return None

# Main loop
try:
    while True:
        data = read_sensor_data()
        if data:
            print("Sensor Values:", data)
        time.sleep(1)  # Adjust the delay as needed
except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
