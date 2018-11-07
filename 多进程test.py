from multiprocessing import Process
import os
s=[]
def run_process(name,id):
    print("Child process %s (%s) Running"%(name,os.getpid()))
    s.append(id)

if __name__ == "__main__":
    print("Parent process %s."%(os.getpid()))
    for i in range(5):
         p = Process(target=run_process,args=(str(i),i))
         print("Process will start.")
         p.start()
    p.join()
    print(s)
    print("Process end")
