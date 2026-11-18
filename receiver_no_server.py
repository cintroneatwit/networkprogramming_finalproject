import os
import socket
import struct
import time
import matplotlib.pyplot as plt

PORT=50505 
FIXED_HEADER=12
CHUNK_SIZE=4096
SMALL_IMAGE=100000
SAVE_FOLDER=r"C:\PixDrop"

def receive_txt(connection, length):
    data=b""
    while len(data)<length:
        piece=connection.recv(length-len(data))
        if piece==b"":
            return False
        data+=piece
    return data


def get_path(filename):
    name, extension=os.path.splitext(filename)
    path=os.path.join(SAVE_FOLDER, filename)
    number=2
    while os.path.exists(path):
        path=os.path.join(SAVE_FOLDER, name+" ("+str(number)+")"+extension)
        number=number+1
    return path


def receive_image(connection, filename, size):
    path=get_path(filename)
    received=0
    start=time.time()

    file=open(path, "wb")
    while received<size:
        amount=min(CHUNK_SIZE, size-received)
        piece=connection.recv(amount)
        if piece==b"":
            file.close()
            print("  The sender disconnected in the middle of "+filename)
            return False
        file.write(piece)
        received=received+len(piece)
        print("  "+str(received*100//size)+"%", end="\r")
    file.close()

    seconds=time.time()-start
    speed=0
    if seconds>0 and size>SMALL_IMAGE:
        speed=size/1024/1024/seconds
    speed_text="-"
    if speed>0:
        speed_text=f"{speed:.2f} MB/s"
    print(f"  Saved {os.path.basename(path)}, {size:,}, "
          f"{seconds:.2f} s, {speed_text}")
    return path

def plot(path,filename):
    try:
        plt.imshow(plt.imread(path))
        plt.axis("off")
        plt.show()
    except Exception:
        print("Can't show a preview of "+filename)


def handler(connection):
    count=0
    total=0
    start=time.time()
    while True:
        fixed=receive_txt(connection, FIXED_HEADER)
        if fixed is False:
            break
        name_length, message_length, size=struct.unpack(">HHQ", fixed)
        if name_length==0:
            connection.sendall(struct.pack(">I", count))
            break

        name_bytes=receive_txt(connection, name_length)
        message_bytes=receive_txt(connection, message_length)
        if name_bytes is False or message_bytes is False:
            break
        filename=name_bytes.decode()
        message=message_bytes.decode()
        if message!="":
            print("\nMessage: "+message)

        print("Receiving "+filename)
        path=receive_image(connection, filename, size)
        if path is False:
            break
        count=count+1
        total=total+size
        plot(path,filename)

    seconds=time.time()-start
    megabytes=total/1024/1024
    print(f"Finished: {count} images, {megabytes:.2f} MB in {seconds:.2f} s\n")


def main():
    print("PixDrop Receiver")
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen()
    print("Your IP: "+socket.gethostbyname(socket.gethostname()))
    print("Waiting for a sender on port "+str(PORT))
    print("Saving images to "+SAVE_FOLDER)

    while True:
        connection, address=server.accept()
        print("\nConnected to "+address[0])
        try:
            handler(connection)
        except (OSError, ValueError) as error:
            print("Transfer stopped: "+str(error))
        connection.close()


main()