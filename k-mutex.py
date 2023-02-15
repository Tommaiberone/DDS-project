import threading
#import tcp
import queue
import pymq
from pymq import EventBus
from pymq.provider.redis import RedisConfig
import random
import time


K = 5
N = 10
BROADCAST = 1899
threads = [0]*N

#q = queue.Queue()


class Msg:
	
	kind : str
	mit : int
	dest: int
	seq : int
	num_rep : int

class TimeServer:
	
	bus : EventBus
	threads = [0]*N
	resources = [0]*K
	
	def handle_message(self,message : Msg):
		return
	
	
	def __init__(self, bus: EventBus):
		self.bus = bus
		print("topolino")
		self.bus.subscribe(self.handle_message)
		print("minni")

	def start_threads(self,bus):
		for i in range(N):
			print("pluto")
			threads[i] = threading.Thread(target = thread_function, args=(i, bus))
		#self.bus.subscribe(self.handle_message)
	
	
	def timed_countdown():
		
		while True:

			timeout = random.randint(0,10)
			random_process = random.randint(0, N-1)

			time.sleep(timeout)
			
			#Quando scade manda un messaggio ad un processo random di entrare in cs

			msg = Msg()
			msg.kind = "GO"
			mit = 0
			dest = random_process
			seq = 0
			num_rep = 0

			self.bus.publish(msg)

	
class Thread:
	
	pid : int
	req_cs : bool
	cs:	bool
	seq : int
	maxseq : int
	def_c: [0]*N
	reply_count: [0]*N
	
	def __init__(self,bus: EventBus,pid: int):
		
		self.pid = pid
		self.req_cs = False
		self.cs = False
		self.seq = 0
		self.maxseq = 0
		self.bus = bus
		
		self.bus.subscribe(self.handle_message)	
		print("pippo")
	
	def handle_message(self,message : Msg):
		
		if message.dest == self.pid or message.dest == BROADCAST:
			
			if message.kind == "REQ":
				self.maxseq = max(maxseq,message.seq)
				if cs or (req_cs and (self.seq,self.pid) < (message.seq,message.mit)):
					self.def_c[message.mit] +=1
				else:
					send(self,"REPLY",self.pid,message.mit,self.maxseq,self.def_c[message.mit])
					
				
			elif message.kind == "REPLY":
				reply_count[message.mit] -= message.num_rep
				if self.req_cs and not_in_cs() >= N-K:
					self.req_cs = False
					self.cs = True
					do_cs_stuff()

			elif message.kind == "GO":
				self.cs == True
				self.maxseq += 1
				send(self,"REQ",self.pid, BROADCAST, self.maxseq, 0)
				for elem in reply_count:
					reply_count += 1


			
	def send(self,kind :str,mit :int,dest : int, seq : int, num : int):
		m=Msg()
		m.kind = kind
		m.mit = mit
		m.dest = dest			
		m.seq = self.maxseq
		m.num = num
		self.bus.publish(m)
		

	def not_in_cs():
		c = 0
		for i in range(0,N):
			if i != self.pid and reply_count[i] == 0:
				c+=1
		return c
		
	def do_cs_stuff():
		for i in range(0,34):
			print(self.pid+"\n")


def thread_function(pid, bus):
	thread = Thread(pid, bus)


def main():
	#start threads
	bus = pymq.init(RedisConfig())
	ts=TimeServer(bus)
	ts.start_threads(bus)
	ts.timed_countdown()

if __name__ == '__main__':
    main()
	
