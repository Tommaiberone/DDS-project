import threading
import pymq
from pymq import EventBus
from pymq.provider.redis import RedisConfig
import random
import time


DEBUG = False
CHATTY = False

M = 5
N = 10
BROKER = 1293
BROADCAST = 1899
threads = [0]*N

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

		for i in range(0, N):
			threads[i] = threading.Thread(target = thread_function, args=(i, bus))
			threads[i].start()
	
		for i in range(N):
			threads[i].join()
			
	def timed_countdown(self):
		
		with open('values.txt', 'r') as file:
			values = file.read()
			values = values.replace("\n", "").replace("  ", " ").split(" ")
			float_values = list(map(float, values))

			with open('processes.txt', 'r') as file2:
				processes = file2.read()
				processes = processes.replace("\n", "").split(" ")
				int_processes = list(map(int, processes))

				for i in range(len(float_values)):

					timeout = float_values[i]
					random_process = int_processes[i]
					
					time.sleep(timeout)
					
					#Quando scade manda un messaggio ad un processo random di entrare in cs
					msg = Msg()
					msg.kind = "GO"
					msg.mit = 0
					msg.dest = random_process
					msg.h = 0
					#msg.k = random.randint(1,10)
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
		self.time = 0
		
		self.bus.subscribe(self.handle_message)	
		
	
	def handle_message(self,message : Msg):
		
		if message.dest == self.pid or message.dest == BROADCAST:
			
			if self.pid != message.mit:
					
				if message.kind == "REQ":

					self.maxh = max(self.maxh,message.h)
					self.prio = (self.scdem or self.ok) and ((self.h,self.pid) < (message.h,message.mit))

					if ( self.prio!=True or message.mit in self.delayed):
						self.send("FREE",self.pid,message.mit,self.maxh,M)
						"""else:
						if message.mit in delayed:
							self.send("FREE",self.pid,message.mit,self.maxh,M)"""			
						
					else:
						
						if self.k != M:
							self.send("FREE",self.pid,message.mit,self.maxh,M-self.k)
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
						
						self.do_cs_stuff()
						self.ok = False
						
						for i in range(0,len(self.delayed)):
							self.send("FREE",self.pid,self.delayed[i],self.maxh,self.k)

						self.delayed = []
						self.k = 0

				elif message.kind == "GO":

					self.time = time.time()
					
					if not(self.scdem or self.ok):
						self.scdem = True
						self.ok = False
						self.h = self.maxh + 1
						self.k = message.k

						if DEBUG: print("sono "+str(self.pid)+" e mando una req per "+str(self.k)+" risorse\n")
						
						for i in range(0,N):
							if i != self.pid:
								self.used[i]+=M

						self.send("REQ",self.pid, BROADCAST, self.h, self.k)
					

			
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

		print("Sono entrato in cs dopo:", time.time() - self.time, "secondi")

		if CHATTY: print(str(self.pid)+" inizia a lavora con "+str(self.k)+" risorse\n")

		self.send("ADD", self.pid, BROKER, 0, self.k)

		#time.sleep(random.randint(1,10))

		self.send("REMOVE", self.pid, BROKER, 0, self.k)
		if CHATTY: print("vaffanculo, "+str(self.pid)+" va a casa\n")


def thread_function(pid, bus):
	thread = Thread(bus, pid)


def main():

	#start threads
	bus = pymq.init(RedisConfig())
	ts=TimeServer(bus)
	ts.start_threads(bus)
	ts.timed_countdown()

if __name__ == '__main__':
    main()
	
