import threading
#import tcp
import queue
import pymq

pymq.init(RedisConfig())

K = 5
N = 10

q = queue.Queue()

threads[N]
resources = [K]

class TimeServer():
	bus
	



class Msg(NamedTuple):
	
	kind : str
	mit : int
	dest: int
	seq : int
	num_rep : int
	
class Thread:
	
	pid : int
	req_cs : bool
	cs:	bool
	seq : int
	maxseq : int
	def_c: int[N]
	rep_c: int[N]
	
	def __init__(self,bus: EventBus,pid: int):
		
		self.pid = pid
		self.req_cs = False
		self.cs = False
		self.seq = 0
		self.maxseq = 0
		self.bus = bus
		
		self.bus.subscribe(self.handle_message)
		
	
	
	
	
	def handle_message(self,message : Msg):
		
		if message.dest == self.pid:
			
			if message.kind == "REQ":
				self.maxseq = max(maxseq,message.seq)
				if cs or (req_cs and (self.seq,self.pid) < (message.seq,message.mit)):
					self.def_c[message.mit] +=1
				else:
					send(self,"REPLY",self.pid,message.mit,self.maxseq,self.def_c[message.mit])
					
				
			if message.kind == "REPLY":
				rep_c[message.mit] -= message.num_rep
				if self.req_cs and not_in_cs() >= N-K:
					self.req_cs = False
					self.cs = True
					do_cs_stuff()					
			
	
	
	def send(self,kind :str,mit :int,dest : int, seq : int,num : int):
		m=Msg()
		m.kind = kind
		m.mit = mit
		m.dest = dest
		if kind == "REQ":
			self.maxseq +=1
		m.seq = self.maxseq
		m.num = num
		self.bus.publish(m)
		

	def not_in_cs():
		c = 0
		for i in range(0,N):
			if i != self.pid and rep_c[i] == 0:
				c+=1
		return c
		
	def do_cs_stuff():
		for i in range(0,34):
			print(self.pid+"\n")

def start_threads():
	for i in range(N):
		print("pluto")
		threads[i] = threading.Thread(target=thread_function)

def thread_function():




def main():
	#start threads
	start_threads()
	
