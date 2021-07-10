#include <core.p4>






#include <v1model.p4>
#include "CONSTANTS.p4"
#include "headers.p4"
#include "parser.p4"


#ifndef RANGE_TCAM_ROUTING_BLOCK
#define RANGE_TCAM_ROUTING_BLOCK
control range_tcam_upstream_routing(inout parsed_headers_t    hdr,
                        inout local_metadata_t    local_metadata,
                        inout standard_metadata_t standard_metadata)
{



     //======================================== Table for slecting path with minimum egress port rate ==========================================
    action egr_port_rate_based_upstream_path_selector_action_without_param() {
        standard_metadata.egress_spec = 0;


    }
    action egr_port_rate_based_upstream_path_selector_action_with_param(bit<9> port_num) {
        standard_metadata.egress_spec = port_num;
    }

    table egr_port_rate_based_upstream_path_table {
        key = {
            hdr.ipv6.dst_addr:          lpm;
            local_metadata.egr_port_rate_value_range : range;
        }
        actions = {
            egr_port_rate_based_upstream_path_selector_action_without_param;
            egr_port_rate_based_upstream_path_selector_action_with_param;
        }
        default_action = egr_port_rate_based_upstream_path_selector_action_without_param;

    }


    apply {
        if (hdr.ipv6.traffic_class == TRAFFIC_CLASS_LOW_DELAY){
            local_metadata.egr_port_rate_value_range = 1;
        }else if (hdr.ipv6.traffic_class == TRAFFIC_CLASS_HIGH_THROUGHPUT){
             local_metadata.egr_port_rate_value_range = 2;
        }else if (hdr.ipv6.traffic_class == TRAFFIC_CLASS_CUSTOM_QOS){
            local_metadata.egr_port_rate_value_range = 3;

        }else{
            local_metadata.egr_port_rate_value_range = 1;
        }

        if (hdr.ipv6.traffic_class == TRAFFIC_CLASS_LOW_DELAY){
            local_metadata.kth_path_selector_bitmask =  ALL_1_256_BIT[K-1:0] << 2;
        }else if (hdr.ipv6.traffic_class == TRAFFIC_CLASS_QOS1){
             local_metadata.kth_path_selector_bitmask =  ALL_1_256_BIT[K-1:0] << 0;
        }else if (hdr.ipv6.traffic_class == TRAFFIC_CLASS_QOS2){
            bit<K> tempMask = ALL_1_256_BIT[K-1:0] <<1;
            local_metadata.kth_path_selector_bitmask = tempMask;

        }else{
            local_metadata.kth_path_selector_bitmask =  ALL_1_256_BIT[K-1:0]; //set it here
        }
        egr_port_rate_based_upstream_path_table.apply();
        //log_msg("Delay based selected path  {}", {local_metadata.delay_based_path});
    }

}
#endif







