import socket
import matplotlib.pyplot as plt
import time
from PIL import Image
import os

s = socket.socket()
s.bind(("0.0.0.0", 50505))

s.listen(100)
print("Waiting for image...")

conn, addr = s.accept()
print("Connected to:", addr)

# Start timer
start_time = time.time()

f = open("received.png", "wb")

total_size = 0

data = conn.recv(4096)

while data:
    f.write(data)
    total_size += len(data)
    data = conn.recv(4096)

# Stop timer
end_time = time.time()
elapsed_time = end_time - start_time

f.close()
conn.close()
s.close()

# Get image resolution
img = Image.open("received.png")
width, height = img.size

print("Image received")
print("-------------------------")
print("Total file size:", total_size, "bytes")
print("Total file size:", round(total_size / (1024 * 1024), 2), "MB")
print("Image resolution:", width, "x", height)
print("Time taken:", round(elapsed_time, 4), "seconds")

if elapsed_time > 0:
    speed = (total_size / (1024 * 1024)) / elapsed_time
    print("Average transfer speed:", round(speed, 2), "MB/s")

# Display image in Spyder
img = plt.imread("received.png")
plt.imshow(img)
plt.axis("off")
plt.show()
