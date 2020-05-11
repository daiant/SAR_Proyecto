v=[1,2,3,4,5,6]

for i in range(0,len(v)):
    print(v[i])
    if (i == len(v) - 1):
        print("bro")
        break
else:
    print("else al final")

print("final:{}".format(i))
