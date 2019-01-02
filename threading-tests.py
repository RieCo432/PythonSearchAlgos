import threading
from datetime import datetime

new_list = []

def worker(index_start, index_end):
    for i in range(index_start, index_end):
        new_list[i] = new_list[i] ** 4
        print(new_list[i])



for i in range(0, 100):
    new_list.append(i)

total_threads = 16

its_per_thread = len(new_list)/total_threads
threads = []
start = datetime.now()
for i in range(0, total_threads):
    t = threading.Thread(target=worker, args=(int(round(i*its_per_thread)), int(round((i+1)*its_per_thread))))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print((datetime.now()-start).microseconds)

