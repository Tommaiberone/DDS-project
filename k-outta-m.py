import threading
#import tcp
import queue
import pymq
from pymq import EventBus
from pymq.provider.redis import RedisConfig
import random
import time


M = 10
N = 10
BROADCAST = 1899
threads = [0]*N
in_cs=[]

#q = queue.Queue()


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
	
	def handle_message(self,message : Msg):
		return
	
	
	def __init__(self, bus: EventBus):
		self.bus = bus
		#print("topolino")
		self.bus.subscribe(self.handle_message)
		#print("minni")

	def start_threads(self,bus):
		for i in range(N):
			#print("pluto")
			threads[i] = threading.Thread(target = thread_function, args=(i, bus))
			threads[i].start()
		#self.bus.subscribe(self.handle_message)
		#threads[0].start()
	
	def timed_countdown(self):
		
		while True:

			timeout = random.randint(0,2)
			random_process = random.randint(0, N-1)

			time.sleep(timeout)
			
			#Quando scade manda un messaggio ad un processo random di entrare in cs

			msg = Msg()
			msg.kind = "GO"
			msg.mit = 0
			msg.dest = random_process
			msg.h = 0
			msg.k = random.randint(1,M)

			self.bus.publish(msg)

	
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
		
		#print("daje")
		self.bus.subscribe(self.handle_message)	
		#print("pippo_thread")
		
	
	def handle_message(self,message : Msg):
		
		if message.dest == self.pid or message.dest == BROADCAST:
			
			if self.pid != message.mit:
					
				if message.kind == "REQ":
					self.maxh = max(self.maxh,message.h)
					self.prio = (self.scdem or self.ok) and (self.h,self.pid) < (message.h,message.mit)
					
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
					if self.scdem and (self.sum_used() + self.k) <= M:
						print("sono "+str(self.pid)+"per me tot usato e "+str(self.sum_used() + self.k))
						self.scdem = False
						self.ok = True
						print(str(self.pid)+"sono in cs")
						in_cs.append(self.pid)
						print(in_cs)
						self.do_cs_stuff()
						self.ok = False
						in_cs.remove(self.pid)
						
						for i in range(0,len(self.delayed)):
							self.send("FREE",self.pid,message.mit,self.maxh,self.k)
						self.delayed = []

				elif message.kind == "GO":
					self.scdem = True
					self.ok = False
					self.h = self.maxh + 1
					self.k = message.k
					print("sono"+str(self.pid)+"e mando una req per"+str(self.k)+"risorse\n")
					for i in range(0,N):
						if i != self.pid:
							self.used[i]+=M
					self.send("REQ",self.pid, BROADCAST, self.h, self.k)
					

			
	def send(self,kind :str,mit :int,dest : int, h : int, num : int):
		m=Msg()
		m.kind = kind
		m.mit = mit
		m.dest = dest			
		m.h = self.maxh
		m.k = num
		self.bus.publish(m)
		
	def sum_used(self):
		s = 0
		for i in range(0,N):
			if i != self.pid:
				s+=self.used[i]
		return s
					
		
	def do_cs_stuff(self):
		print(str(self.pid)+" inizia a lavora con "+str(self.k)+" risorse")
		time.sleep(random.randint(1,7))
		print("vaffanculo, "+str(self.pid)+" va a casa")
		#for i in range(0,34):
		#	print(str(self.pid)+"\n")


def thread_function(pid, bus):
	#print("ciao")
	thread = Thread(bus, pid)


def main():
	#start threads
	bus = pymq.init(RedisConfig())
	ts=TimeServer(bus)
	ts.start_threads(bus)
	ts.timed_countdown()

if __name__ == '__main__':
    main()
	
