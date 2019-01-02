import threading
from datetime import datetime

new_list = []

def worker(sublist):
    for i in sublist:
        print(i)


for i in range(0, 100):
    new_list.append(i)

total_threads = 3

its_per_thread = len(new_list)/total_threads

start = datetime.now()
for i in range(0, total_threads):
    sublist = new_list[int(round(i*its_per_thread)):int(round((i+1)*its_per_thread))]
    print(sublist)
    t = threading.Thread(target=worker, args=(sublist,))
    t.start()
    t.join()

print((datetime.now()-start).microseconds/1000.0)

