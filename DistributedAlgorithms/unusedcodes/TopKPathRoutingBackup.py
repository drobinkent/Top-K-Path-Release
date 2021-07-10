import logging.handlers
import threading
import time

import ConfigConst
import DistributedAlgorithms.Testingconst as tstConst
import ConfigConst as ConfConst
import InternalConfig
import InternalConfig as intCoonfig
from DistributedAlgorithms.TopKPathManager import TopKPathManager
import P4Runtime.SwitchUtils as swUtils
from TestCaseDeployer import TestCommandDeployer

logger = logging.getLogger('Shell')
logger.handlers = []
hdlr = logging.handlers.RotatingFileHandler(ConfConst.CONTROLLER_LOG_FILE_PATH, maxBytes = ConfConst.MAX_LOG_FILE_SIZE , backupCount= ConfConst.MAX_LOG_FILE_BACKUP_COUNT)
hdlr.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logging.StreamHandler(stream=None)
logger.setLevel(logging.INFO)


def getRank(pathUtil):
    rankList = []
    if(pathUtil>=0) and (pathUtil <= 0.125):
        return 0
    if(pathUtil>0.125) and (pathUtil <= 0.250):
        return 1
    if(pathUtil>0.250) and (pathUtil <= 0.375):
        return 2
    if(pathUtil>0.375) and (pathUtil <= .500):
        return 3
    if(pathUtil>0.500) and (pathUtil <= .625):
        return 4
    if(pathUtil>0.625) and (pathUtil <= .750):
        return 5
    if(pathUtil>0.750) and (pathUtil <= .875):
        return 6
    if(pathUtil>0.875) and (pathUtil <= .1000):
        return 7
    return 0

class TopKPathRouting:

    def __init__(self, dev):
        self.p4dev = dev
        self.testOperationIndex =0
        if self.p4dev.fabric_device_config.switch_type == intCoonfig.SwitchType.LEAF:
            #self.topKPathManager = TopKPathManager(dev = self.p4dev, k=len(self.p4dev.portToSpineSwitchMap.keys()))
            self.topKPathManager = TopKPathManager(dev = self.p4dev, k=ConfConst.K)
        elif self.p4dev.fabric_device_config.switch_type == intCoonfig.SwitchType.SPINE:
            # self.topKPathManager = TopKPathManager(dev = self.p4dev, k=len(self.p4dev.portToSuperSpineSwitchMap.keys()))
            self.topKPathManager = TopKPathManager(dev = self.p4dev, k=ConfConst.K)
        elif self.p4dev.fabric_device_config.switch_type == intCoonfig.SwitchType.SUPER_SPINE:
            self.topKPathManager = TopKPathManager(dev = self.p4dev, k=ConfConst.K) # by default add space for 16 ports in super spine. This is not actually used in our simulation
            pass

        return
    def initMAT(self, switchObject, bitMaskLength):
        allOneMAsk = BinaryMask(bitMaskLength)
        allOneMAsk.setAllBitOne()
        allOneMAskBinaryString = allOneMAsk.getBinaryString()
        for j in range(0, bitMaskLength):
            mask = BinaryMask(bitMaskLength)
            mask.setNthBitWithB(n=j,b=1)
            maskAsString = mask.getBinaryString()
            switchObject.addTernaryMatchEntry( "IngressPipeImpl.k_path_selector_control_block.kth_path_finder_mat",
                                               fieldName = "local_metadata.kth_path_selector_bitmask",
                                               fieldValue = allOneMAskBinaryString, mask = maskAsString,
                                               actionName = "IngressPipeImpl.k_path_selector_control_block.kth_path_finder_action_with_param",
                                               actionParamName = "rank",
                                               actionParamValue = str(j), priority=bitMaskLength-j+1)





    def setup(self,nameToSwitchMap):
        '''
        This function setup all the relevant stuffs for running the algorithm
        '''
        startingRankForTestingTopKPathProblem = 0
        #swUtils.setupFlowtypeBasedIngressRateMonitoringForKPathProblem(self.p4dev)
        self.initMAT(self.p4dev, ConfConst.K)
        if self.p4dev.fabric_device_config.switch_type == intCoonfig.SwitchType.LEAF:
            rankOrder = [4,6,8] # best 4 paths will be in rank 0, then 2 in next rank and so on
            portList = list(self.p4dev.portToSpineSwitchMap.keys())
            i=0
            while i < len(portList):
                for r in range(0,len(rankOrder)):
                    if i < rankOrder[r]:
                        port = portList[i]
                        insertPkt = self.topKPathManager.insertPort(port, r)
                        self.p4dev.send_already_built_control_packet_for_top_k_path(insertPkt)
                i = i+1
        elif self.p4dev.fabric_device_config.switch_type == intCoonfig.SwitchType.SPINE:
            rankOrder = [4,6,8] # best 4 paths will be in rank 0, then 2 in next rank and so on
            portList = list(self.p4dev.portToSuperSpineSwitchMap.keys())
            i=0
            while i < len(portList):
                for r in range(0,len(rankOrder)):
                    if i < rankOrder[r]:
                        port = portList[i]
                        insertPkt = self.topKPathManager.insertPort(port, r)
                        self.p4dev.send_already_built_control_packet_for_top_k_path(insertPkt)
                i = i+1
        elif self.p4dev.fabric_device_config.switch_type == intCoonfig.SwitchType.SUPER_SPINE:
            self.topKPathManager = TopKPathManager(dev = self.p4dev, k=ConfConst.K) # by default add space for 16 ports in super spine. This is not actually used in our simulation
            pass

        return

    def processFeedbackPacket(self, parsedPkt, dev):
        #print("Called the algo")
        #TODO: for each of the different types of the packet, we have to write a separate function to process them
        pass

    def p4kpUtilBasedReconfigureForLeafSwitches(self, linkUtilStats, oldLinkUtilStats):
        # logger.info("CLB ALGORITHM: For switch "+ self.p4dev.devName+ "new Utilization data is  "+str(linkUtilStats))
        # logger.info("CLB ALGORITHM: For switch "+ self.p4dev.devName+ "old Utilization data is  "+str(oldLinkUtilStats))
        pathAndUtilist = []
        for i in range (int(ConfConst.MAX_PORTS_IN_SWITCH/2), ConfConst.MAX_PORTS_IN_SWITCH):
            index = i
            utilInLastInterval = (linkUtilStats[index] -  oldLinkUtilStats[index])/ConfigConst.queueRateForSpineFacingPortsOfLeafSwitch
            # rankInLastInterval = self.topKPathManager.portToRankMap.get(i)
            # pathAndUtilist.append((i,utilInLastInterval,rankInLastInterval))
            pathAndUtilist.append((i+1,utilInLastInterval))
        pathAndUtilist.sort(key=lambda x:x[1])
        # if(self.p4dev.devName == ConfConst.CLB_TESTER_DEVICE_NAME):
        #     print("For device "+self.p4dev.devName+" The port utilization data according to rank is "+str(pathAndUtilist))
        controlPacketList = []
        portConfiguredIncurrentIteration = {}
        for i in range (0, len(pathAndUtilist)):
            port = pathAndUtilist[i][0]
            if(portConfiguredIncurrentIteration.get(port)== None):
                dltPkt = self.topKPathManager.deletePort(port)
                controlPacketList.append(dltPkt)
                # self.p4dev.send_already_built_control_packet_for_top_k_path(dltPkt)
            # insertPkt = self.topKPathManager.insertPort(port, getRank(pathAndUtilist[i][1]))
            # controlPacketList.append(insertPkt)
            # portConfiguredIncurrentIteration[port] = port

            if(i==(len(pathAndUtilist))-1):
                insertPkt = self.topKPathManager.insertPort(port, getRank(pathAndUtilist[i][1]))
                controlPacketList.append(insertPkt)
            else:
                insertPkt = self.topKPathManager.insertPort(port, i)
                controlPacketList.append(insertPkt)

        # rankOrder = [4,6,8] # best 4 paths will be in rank 0, then 2 in next rank and so on
        # i=0
        # portConfiguredIncurrentIteration = {}
        # while i < len(pathAndUtilist):
        #     for r in range(0,len(rankOrder)):
        #         if i < rankOrder[r]:
        #             port = pathAndUtilist[i][0]
        #             if(portConfiguredIncurrentIteration.get(port)== None):
        #                 dltPkt = self.topKPathManager.deletePort(port)
        #                 self.p4dev.send_already_built_control_packet_for_top_k_path(dltPkt)
        #                 insertPkt = self.topKPathManager.insertPort(port, r)
        #                 self.p4dev.send_already_built_control_packet_for_top_k_path(insertPkt)
        #                 portConfiguredIncurrentIteration[port] = port
        #             else:
        #                 insertPkt = self.topKPathManager.insertPort(port, r)
        #                 self.p4dev.send_already_built_control_packet_for_top_k_path(insertPkt)
        #                 portConfiguredIncurrentIteration[port] = port
        #     i = i+1
        # for ctrlPkt in controlPacketList:
        #     self.p4dev.send_already_built_control_packet_for_top_k_path(ctrlPkt)



    def topKpathroutingTesting(self):
        time.sleep(25)
        i = 0
        while(True):
            j = i % len(tstConst.TOP_K_PATH_EXPERIMENT_PORT_RATE_CONFIGS)
            if(self.p4dev.devName != "device:p0l0"):
                return
            portCfg = tstConst.TOP_K_PATH_EXPERIMENT_PORT_RATE_CONFIGS[j]
            time.sleep(portCfg[0])
            for k in range(0,len(portCfg[1])): # k gives the rank iteslf as the port configs are already sorted
                if self.p4dev.fabric_device_config.switch_type == InternalConfig.SwitchType.LEAF:
                    port =portCfg[1][k][0]
                    portRank = portCfg[1][k][1]
                    portRate = portCfg[1][k][2]
                    bufferSize = portCfg[1][k][3]
                    setPortQueueRatesAndDepth(self.p4dev, port, portRate, bufferSize)
                if self.p4dev.fabric_device_config.switch_type == InternalConfig.SwitchType.SPINE:
                    port =portCfg[1][k][0]
                    portRank = portCfg[1][k][1]
                    portRate = portCfg[1][k][2]
                    bufferSize = portCfg[1][k][3]
                dltPkt = self.topKPathManager.deletePort(port)
                self.p4dev.send_already_built_control_packet_for_top_k_path(dltPkt)
                if(portRate> 0): # if 0 that means the port is not down . So need to iinsert it. but for rate < 0 we delete the port but do not insert it agian to simulate delete behavior
                    insertPkt = self.topKPathManager.insertPort(port, portRank)
                    self.p4dev.send_already_built_control_packet_for_top_k_path(insertPkt)
                else:
                    logger.info("Port : "+str(port)+" will not be configured into system as it's rate is <0 = ")
            print("Installed routes ",portCfg)
            topologyConfigFilePath =  ConfConst.TOPOLOGY_CONFIG_FILE
            # if(self.p4dev.devName == "device:p0l0"):
            #     testEvaluator = TestCommandDeployer(topologyConfigFilePath,
            #                                         "/home/deba/Desktop/Top-K-Path/testAndMeasurement/TestConfigs/TopKPathTesterWithTopKPath.json",
            #                                         ConfConst.IPERF3_CLIENT_PORT_START, ConfConst.IPERF3_SERVER_PORT_START, testStartDelay= 5)
            # testEvaluator.setupTestCase()
            i = i+ 1


            # after reconfiguration start the testcase with 3 special flows





class BinaryMask:
    def __init__(self, length):
        self.bits=[]
        self.length = length
        for i in range(0,self.length):
            self.bits.append(0)

    def setNthBitWithB(self,n,b):
        self.bits[(len(self.bits) - 1 )-n] = b
    def setAllBitOne(self):
        for i in range(0,self.length):
            self.bits[i]  = 1

    def setAllBitMinuxOneEqualX(self):
        for i in range(0,self.length):
            self.bits[i]  = -1

    def getBinaryString(self):
        val = "0b"
        for i in range(0, self.length):
            if(self.bits[i] == 0):
                val = val + "0"
            elif (self.bits[i] == 1):
                val = val + "1"
            else:
                val = val + "X"
        return  val


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

def setPortQueueRatesAndDepth(dev, port, queueRate, bufferSize):
    cmdString = ""
    cmdString = cmdString+  "set_queue_rate "+str(queueRate)+ " "+str(port)+"\n"
    dev.executeCommand(cmdString)
    cmdString = ""
    cmdString = cmdString+  "set_queue_depth "+str(bufferSize)+ " "+str(port)+"\n"
    dev.executeCommand(cmdString)
    logger.info("Executing queuerate and depth setup commmand for device "+ str(dev))
    logger.info("command is: "+cmdString)
    #dev.executeCommand(cmdString)