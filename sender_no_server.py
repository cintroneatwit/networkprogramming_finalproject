import os
import socket
import struct
import time
PORT=50505
CHUNK_SIZE=4096
IMAGE_TYPES=(".jpg", ".jpeg", ".png")
SMALL_IMAGE=100000

#follow the path and save images in a list
def find(path):
    images=[]
    if os.path.isfile(path):#is there a file here(or folder)
        if path.lower().endswith(IMAGE_TYPES):
            images.append(path)
    else:
        for name in os.listdir(path):#go through files in folder
            if name.lower().endswith(IMAGE_TYPES):
                images.append(os.path.join(path, name))
    return images

#make each image header like DNS header lab
def header(filename, size, message):
    name_bytes=filename.encode()
    message_bytes=message.encode()
    header=struct.pack(">HHQ", len(name_bytes), len(message_bytes), size)
    return header+name_bytes+message_bytes#include lengths to sort through header

#recieve confirmation messages
def receive(connection, length):
    data=b""
    while len(data)<length:
        piece=connection.recv(length-len(data))
        if piece==b"":
            return False  # The receiver closed the connection
        data+=piece
    return data

#send image in chunks
def send_image(connection, path, message):
    filename=os.path.basename(path)
    size=os.path.getsize(path)
    connection.sendall(header(filename, size, message))

    amount=0
    start=time.time()
    file=open(path, "rb")
    while True:
        chunk=file.read(CHUNK_SIZE)
        if chunk==b"":#empty chunk, end loop
            break
        connection.sendall(chunk)
        amount+=len(chunk)
        print("  "+str(amount*100//size)+"%", end="\r")#percent done
    file.close()

    seconds=time.time()-start
    speed=0
    if seconds>0 and size>SMALL_IMAGE:
        speed=size/1024/1024/seconds
    speed_text="-"
    if speed>0:
        speed_text=f"{speed:.2f} MB/s"
    print(f"  Sent {filename}, {size:,} bytes, {seconds:.2f} s, {speed_text}")
    return size, speed


def summary(results):
    if len(results)==0:
        return
    largest=results[0]
    smallest=results[0]
    for image in results:
        if image["size"]>largest["size"]:
            largest=image
        if image["size"]<smallest["size"]:
            smallest=image
    print(f"Largest:  {largest['name']} ({largest['size']/1024/1024:.2f} MB)")
    print(f"Smallest: {smallest['name']} ({smallest['size']/1024/1024:.2f} MB)")

    timed=[]
    for image in results:
        if image["speed"]>0:
            timed.append(image)
    if len(timed)==0:
        return
    fastest=timed[0]
    slowest=timed[0]
    for image in timed:
        if image["speed"]>fastest["speed"]:
            fastest=image
        if image["speed"]<slowest["speed"]:
            slowest=image
    print(f"Fastest:  {fastest['name']} ({fastest['speed']:.2f} MB/s)")
    print(f"Slowest:  {slowest['name']} ({slowest['speed']:.2f} MB/s)")

#send multiple images with connection
def send_images(ip, images, message):
    count=0
    total=0
    results=[]  # Stats of images
    start=time.time()
    connection=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(10)

    try:
        connection.connect((ip, PORT))
        print("Connected to "+ip)
        for path in images:
            print("Sending "+os.path.basename(path))
            size, speed=send_image(connection, path, message)
            message=""  # Only send the message with first image
            results.append({"name": os.path.basename(path), "size": size, "speed": speed})

        connection.sendall(struct.pack(">HHQ", 0, 0, 0))  # End header
        connection.settimeout(60)  #Extra time to save big files
        reply=receive(connection, 4)  #amount of images
        if reply is False:
            print("No confirmation from receiver")
        else:
            count=struct.unpack(">I", reply)[0]
            print(f"Receiver confirmed {count} images")
    except OSError as error:
        print("Transfer stopped: "+str(error))
    connection.close()

    results=results[:count]  # Only keep stats for confirmed images
    for image in results:
        total+=image["size"]

    seconds=time.time()-start
    megabytes=total/1024/1024
    speed=0
    if seconds>0:
        speed=megabytes/seconds
    print(f"\n{count}/{len(images)} images confirmed")
    if count<len(images):
        not_sent=[]
        for path in images[count:]:
            not_sent.append(os.path.basename(path))
        print("Not confirmed: "+", ".join(not_sent))

    print(f"Total: {megabytes:.2f} MB in {seconds:.2f} s, average {speed:.2f} MB/s")
    if count>0:
        print(f"Average image size: {megabytes/count:.2f} MB")
    summary(results)


def main():
    print("PixDrop Sender")
    images=[]
    while True:
        path=input("Image name or folder path (type send when done): ")
        path=path.strip()
        path=path.strip('"')
        if path.lower()=="send":
            break
        if not os.path.exists(path):
            print("Not Found")
            continue
        found=find(path)
        images=images+found
        print(f"Added {len(found)} image(s), {len(images)} in total")
    if len(images)==0:
        print("No images to send.")
        return

    message=input("Send a message with images(press Enter to skip): ")
    ip=input("Receiver's IP address: ").strip()

    send_images(ip, images, message)

main()