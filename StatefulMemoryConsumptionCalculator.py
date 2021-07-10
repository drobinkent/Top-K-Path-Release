
import math

def findStatefulMemoryConsumption(P,K,W,L,Q,R,D):
    print("RangeMatch Tcam based schemes TCAM consumption is ")
    print((P*K*W*(L+W))/(8*1024))
    print("RangeMatch Tcam based schemes SRAM consumption is ")
    print((P*K*Q)/(8*1024))

    print("P4KP based schemes TCAM consumption is ")
    print((P*L + K*K)/(8*1024))

    print("P4KP based schemes SRAM consumption is ")
    print((P*R + P*K + K*D + 2*P*K*D + K*P*Q)/(8*1024))


R=20
Q=10
W = 4
L=128 # for Ipv6 L =128 bits are required
# print("For K=4, P = 16")
# P=16
# K=4
# findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))
# print("\n\n")

# print("For K=4, P = 32")
# P=32
# K=4
# findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))
# print("\n\n")


# print("For K=8, P = 32")
# P=32
# K=8
# findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))
# print("\n\n")
#
#
# print("For K=8, P = 64")
# P=64
# K=8
# findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))
# print("\n\n")
#
# print("For K=8, P = 128")
# P=128
# K=8
# findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))
# print("\n\n")
#
# print("For K=8, P = 256")
# P=256
# K=8
# findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))
# print("\n\n")



# print("\n\n\nFor K=16, P = 512")
# P=512
# K=16
# findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))


print("\n\nFor K=16, P = 1024")
P=1024
K=16
findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))

print("\n\nFor K=16, P = 2048")
P=2048
K=16
findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))

print("\n\nFor K=16, P = 4096")
P=4096
K=16
findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))


print("\n\nFor K=16, P = 8192")
P=8192
K=16
findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))


print("\n\nFor K=16, P = 10240")
P=10240
K=16
findStatefulMemoryConsumption(P=P,K=K,W= W,L = L,Q=Q,R=R,D=math.ceil(math.log(K,2)))


