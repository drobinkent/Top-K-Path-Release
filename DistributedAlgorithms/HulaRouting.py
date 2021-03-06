import logging
import logging.handlers
import math
import threading
import time

import ConfigConst
import DistributedAlgorithms.Testingconst as tstConst
import P4Runtime.P4DeviceManager as jp
import P4Runtime.leafSwitchUtils as leafUtils
import P4Runtime.spineSwitchUtils as  spineUtils
import P4Runtime.superSpineSwitchUtils as  superSpineUtils
import P4Runtime.SwitchUtils as swUtils
import InternalConfig
import P4Runtime.shell as sh
import InternalConfig as intCoonfig
from DistributedAlgorithms.RoutingInfo import RoutingInfo
import ConfigConst as ConfConst
logger = logging.getLogger('Shell')
logger.handlers = []
hdlr = logging.handlers.RotatingFileHandler(ConfConst.CONTROLLER_LOG_FILE_PATH, maxBytes = ConfConst.MAX_LOG_FILE_SIZE , backupCount= ConfConst.MAX_LOG_FILE_BACKUP_COUNT)
hdlr.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logging.StreamHandler(stream=None)
logger.setLevel(logging.INFO)

class HulaRouting:

    def __init__(self, dev):
        self.p4dev = dev
        self.delayBasedRoutingInfo = RoutingInfo(name = "Delay Based Routing Info Store")
        self.egressQueueDepthBasedRoutingInfo = RoutingInfo(name = "Egress queue Depth Based Routing Info Store")
        pass

    def setup(self, nameToSwitchMap):
        '''
        This function setup all the relevant stuffs for running the algorithm
        '''

        # if self.p4dev.fabric_device_config.switch_type == jp.SwitchType.LEAF:
        #     leafUtils.addUpStreamRoutingGroupForLeafSwitch(self.p4dev, list(self.p4dev.portToSpineSwitchMap.keys())) #this creates a group for upstream routing with  group_id=InternalConfig.LEAF_SWITCH_UPSTREAM_PORTS_GROUP
        #     self.p4dev.addLPMMatchEntryWithGroupAction( tableName = "IngressPipeImpl.upstream_ecmp_routing_control_block.upstream_routing_table", fieldName = "hdr.ipv6.dst_addr",
        #                                           fieldValue= InternalConfig.DCN_CORE_IPv6_PREFIX, prefixLength = InternalConfig.DCN_CORE_IPv6_PREFIX_LENGTH,
        #                                           actionName="IngressPipeImpl.upstream_ecmp_routing_control_block.set_upstream_egress_port", actionParamName=None, actionParamValue=None,
        #                                           groupID = InternalConfig.LEAF_SWITCH_UPSTREAM_PORTS_GROUP, priority = None)
        #     return
        # elif self.p4dev.fabric_device_config.switch_type == jp.SwitchType.SPINE:
        #     spineUtils.addUpStreamRoutingGroupForSpineSwitch(self.p4dev, list(self.p4dev.portToSuperSpineSwitchMap.keys()))  #this creates a group for upstream routing with  group_id=InternalConfig.SPINE_SWITCH_UPSTREAM_PORTS_GROUP
        #     self.p4dev.addLPMMatchEntryWithGroupAction( tableName = "IngressPipeImpl.upstream_ecmp_routing_control_block.upstream_routing_table", fieldName = "hdr.ipv6.dst_addr",
        #                                           fieldValue= InternalConfig.DCN_CORE_IPv6_PREFIX, prefixLength = InternalConfig.DCN_CORE_IPv6_PREFIX_LENGTH,
        #                                           actionName="IngressPipeImpl.upstream_ecmp_routing_control_block.set_upstream_egress_port", actionParamName=None, actionParamValue=None,
        #                                           groupID = InternalConfig.SPINE_SWITCH_UPSTREAM_PORTS_GROUP, priority = None)
        #     pass
        # elif self.p4dev.fabric_device_config.switch_type == jp.SwitchType.SUPER_SPINE:
        #     pass
        self.nameToSwitchMap = nameToSwitchMap
        self.p4dev.setupHULAUpstreamRouting(self.nameToSwitchMap)
        if self.p4dev.fabric_device_config.switch_type == intCoonfig.SwitchType.LEAF:
            self.link_reconfiguration_thread = threading.Thread(target=self.linkReconfigurator, args=())
            self.link_reconfiguration_thread.start()
            logger.info("TopKpathrouting link_reconfiguration_thread  started")
        return

    def linkReconfigurator(self):
        time.sleep(25)
        i = 0
        # if(self.p4dev.devName != "device:p0l0"):
        #     return
        while(True):
            j = i % len(tstConst.MULTI_TENANCY_PORT_RATE_CONFIGS)
            portRates = tstConst.MULTI_TENANCY_PORT_RATE_CONFIGS[j]
            logger.info("PortRates are : "+str(portRates))
            rankInsertedIncurrentIteration = {}
            for k in range (0,len(portRates)):
                print(portRates[k])
                port = portRates[k][0]
                rate = int(math.floor(portRates[k][1] * ConfConst.queueRateForSpineFacingPortsOfLeafSwitch))
                bufferSize = int(math.floor(ConfigConst.QUEUE_RATE_TO_QUEUE_DEPTH_FACTOR * rate))
                if(bufferSize<200):
                    bufferSize = 200
                setPortQueueRatesAndDepth(dev = self.p4dev, port = port, queueRate = rate , bufferSize = ConfigConst.QUEUE_RATE_TO_QUEUE_DEPTH_FACTOR)
            time.sleep(ConfigConst.MULTITENANCY_RATE_RECONFIGURATION_INTERVAL)
            i=i+1

    def processFeedbackPacket(self, parsedPkt, dev):
        #print("Called the algo")
        #TODO: for each of the different types of the packet, we have to write a separate function to process them
        # self.ingress_port= packet.metadata[0];
        # self._pad= packet.metadata[1];
        # self.ingress_queue_event= packet.metadata[2];   -- type 1
        # self.ingress_queue_event_data= packet.metadata[3];
        # self.egress_queue_event= packet.metadata[4];  -- type 2
        # self.egress_queue_event_data= packet.metadata[5];
        # self.ingress_traffic_color= packet.metadata[6];  --   -- type 3 . if color is 0 then green, then we may not need to do anything. Here color itself shows the event
        # self.ingress_rate_event_data= packet.metadata[7];
        # self.egress_traffic_color= packet.metadata[8];   -- same as ingress traffic color
        # self.egress_rate_event_data= packet.metadata[9];
        # self.path_delay_event_type= packet.metadata[11];  # -- type 4 delay event
        # self.delay_event_src_type= packet.metadata[10];
        # self.path_delay_event_data= packet.metadata[12];
        # self.dest_IPv6_address= packet.metadata[13];
        # if parsedPkt.ingress_queue_event >0:
        #     print("Valid ingress_queue_event :"+str(parsedPkt.ingress_queue_event))
        # if parsedPkt.egress_queue_event >0:
        #     print("Valid egress_queue_event"+str(parsedPkt.egress_queue_event))
        # if parsedPkt.ingress_traffic_color >0:
        #     print("Valid ingress_traffic_color :"+ str(parsedPkt.ingress_traffic_color))
        # if parsedPkt.egress_traffic_color >0:
        #     print("Valid ingress_traffic_color :"+str(parsedPkt.egress_traffic_color))
        # if parsedPkt.path_delay_event_type >0:
        #     print("Valid path_delay_event_type :"+str(parsedPkt.path_delay_event_type))
        pass

def setPortQueueRatesAndDepth(dev, port, queueRate, bufferSize):
    cmdString = ""
    cmdString = cmdString+  "set_queue_rate "+str(queueRate)+ " "+str(port)+"\n"
    dev.executeCommand(cmdString)
    cmdString = ""
    cmdString = cmdString+  "set_queue_depth "+str(bufferSize)+ " "+str(port)+"\n"
    dev.executeCommand(cmdString)
    # logger.info("Executing queuerate and depth setup commmand for device "+ str(dev))
    # logger.info("command is: "+cmdString)
    #dev.executeCommand(cmdString)

