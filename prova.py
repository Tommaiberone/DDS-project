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

class Msg(NamedTuple):
	
	kind : str
	mit : int
	dest: int
	seq : int
	
class Thread:
	
	pid : int
	req_cs : bool
	cs:	bool
	seq : int
	maxseq : int
	
	def __init__(self,bus: EventBus,pid: int):
		
		self.pid = pid
		self.req_cs = False
		self.cs = False
		self.seq = 0
		
		self.bus.subscribe(self.handle_message)
		
	
	
	
	
	def handle_message(self,message : Msg):
		
		if message.dest == self.pid:
			
			if message.kind == "REQ":
				self.maxseq = max(maxseq,message.seq)
				if cs or (req_cs and (self.seq,self.pid) < (message.seq,message.mit)):
					
				
			if message.kind == "REPLY":
			
	
	
	def send(self,kind :str,mit :int,dest : int, seq : int):
		




def start_threads():
	for i in range(N):
		print("pluto")
		threads[i] = threading.Thread(target=thread_function)

def thread_function():
