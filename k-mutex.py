import threading
#import tcp
import queue
import pymq
from pymq import EventBus
from pymq.provider.redis import RedisConfig
import random
import time

# Constants
K = 5
N = 10
BROADCAST = 1899
threads = [0]*N

# Define a message class
class Msg:
	kind : str
	mit : int
	dest: int
	seq : int
	num_rep : int

# Define a TimeServer class
class TimeServer:
	bus : EventBus
	threads = [0]*N
	resources = [0]*K
	
	# Handler for incoming messages
	def handle_message(self, message : Msg):
		return
	
	# Constructor
	def __init__(self, bus: EventBus):
		self.bus = bus
		self.bus.subscribe(self.handle_message)

	# Starts worker threads
	def start_threads(self, bus):
		for i in range(N):
			threads[i] = threading.Thread(target=thread_function, args=(i, bus))
			threads[i].start()
	
	# Periodically sends GO messages to random processes
	def timed_countdown(self):
		while True:
			timeout = random.randint(0, 10)
			random_process = random.randint(0, N-1)
			time.sleep(timeout)

			# Send a GO message to a random process
			msg = Msg()
			msg.kind = "GO"
			msg.mit = 0
			msg.dest = random_process
			msg.seq = 0
			msg.num_rep = 0
			self.bus.publish(msg)

# Define a Thread class
class Thread:
	pid : int
	req_cs : bool
	cs:	bool
	seq : int
	maxseq : int
	def_c: [0]*N
	reply_count: [0]*N
	
	# Constructor
	def __init__(self,bus: EventBus,pid: int):
		self.pid = pid
		self.req_cs = False
		self.cs = False
		self.seq = 0
		self.maxseq = 0
		self.bus = bus
		self.def_c= [0]*N
		self.reply_count= [0]*N
		self.bus.subscribe(self.handle_message)	
		
	# Handler for incoming messages
	def handle_message(self, message : Msg):

		# If the message is addressed to this process or is a broadcast
		if message.dest == self.pid or message.dest == BROADCAST:

			# Ignore messages sent by this process
			if self.pid != message.mit:

				if message.kind == "REQ":

					# Update the maximum sequence number seen so far
					self.maxseq = max(self.maxseq,message.seq)

					if self.cs or (self.req_cs and (self.seq,self.pid) < (message.seq,message.mit)):

						# Defer the request if this process is in the critical section
						# or has already requested the critical section with a higher sequence number
						self.def_c[message.mit] +=1
					else:

						# Grant the request by sending a REPLY message
						self.send("REPLY",self.pid,message.mit,self.maxseq,1+self.def_c[message.mit])
						self.def_c[message.mit] = 0

				      # Check if the message is a reply to a request for the critical section
				elif message.kind == "REPLY":
					# Update the reply_count variable
					self.reply_count[message.mit] += 1
					
					# Check if the process has received replies from all processes except itself and can enter the critical section
					if self.req_cs and (self.not_in_cs() >= N-K):
						self.req_cs = False
						print("sono" + str(self.pid) + "e entro in cs\n")
						self.cs = True
						self.do_cs_stuff()
						self.cs = False
						
						# Send replies to deferred requests
						for i in range(0, N):
							if self.def_c[i] != 0:
								self.send("REPLY", self.pid, i, self.maxseq, self.def_c[i])
								self.def_c[i] = 0
								
				# Check if the message is a signal to request access to the critical section
				elif message.kind == "GO":
					# Update the request variables
					self.req_cs = True
					self.seq = self.maxseq + 1
					print("sono"+str(self.pid)+"e mando una req\n")
					# Send a request message to all processes and update the reply_count variable
					self.send("REQ", self.pid, BROADCAST, self.seq, 0)
					
					for i in range(0, N):
						self.reply_count[i] += 1


			
	def send(self, kind: str, mit: int, dest: int, seq: int, num: int):
		# Define a function for sending a message to the message bus
		# and update the message attributes
		m = Msg()
		m.kind = kind
		m.mit = mit
		m.dest = dest
		m.seq = self.maxseq
		m.num_rep = num
		self.bus.publish(m)

	def not_in_cs(self):
		# Define a function for counting the number of processes that have not replied
		# to a request message sent by this process
		print("sono "+str(self.pid)+" e conto le reply")
		c = 0
		for i in range(0, N):
			print(self.reply_count[i])
			if i != self.pid and self.reply_count[i] == 0:
				c += 1
		return c
		
	def do_cs_stuff(self):
		# Define a function that simulates the process performing some critical section work
		print("inizio a lavora")
		time.sleep(random.randint(0,5))
		print("vaffanculo vado a casa")

def thread_function(pid, bus):
	# Define a function that runs a thread for a specific process ID and message bus
	thread = Thread(bus, pid)
	thread.run()

def main():
	# Initialize the message bus and the time server
	bus = pymq.init(RedisConfig())
	ts = TimeServer(bus)
	
	# Start the threads and the time server
	for i in range(0, N):
		t = Thread(target=thread_function, args=(i, bus))
		t.start()
	ts.start_threads(bus)
	ts.timed_countdown()

if __name__ == '__main__':
    main()
