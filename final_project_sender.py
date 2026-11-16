import socket
import time
import os

s = socket.socket()

# Insert other person's IP address, then 50505
s.connect(("[address]", 50505))

filename = "wentworth_leopard.jpg"
f = open(filename, "rb")

# Get total file size
file_size = os.path.getsize(filename)

# Start timer
start_time = time.time()

data = f.read(4096)

while data:
    s.sendall(data)
    data = f.read(4096)

# Stop timer
end_time = time.time()
elapsed_time = end_time - start_time

f.close()
s.close()

print("Image sent")
print("-------------------------")
print("Total file size:", file_size, "bytes")
print("Total file size:", round(file_size / (1024 * 1024), 2), "MB")
print("Time taken:", round(elapsed_time, 4), "seconds")

if elapsed_time > 0:
    speed = (file_size / (1024 * 1024)) / elapsed_time
    print("Average transfer speed:", round(speed, 2), "MB/s")
