import socket

s = socket.socket()

# insert other persons ip address, then 50505
s.connect(("10.220.28.242", 50505))

f = open("wentworth_leopard.png", "rb")

data = f.read(4096)

while data:
        s.sendall(data)
        data = f.read(4096)
        
f.close()
s.close()

print("image sent")