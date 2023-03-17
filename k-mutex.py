import os
import threading
import pymq
from pymq import EventBus
from pymq.provider.redis import RedisConfig
import time
import random

# ConstantimedServer
K = 5
N = 10
BROADCAST = 1899
TIME = 0
CHATTY = False
SERVER = 0xcafe

threads = [0]*N
is_finished = 0

class Counter:
	c = 0
	
pippo = Counter()


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
		

	# StartimedServer worker threads
	def start_threads(self, bus):

		for i in range(N):
			threads[i] = threading.Thread(target=thread_function, args=(i, bus))
			threads[i].start()

		#for i in range(N):
		#	threads[i].join()
	
	# Periodically sends GO messages to random processes
	def timed_countdown(self):

		# cwd = os.getcwd()  # Get the current working directory (cwd)
		# files = os.listdir(cwd)  # Get all the files in that directory
		# print("Files in %r: %s" % (cwd, files))

		with open('Inputs/values_fast.txt', 'r') as file:
			values = file.read()
			values = values.replace("\n", "").replace("  ", " ").split(" ")
			float_values = list(map(float, values))

			with open('Inputs/processes.txt', 'r') as file2:
				processes = file2.read()
				processes = processes.replace("\n", "").split(" ")
				int_processes = list(map(int, processes))


				for i in range(len(float_values)):

					timeout = float_values[i]
					random_process = int_processes[i]
					
					time.sleep(timeout)

					# Send a GO message to a random process
					msg = Msg()
					msg.kind = "GO"
					msg.mit = SERVER
					msg.dest = random_process
					msg.seq = 0
					msg.num_rep = 0
					self.bus.publish(msg)
				
				msg = Msg()
				msg.kind = "STOP"
				msg.mit = SERVER
				msg.dest = BROADCAST
				msg.h = 0
				msg.k = 1

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
	time : float
	queue : []
	
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
		self.queue = []
		
		time = 0	
		
	def self_destroy(self):

		if CHATTY: print("Sono il processo " + str(self.pid) + " e mi fermo")
		self.bus.unsubscribe(self.handle_message)
		return
		
	# Handler for incoming messages
	def handle_message(self, message : Msg):

		global is_finished

		# If the message is addressed to this process or is a broadcast
		if message.dest == self.pid or message.dest == BROADCAST:

			# Ignore messages sent by this process
			if self.pid != message.mit:

				if message.kind == "STOP":

					if self.req_cs or self.cs:
						if CHATTY: print("Sono il processo " + str(self.pid) + " e APPENDO uno stop")
						self.queue.append(message)

					else:
						is_finished += 1
						if CHATTY: print("Sono il processo " + str(self.pid) + " e ho finito")

						if is_finished == N:
							if CHATTY: print("Sono il processo " + str(self.pid) + " e ESEGUO uno stop")
							self.self_destroy()
					

				elif message.kind == "REQ":

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
						pippo.c+=1

				      # Check if the message is a reply to a request for the critical section
				elif message.kind == "REPLY":

					# Update the reply_count variable
					self.reply_count[message.mit] -= message.num_rep
					
					# Check if the process has received replies from all processes except itimedServerelf and can enter the critical section
					if self.req_cs and (self.not_in_cs() >= N-K):

						self.req_cs = False
						if CHATTY: print("sono" + str(self.pid) + "e entro in cs\n")
						
						print("att_cs"+","+str( time.time() - self.time))
						
						self.cs = True

						self.do_cs_stuff()
						self.cs = False
						
						# Send replies to deferred requestimedServer
						for i in range(0, N):
							if self.def_c[i] != 0:
								self.send("REPLY", self.pid, i, self.maxseq, self.def_c[i])
								pippo.c +=1
								self.def_c[i] = 0

						if len(self.queue) != 0 and self.queue[0].kind == "STOP":
							
							if CHATTY: print("Sono il processo " + str(self.pid) + " e ho finito")
							is_finished += 1

							if is_finished == N:
								if CHATTY: print("Sono il processo " + str(self.pid) + " e ESEGUO uno stop")
								self.self_destroy()
						
						elif len(self.queue) != 0 and self.queue[0].kind == "GO":
							self.send_request()
							self.queue.pop(0)
								
				# Check if the message is a signal to request access to the critical section
				elif message.kind == "GO":

					if self.req_cs or self.cs:
						self.queue.append(message)

					else:
						self.send_request()

					


	def send_request(self):

		self.time = time.time()
		
		# Update the request variables
		self.req_cs = True
		self.seq = self.maxseq + 1
		if CHATTY: print("sono"+str(self.pid)+"e mando una req\n")
		# Send a request message to all processes and update the reply_count variable
		self.send("REQ", self.pid, BROADCAST, self.seq, 0)
		pippo.c+=N-1
		
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
		if CHATTY: print("sono "+str(self.pid)+" e conto le reply")
		c = 0

		for i in range(0, N):
			#print(self.reply_count[i])
			if i != self.pid and self.reply_count[i] == 0:
				c += 1

		return c
		
	def do_cs_stuff(self):

		# Define a function that simulates the process performing some critical section work
		t0 = time.time()
		#time.sleep(.5)
		time.sleep(random.uniform(0.1,0.3))
		print("cs,"+str(time.time()-t0))
		if CHATTY:print("inizio a lavorare")
		if CHATTY:print("Finito! Vado a casa")

def thread_function(pid, bus):

	# Define a function that runs a thread for a specific process ID and message bus
	thread = Thread(bus, pid)

def main():

	# Initialize the message bus and the time server
	bus = pymq.init(RedisConfig())
	timedServer = TimeServer(bus)
	
	timedServer.start_threads(bus)
	timedServer.timed_countdown()

	TIME = time.time()

	while is_finished != N:
		time.sleep(1)
	
	for i in range(0,N):
		threads[i].join()
	
	print("In totale sono stati inviati "+str(pippo.c)+" messaggi")

if __name__ == '__main__':
    main()
