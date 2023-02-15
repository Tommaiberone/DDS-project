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

			timeout = random.randint(0,10)
			random_process = random.randint(0, N-1)

			time.sleep(timeout)
			
			#Quando scade manda un messaggio ad un processo random di entrare in cs

			msg = Msg()
			msg.kind = "GO"
			msg.mit = 0
			msg.dest = random_process
			msg.seq = 0
			msg.num_rep = 0

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
		self.def_c= [0]*N
		self.reply_count= [0]*N
		
		#print("daje")
		self.bus.subscribe(self.handle_message)	
		#print("pippo_thread")
		
	
	def handle_message(self,message : Msg):
		
		if message.dest == self.pid or message.dest == BROADCAST:
			
			if self.pid != message.mit:
					
				if message.kind == "REQ":
					self.maxseq = max(self.maxseq,message.seq)
					if self.cs or (self.req_cs and (self.seq,self.pid) < (message.seq,message.mit)):
						print("sono"+str(self.pid)+"e defero una req\n")
						self.def_c[message.mit] +=1
					else:
						
				
						self.send("REPLY",self.pid,message.mit,self.maxseq,1+self.def_c[message.mit])
						self.def_c[message.mit] = 0
						#print("sono"+str(self.pid)+"e mando una reply\n")
					
					
				elif message.kind == "REPLY":
					#print("sono"+str(self.pid)+"e ho ricevuto una reply\n")
					print("questo e il mio reply conunt ["+str(self.pid)+"]"+str(self.reply_count[message.mit]))
					self.reply_count[message.mit] -= message.num_rep
					#if (self.not_in_cs() >= N-K):
					if self.req_cs and (self.not_in_cs() >= N-K):
						self.req_cs = False
						print("sono"+str(self.pid)+"e entro in cs\n")
						self.cs = True
						self.do_cs_stuff()
						self.cs = False
						for i in range(0,N):
							if self.def_c[i] != 0:
								self.send("REPLY",self.pid,i,self.maxseq,self.def_c[i])
								self.def_c[i] = 0

				elif message.kind == "GO":
					self.req_cs = True
					self.seq = self.maxseq + 1
					print("sono"+str(self.pid)+"e mando una req\n")
					self.send("REQ",self.pid, BROADCAST, self.seq, 0)
					for i in range(0,N):
						self.reply_count[i]+=1
					#for elem in self.reply_count:
					#	elem += 1


			
	def send(self,kind :str,mit :int,dest : int, seq : int, num : int):
		m=Msg()
		m.kind = kind
		m.mit = mit
		m.dest = dest			
		m.seq = self.maxseq
		m.num_rep = num
		self.bus.publish(m)
		

	def not_in_cs(self):
		print("sono "+str(self.pid)+" e conto le reply")
		c = 0
		for i in range(0,N):
			print(self.reply_count[i])
			if i != self.pid and self.reply_count[i] == 0:
				c+=1
		return c
		
	def do_cs_stuff(self):
		print("inizio a lavora")
		time.sleep(random.randint(0,5))
		print("vaffanculo vado a casa")
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
	
