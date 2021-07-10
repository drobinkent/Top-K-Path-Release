import logging.handlers


import logging.handlers
import math
import threading
import time

import ConfigConst
import DistributedAlgorithms.Testingconst as tstConst
import ConfigConst as ConfConst
import InternalConfig
import InternalConfig as intCoonfig
from DistributedAlgorithms.TopKPathManager import TopKPathManager



logger = logging.getLogger('Shell')
logger.handlers = []
hdlr = logging.handlers.RotatingFileHandler(ConfConst.CONTROLLER_LOG_FILE_PATH, maxBytes = ConfConst.MAX_LOG_FILE_SIZE , backupCount= ConfConst.MAX_LOG_FILE_BACKUP_COUNT)
hdlr.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logging.StreamHandler(stream=None)
logger.setLevel(logging.INFO)



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

class ECMPRouting:

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





    def setup(self,nameToSwitchMap):
        '''
        This function setup all the relevant stuffs for running the algorithm
        '''
        self.p4dev.setupECMPUpstreamRouting()
        if self.p4dev.fabric_device_config.switch_type == intCoonfig.SwitchType.LEAF:
            self.link_reconfiguration_thread = threading.Thread(target=self.linkReconfigurator, args=())
            self.link_reconfiguration_thread.start()
            logger.info("ECMP Routing link_reconfiguration_thread  started")

        return

    def processFeedbackPacket(self, parsedPkt, dev):
        #print("Called the algo")
        #TODO: for each of the different types of the packet, we have to write a separate function to process them
        pass


    def linkReconfigurator(self):
        time.sleep(25)
        i = 0
        # if(self.p4dev.devName != "device:p0l0"):
        #     return
        while(True):
            j = i % len(tstConst.MULTI_TENANCY_PORT_RATE_CONFIGS)
            portRates = tstConst.MULTI_TENANCY_PORT_RATE_CONFIGS[j]
            # logger.info("PortRates are : "+str(portRates))
            rankInsertedIncurrentIteration = {}
            for k in range (0,len(portRates)):
                print(portRates[k])
                port = portRates[k][0]
                rate = int(math.floor(portRates[k][1] * ConfConst.queueRateForSpineFacingPortsOfLeafSwitch))
                bufferSize = int(math.floor(ConfigConst.QUEUE_RATE_TO_QUEUE_DEPTH_FACTOR * rate))
                if(bufferSize<200):
                    bufferSize = 200
                rank = getRank(portRates[k][1])
                # logger.info("Port "+str(port)+ " rate :"+str(portRates[k][1])+" rank:"+str(rank))
                setPortQueueRatesAndDepth(dev = self.p4dev, port = port, queueRate = rate , bufferSize = ConfigConst.QUEUE_RATE_TO_QUEUE_DEPTH_FACTOR)
            time.sleep(ConfigConst.MULTITENANCY_RATE_RECONFIGURATION_INTERVAL)
            i=i+1

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