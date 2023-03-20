import math
# f = open("Stats/K-mutex/Tests/Random_busy_waiting_mid_scheduler.csv",'r')
f = open("temp.csv",'r')
numberOfRequests = 0
numberOfEnteringsInCS = 0
waitingTimesDictionary = {}
timeInCSDictionary = {}

for riga in f:
	data = riga.strip().split(',')

	if data[0] == "req_cs":
		numberOfRequests += 1
		
	if data[0] == "att_cs":
		waitingTimesDictionary[numberOfRequests] = float(data[1])


	if data[0] == "cs":
		numberOfEnteringsInCS += 1
		timeInCSDictionary[numberOfRequests] = float(data[1])
	
		
print("Sono state mandate un totale di", str(numberOfRequests), "richieste\n")
print("La CS è stata acceduta", str(numberOfEnteringsInCS), "volte\n")

#Calculate average waiting time		
totalWaitingTime = 0
for elem in waitingTimesDictionary:
	totalWaitingTime += waitingTimesDictionary[elem]
	
averageWaitingTime = totalWaitingTime/numberOfRequests
print("la media del tempo di attesa prima di entrare in cs e' pari a "+str(averageWaitingTime)+"\n")

#Calculate variance of waiting time	
tempVariance = 0
for elem in waitingTimesDictionary:
	tempVariance = tempVariance + math.pow(waitingTimesDictionary[elem]-averageWaitingTime,2)
varianceWaitingTime = tempVariance/(numberOfRequests-1)
print("la varianza invece e' pari a "+str(varianceWaitingTime)+"\n")

#Calculate standardDeviation of waiting time	
standardDeviationWaitingTime = math.sqrt(varianceWaitingTime)
print("la dev std e' pari a"+str(standardDeviationWaitingTime)+"\n")

#Calculate average time in CS
singleTimeInCS = 0
for elem in timeInCSDictionary:
	singleTimeInCS = singleTimeInCS + timeInCSDictionary[elem]
averageTimeInCS = singleTimeInCS/numberOfRequests
print("la media del tempo di permanenza in cs e' pari a "+str(averageTimeInCS)+"\n")

#Calculate variance of time in CS
tempVarCS = 0
for elem in timeInCSDictionary:
	tempVarCS = tempVarCS + math.pow(timeInCSDictionary[elem]-averageTimeInCS,2)
VarianceTimeinCS = tempVarCS/(numberOfRequests-1)
print("la varianza invece e' pari a "+str(VarianceTimeinCS)+"\n")

#Calculate standard Deviation of time in CS
standardDeviationCS = math.sqrt(VarianceTimeinCS)
print("la dev std e' pari a "+str(standardDeviationCS)+"\n")
