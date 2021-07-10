import logging.handlers
import logging.handlers

import bitarray as ba
from p4.v1 import p4runtime_pb2

import ConfigConst as ConfConst

logger = logging.getLogger('TopKPathManager')
logger.handlers = []
hdlr = logging.handlers.RotatingFileHandler(ConfConst.CONTROLLER_LOG_FILE_PATH, maxBytes = ConfConst.MAX_LOG_FILE_SIZE , backupCount= ConfConst.MAX_LOG_FILE_BACKUP_COUNT)
hdlr.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logging.StreamHandler(stream=None)
logger.setLevel(logging.INFO)

def modifyBit(n, position, b):
    '''
    # Python3 program to modify a bit at position
    # p in n to b.

    # Returns modified n.
        :param n:
        :param position:
        :param b:
        :return:
    '''
    mask = 1 << position
    return (n & ~mask) | ((b << position) & mask)

class TopKPathManager:
    '''
    In out system 0 means empty. k=0 means this is not a valid path
    We do this to reduce an extra checking in data plane. Because in data plane if-else is costly then memory
    so we decided to start the start the index from 0.
    in the actual storage where paths are stored we use (K+1)^2
    '''

    def __init__(self, dev, k):
        self.p4dev = dev
        self.maxRank = k
        self.portToRankMap = {}
        self.rankToCounterMap = {} #init needed
        self.rankToPortAtMaxIndexMap = {} #init needed
        self.portToIndexAtCurrentRankMap = {}
        self.rankToPort2dMap = {}
        for i in range(0, self.maxRank):
            self.rankToCounterMap[i] = ConfConst.INVALID
            self.rankToPortAtMaxIndexMap[i] = ConfConst.INVALID
            portList = []
            for j in range(0, self.maxRank):
                portList.append(0)
            self.rankToPort2dMap[i] = portList
        pass

    def printDS(self):
        print("portToRankMap is :",self.portToRankMap)
        print("rankToCounterMap is ", self.rankToCounterMap)
        print("rankToPortAtMaxIndexMap is :",self.rankToPortAtMaxIndexMap)
        print("portToIndexAtCurrentRankMap is ",self.portToIndexAtCurrentRankMap)
        print("rankToPort2dMap is ")
        for i in range (0, self.maxRank):
            print(self.rankToPort2dMap[i])
        pass
    def buildMetadataBasedPacketOut(self,  isDelete,   rank, port, rankMinIndex, rankMaxIndex, newPortIndex,bitmask, packet_out_port = 255):
        '''

        port_num_t  egress_port;
        bit<7>      _pad;
        //Previous all fields are not necessary for CLB. TODO  at sometime we will trey to clean up them. But at this moment we are not focusing on that
        bit<8> top_k_path_flags; //Here we will keep various falgs for CLB
        //--------bit-7--------|| If this bit is set then reet the counter
        //--------bit-6--------|| If this bit is set then this is a port delete packet
        //--------bit-5--------|| If this bit is set then this is a port insert packet
        //--------bit-4--------|| Other bits are ununsed at this moment
        //--------bit-3--------||
        //--------bit-2--------||
        //--------bit-1--------||
        //--------bit-0--------||

        bit<K> bitmask;
        bit<32> rank;
        bit<32> port;
        bit<32> rank_max_index;
        bit<32> rank_min_index;
        bit<32> new_port_index;
        '''
        # logger.info("for device "+self.p4dev.devName+"  Packet built for rank : "+str(rank)+" port :"+str(port)+" minindex : "+
        #             str(rankMinIndex)+" maxindex :"+str(rankMaxIndex)+" portIndex "+str(newPortIndex)+" Packet type "+(str(isDelete))+ " Bitmask "+str(bitmask))

        rawPktContent = (255).to_bytes(2,'big') # first 2 byte egressport and padding
        if(isDelete == True):
            rawPktContent = rawPktContent + (128).to_bytes(1,'big')
            topKPathFalgs = 128
        else:
            rawPktContent = rawPktContent + (0).to_bytes(1,'big')
            topKPathFalgs = 0
        # rawPktContent = rawPktContent + (linkID).to_bytes(4,'big')
        # rawPktContent = rawPktContent + (bitmask).to_bytes(4,'big')
        # rawPktContent = rawPktContent + (level_to_link_id_store_index).to_bytes(4,'big')

        packet_out_req = p4runtime_pb2.StreamMessageRequest()
        packet_out_port_hex = packet_out_port.to_bytes(length=2, byteorder="big")
        packet_out = p4runtime_pb2.PacketOut()
        egress_physical_port = packet_out.metadata.add()
        egress_physical_port.metadata_id = 1
        egress_physical_port.value = packet_out_port_hex

        topKPathFalgs_metadata_field = packet_out.metadata.add()
        topKPathFalgs_metadata_field.metadata_id = 3
        topKPathFalgs_metadata_field.value = (topKPathFalgs).to_bytes(1,'big')

        bitmask_metadata_field = packet_out.metadata.add()
        bitmask_metadata_field.metadata_id = 4
        bitmask_metadata_field.value = (bitmask).to_bytes(4,'big')

        rank_metadata_field = packet_out.metadata.add()
        rank_metadata_field.metadata_id = 5
        rank_metadata_field.value = (rank).to_bytes(4,'big')

        port_metadata_field = packet_out.metadata.add()
        port_metadata_field.metadata_id = 6
        port_metadata_field.value = (port).to_bytes(4,'big')

        rankMaxIndex_metadata_field = packet_out.metadata.add()
        rankMaxIndex_metadata_field.metadata_id = 7
        rankMaxIndex_metadata_field.value = (rankMaxIndex).to_bytes(4,'big')

        rankMinIndex_metadata_field = packet_out.metadata.add()
        rankMinIndex_metadata_field.metadata_id = 8
        rankMinIndex_metadata_field.value = (rankMinIndex).to_bytes(4,'big')

        newPortIndex_metadata_field = packet_out.metadata.add()
        newPortIndex_metadata_field.metadata_id = 9
        newPortIndex_metadata_field.value = (newPortIndex).to_bytes(4,'big')

        packet_out.payload = rawPktContent
        packet_out_req.packet.CopyFrom(packet_out)
        return packet_out_req

    def insertPort(self, port, k):
        '''
        This function inserts the port at K'th rank
        :param port:
        :param k:
        :return:
        '''
        if(k>self.maxRank):
            logger.error("given  rank is more than the system's available rank. so can't insert the port")
            return None
        if((self.rankToCounterMap.get(k) != None) and (self.rankToCounterMap.get(k) != None) and  (self.rankToCounterMap.get(k) >= (self.maxRank-1))):
            print("Already k memebers in the group. Yoo may enter the port into next group")
            return None
        oldRank = self.portToRankMap.get(port)
        if((oldRank != None) and (oldRank > ConfConst.INVALID) and  (oldRank != k)):
            logger.info(self.p4dev.devName+"-Old rank of port "+str(port)+" is: "+str(oldRank)+" and new rank is: "+str(k))
            logger.info("This can not happen. Please Debug. !!!!")
            return None
        if((oldRank != None) and (oldRank > ConfConst.INVALID) and  (oldRank==k)):
            logger.info(self.p4dev.devName+"-The port is already in rank-"+str(k))
            # print(self.p4dev.devName+"-The port is already in rank-",k)
            return None

        oldIndex = self.portToIndexAtCurrentRankMap.get(port)
        if((oldIndex != None) and (oldIndex >0) and (oldIndex!= (self.rankToCounterMap[k] + 1))):
            logger.info(self.p4dev.devName+"-Old index of port "+str(port)+" is: "+str(oldIndex)+" and new index is: "+str(self.rankToCounterMap.get(k)))
            logger.info("This can not happen. Please Debug. Exiting the thread!!!!")
            return None
        self.portToRankMap[port] = k
        self.rankToCounterMap[k] = self.rankToCounterMap.get(k) + 1
        self.rankToPortAtMaxIndexMap[k] = port
        self.portToIndexAtCurrentRankMap[port] = self.rankToCounterMap.get(k)
        self.rankToPort2dMap.get(k)[self.rankToCounterMap.get(k)] = port
        #next we need to build the control message
        #row = k, column = self.rankToCounterMap[k]
        #kth bit in bitmask will be 1
        pktForInsertPort = self.buildMetadataBasedPacketOut(isDelete=False,   rank = k, port = port, rankMinIndex=self.getMinIndex(k),
                        rankMaxIndex = self.getMaxIndex(rank=k), newPortIndex=self.getMaxIndex(rank=k),bitmask = self.getBitmask())
        # logger.info("Inserting port: "+str(port)+" at rank: "+str(k)+" is done. rank to port map is "+str(self.rankToPort2dMap))

        return pktForInsertPort

    def getBitmask(self):
        bmask = 0
        for k in self.rankToCounterMap.keys():
            if self.rankToCounterMap.get(k) >-1:
                bmask = modifyBit(bmask, k, 1)
        return bmask
    def getMinIndex(self, rank):
        if self.rankToCounterMap.get(rank)> -1:
            return rank * self.maxRank
        else:
            return rank * self.maxRank
    def getMaxIndex(self, rank):
        if self.rankToCounterMap.get(rank)> -1:
            return rank * self.maxRank + self.rankToCounterMap.get(rank)
        else:
            return rank * self.maxRank

    def deletePort(self, port):
        '''
        This function deletes port from the CP data strucutre and  builds a control message to delete the port from data plane
        At any point of execution if it finds any inconsistency, it exits the thread at control plnae to keep consistency intact
        :param port:
        :return:
        '''
        oldRank = self.portToRankMap.get(port)
        if(oldRank == None):
            logger.info(self.p4dev.devName+"-Old rank of port to be deleted("+str(port)+") is None. If you are deleting a port before inserting it then you are ok. otherwise There is some bug.")
            logger.info("To ensure consistency we are exiting.")
            return None
        oldIndex = self.portToIndexAtCurrentRankMap.get(port)
        if((oldIndex == None) ):
            logger.info(self.p4dev.devName+"-Old index of port "+str(port)+" to be deleted is None. This means the port is already not existing ")
            logger.info("This can not happen. Please Debug. !!!!")
            return None
        # logger.info("Port "+str(port)+" is being deleted from rank: "+str(oldRank))
        self.portToRankMap[port] = ConfConst.INVALID
        self.rankToCounterMap[oldRank] = self.rankToCounterMap.get(oldRank) - 1
        portAtMaxIndex = self.rankToPortAtMaxIndexMap.get(oldRank)
        # logger.info("Port at "+str(oldRank)+"'s max location is : "+str(portAtMaxIndex))
        newMaxIndexOfTheRank = self.portToIndexAtCurrentRankMap.get(portAtMaxIndex)-1

        self.portToIndexAtCurrentRankMap[port] = ConfConst.INVALID
        self.rankToPort2dMap[oldRank][oldIndex] = portAtMaxIndex
        #logger.info("Port at "+str(oldRank)+"'s max location: "+str(newMaxIndexOfTheRank)+" is now : "+str(self.rankToPort2dMap[oldRank][oldIndex]))
        # logger.info("Port at "+str(oldRank)+"'s max location: "+str(newMaxIndexOfTheRank)+" is now : "+str(self.rankToPort2dMap[oldRank][oldIndex]))
        #special case when we delete a port from a group. the port itself was the last port in the group. Need s[ecial test for that
        if(port == self.rankToPortAtMaxIndexMap[oldRank]):
            self.portToRankMap[port] = ConfConst.INVALID
            self.portToIndexAtCurrentRankMap[portAtMaxIndex] = ConfConst.INVALID #this case means we are deleting the last port of the group
        else:
            self.portToIndexAtCurrentRankMap[portAtMaxIndex] = oldIndex  #This is necessary because we are shifting it's location
        self.rankToPortAtMaxIndexMap[oldRank] = self.rankToPort2dMap.get(oldRank)[newMaxIndexOfTheRank]
        del self.portToRankMap[port]
        #row = oldRank, column = self.rankToCounterMap[k] --> in this location write self.rankToPortAtMaxIndexMap[oldRank]
        # if elements in oldRank is -1 then bit will be 0
        #When we delete the only element of the rank then newMaxIndexOfTheRank weill be -1. But we do not consider this as special case, because p4 programs will automatically
        #overlook those exception. so we do not think about that. but for other cases, this wil not be -1. so we are okay.
        pktForDeletePort = self.buildMetadataBasedPacketOut(isDelete=True, rank = oldRank, port = portAtMaxIndex,
                            rankMinIndex=self.getMinIndex(oldRank), rankMaxIndex = self.getMaxIndex(rank=oldRank),
                                                            newPortIndex= (oldRank * self.maxRank )+oldIndex,bitmask = self.getBitmask())
        # logger.info("Deleting port: "+str(port)+" from rank: "+str(oldRank)+" is done. rank to port map is "+str(self.rankToPort2dMap))


        return pktForDeletePort




def testDriverFunction():
    mgr = TopKPathManager(dev = None, k=8)
    mgr.printDS()
    # mgr.insertPort(port = 4, k =1)
    # mgr.insertPort(port = 5, k =1)
    # mgr.deletePort(port = 4)
    mgr.printDS()
    # mgr.insertPort(port = 5, k =1)
    # mgr.insertPort(port = 6, k =1)
    # mgr.printDS()
    # mgr.deletePort(port = 5)
    # mgr.insertPort(port = 7, k =1)
    # mgr.insertPort(port = 8, k =1)
    # mgr.insertPort(port = 9, k =1)
    # mgr.insertPort(port = 10, k =1)
    # mgr.insertPort(port = 11, k =1)
    # mgr.insertPort(port = 12, k =1)
    # mgr.insertPort(port = 13, k =2)
    # mgr.deletePort(port = 7)
    # mgr.insertPort(port = 14, k =7)
    # mgr.deletePort(port = 12)
    # mgr.deletePort(port = 13)
    # mgr.insertPort(port = 23, k =2)
    # mgr.insertPort(port = 13, k =2)
    # mgr.deletePort(port = 8)
    # mgr.deletePort(port = 4)
    # mgr.insertPort(port=4, k = 5)
    # mgr.insertPort(port=4, k = 5)
    # mgr.printDS()

# testDriverFunction()


# port insert contro message
# ----- btimask --simply if rankTocounterMap of rank is >=0 thenset bit 1
# ----- rank, counter value -- only on which rank the port was added. at dp at rank'th location' the counter value will be written
# ----- (row column port) and port value index to write the port in 2D map. row is already given as rank, just provide the column location. maxindex of the rank is that location and port is port
#
# port delete control message
# ----- btimask --simply if rankTocounterMap of rank is >=0 thenset bit 1
# ----- rank, counter value -- only from which rank the port was deleted. at dp at rank'th colcation' the counter value will be written
# ----- (row column) index to write the port in 2D map. row is already given as rank, just provide the column location. new maxindex of the rank is that location and port is the port that was replaced from maxlocation
#


# Test case:
# insert only one port in a rank -- then delete it
# insert max number of ports in a rank and then delete the last element
# insert max number of ports in a rank and then delete the first element
#
#
# due to necessity of write of bitmask and rank to countermao we can not only paralllize only the last step of 2d map writing. we also need to parallelieze the
# ranktocounter value wirintg. so in one step we can only achieve 10 writing.