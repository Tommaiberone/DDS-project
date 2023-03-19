import threading
import pymq
from pymq import EventBus
from pymq.provider.redis import RedisConfig
import time
import random

#Modify to change behaviour
DEBUG = False
CHATTY = False
CS_RANDOM_SLEEP_01_03 = True
CS_SLEEP_01 = False
SCHEDULER = "mid"

#Constants
M = 5
N = 10
BROKER = 1293
BROADCAST = 1899
SERVER = 0xcafe

#Global variables
threads = [0]*N
messageCounter = 0
is_finished = 0

class Msg:
	
	kind : str
	mit : int
	dest: int
	h : int
	k : int

class TimeServer:
	
	bus : EventBus
	threads = [0]*N
	resources = [0]*M
	threads_in_cs = []
	
	def handle_message(self,message : Msg):
		return
	
	def __init__(self, bus: EventBus):
		self.bus = bus
		self.bus.subscribe(self.handle_message)

	def start_threads(self,bus):

		global threads

		for i in range(0, N):
			threads[i] = threading.Thread(target = thread_function, args=(i, bus))
			threads[i].start()
			
	def timed_countdown(self):

		#Decide which Scheduler to use
		if SCHEDULER == "fast":	
			scheduler = "Inputs/values_fast.txt"

		elif SCHEDULER == "mid":	
			scheduler = "Inputs/values_mid.txt"

		else:	
			scheduler = "Inputs/values_slow.txt"	
		
		with open(scheduler, 'r') as file:
			values = file.read()
			values = values.replace("\n", "").replace("  ", " ").strip().split(" ")
			float_values = list(map(float, values))

			with open('Inputs/processes.txt', 'r') as file2:
				processes = file2.read()
				processes = processes.replace("\n", "").split(" ")
				int_processes = list(map(int, processes))
				#print(int_processes)

				for i in range(len(float_values)):

					timeout = float_values[i]
					random_process = int_processes[i]
					
					time.sleep(timeout)
					
					#Quando scade manda un messaggio ad un processo random di entrare in cs
					msg = Msg()
					msg.kind = "GO"
					msg.mit = SERVER #special value for server use
					msg.dest = random_process
					msg.h = 0
					msg.k = 1
					

					self.bus.publish(msg)

				msg = Msg()
				msg.kind = "STOP"
				msg.mit = SERVER
				msg.dest = BROADCAST
				msg.h = 0
				msg.k = 1

				self.bus.publish(msg)


	def handle_message(self, message : Msg) :

		if message.dest == BROKER:

			if message.kind == "ADD":

				self.threads_in_cs.append(message.mit)

				if DEBUG: print("I processi attualmente in cs sono: ")
				if DEBUG: print(self.threads_in_cs)

			else:

				self.threads_in_cs.remove(message.mit)
		
class Thread:

	scdem : bool
	ok	  : bool
	prio  :	bool
	h	  :	int
	maxh  :	int
	used  : []
	delayed : []
	k		: int
	pid 	: int
	time : float
	queue : []

	def __init__(self,bus: EventBus,pid: int):
		
		self.pid = pid
		self.scdem = False
		self.ok = False
		self.prio = False
		self.k = 0
		self.h = 0
		self.maxh = 0
		self.bus = bus
		self.used= [0]*N
		self.delayed= []
		self.queue= []
		self.time = 0
		
		self.bus.subscribe(self.handle_message)

		if CHATTY: print("Sono il processo " + str(self.pid))
		
	def self_destroy(self):

		if CHATTY: print("Sono il processo " + str(self.pid) + " e mi fermo")
		self.bus.unsubscribe(self.handle_message)
		return

	def handle_message(self,message : Msg):
		
		global messageCounter
		global is_finished
		
		if message.dest == self.pid or message.dest == BROADCAST:
			
			if self.pid != message.mit:

				if message.kind == "STOP":

					if self.scdem or self.ok:
						if CHATTY: print("Sono il processo " + str(self.pid) + " e APPENDO uno stop")
						self.queue.append(message)

					else:
						is_finished += 1
						if CHATTY: print("Sono il processo " + str(self.pid) + " e ho finito")

						if is_finished == N:
							if CHATTY: print("Sono il processo " + str(self.pid) + " e ESEGUO uno stop")
							self.self_destroy()
					
				elif message.kind == "REQ":

					self.maxh = max(self.maxh,message.h)
					self.prio = (self.scdem or self.ok) and ((self.h,self.pid) < (message.h,message.mit))

					if ( self.prio!=True or message.mit in self.delayed):
						self.send("FREE",self.pid,message.mit,self.maxh,M)
						messageCounter+=1
						
					else:
						
						if self.k != M:
							self.send("FREE",self.pid,message.mit,self.maxh,M-self.k)
							messageCounter+=1
						self.delayed.append(message.mit)
								
				elif message.kind == "FREE":
					self.used[message.mit] -= message.k
					if DEBUG: print("sono "+str(self.pid)+", ", message.mit, " mi ha liberato ", message.k, " risorse")

					if DEBUG: 
						if self.scdem and (self.sum_used() + self.k) > M:
							if DEBUG: print("sono "+str(self.pid)+", ho richiesto "+str(self.k) + ", ma ci sono solo " + str(max(0,M - self.sum_used())) + " liberi")
					
					if self.scdem and (self.sum_used() + self.k) <= M:
						self.scdem = False
						self.ok = True
						
						if CHATTY:
							print("sono " + str(self.pid)+" e sono in cs")

						print("att_cs,"+str(time.time() - self.time))
						
						self.do_cs_stuff()

						self.ok = False
						
						for i in range(0,len(self.delayed)):
							self.send("FREE",self.pid,self.delayed[i],self.maxh,self.k)
							messageCounter+=1

						self.delayed = []
						self.k = 0

						if len(self.queue) != 0 and self.queue[0].kind == "STOP":
							
							if CHATTY: print("Sono il processo " + str(self.pid) + " e ho finito")
							is_finished += 1
							
							if DEBUG: print(is_finished)

							if is_finished == N:
								if CHATTY: print("Sono il processo " + str(self.pid) + " e ESEGUO uno stop")
								self.self_destroy()
						
						elif len(self.queue) != 0 and self.queue[0].kind == "GO":
							self.send_request(self.queue[0])
							self.queue.pop(0)



				elif message.kind == "GO":
					
					if self.ok:
						self.queue.append(message)

					else:
						self.send_request(message)

	def send_request(self, message):
		
		global messageCounter

		print("req_cs")

		self.time = time.time()
					
		self.scdem = True
		self.ok = False
		self.h = self.maxh + 1
		self.k = message.k

		if DEBUG: print("sono "+str(self.pid)+" e mando una req per "+str(self.k)+" risorse\n")
		
		for i in range(0,N):
			if i != self.pid:
				self.used[i]+=M

		self.send("REQ",self.pid, BROADCAST, self.h, self.k)
		messageCounter += N-1


	def send(self,kind :str,mit :int,dest : int, h : int, num : int):
		m=Msg()
		m.kind = kind
		m.mit = mit
		m.dest = dest			
		m.h = h
		m.k = num
		self.bus.publish(m)
		
	def sum_used(self):
		s = 0
		for i in range(0,N):
			if i != self.pid:
				s+=self.used[i]
		return s
					
		
	def do_cs_stuff(self):

		if CHATTY: print(str(self.pid)+" inizia a lavorare con "+str(self.k)+" risorse\n")
		
		t0 = time.time()

		if CS_SLEEP_01: 			time.sleep(.1)
		if CS_RANDOM_SLEEP_01_03: 	time.sleep(random.uniform(0.1,0.3))
		
		print("cs,"+str(time.time()-t0))

		if CHATTY: print("Finito! "+str(self.pid)+" va a casa\n")

def thread_function(pid, bus):
	thread = Thread(bus, pid)


def main():

	global threads

	#start threads
	bus = pymq.init(RedisConfig())
	ts=TimeServer(bus)
	ts.start_threads(bus)
	ts.timed_countdown()

	while is_finished != N:
		time.sleep(1)

	for i in range(0,N):
		threads[i].join()

	if CHATTY: print("ho fatto i join")
	if CHATTY: print("in totale sono stai inviati "+str(messageCounter)+" messaggi")
		

if __name__ == '__main__':
    main()
	
