import math
f = open("k-mutex_stat_values_1.csv",'r')
tot = 0
att = {}
cs = {}

for riga in f:
	data = riga.strip().split(',')
	if data[0] == "att_cs":
		tot= tot+1
		att[tot] = float(data[1])
	if data[0] == "cs":
		cs[tot] = float(data[1])
	
		
print("So stati eseguiti un totale di "+str(tot)+" task\n")
		
a = 0
for elem in att:
	a = a + att[elem]
	
avg = a/tot

a = 0
for elem in att:
	a = a + math.pow(att[elem]-avg,2)
var = a/(tot-1)


print("la media del tempo di attesa prima di entrare in cs e' pari a "+str(avg)+"\n"+"la varianza invece e' pari a "+str(var)+"\n")
dev = math.sqrt(var)
print("la dev std e' pari a"+str(dev)+"\n")
	
a = 0
for elem in cs:
	a = a + cs[elem]
	
avg = a/tot
a = 0
for elem in cs:
	a = a + math.pow(cs[elem]-avg,2)
var = a/(tot-1)

print("la media del tempo di permanenza in cs e' pari a "+str(avg)+"\n"+"la varianza invece e' pari a "+str(var)+"\n")
dev = math.sqrt(var)
print("la dev std e' pari a "+str(dev)+"\n")

