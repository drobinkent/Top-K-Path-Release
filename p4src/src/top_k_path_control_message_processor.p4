#include <core.p4>

#include <v1model.p4>
#include "CONSTANTS.p4"
#include "headers.p4"
#include "parser.p4"

#ifndef TOP_K_PATH_CONTROL_MESSAGE
#define TOP_K_PATH_CONTROL_MESSAGE
control top_k_path_control_message_processor(inout parsed_headers_t    hdr,
                        inout local_metadata_t    local_metadata,
                        inout standard_metadata_t standard_metadata)
{


    apply{
        if(hdr.packet_out.top_k_path_flags[7:7] == (bit<1>)1){ //this is a delete message
            log_msg("TOPKPATH: Control Message for deleting port found");
            log_msg("Values in the message are rank-{} port- {} rank_max_index -{} rank_minIndex- {}, new_port_index-{} bitmask -- {}",
                {hdr.packet_out.rank, hdr.packet_out.port, hdr.packet_out.rank_max_index, hdr.packet_out.rank_min_index, hdr.packet_out.new_port_index, hdr.packet_out.bitmask  });
            stored_bitmask.write( (bit<32>)0, hdr.packet_out.bitmask[K - 1 :0]);
            rank_to_max_index.write((bit<32>)hdr.packet_out.rank, hdr.packet_out.rank_max_index);
            rank_to_min_index.write((bit<32>)hdr.packet_out.rank, hdr.packet_out.rank_min_index);
            //rank_to_port_map.write() this write is not needed as we will use select links based on max_location
            rank_to_port_map.write((bit<32>)hdr.packet_out.new_port_index, (bit<9>)hdr.packet_out.port);


        }else if (hdr.packet_out.top_k_path_flags[7:7] == (bit<1>)0){ //this is a add message
            log_msg("TOPKPATH: Control Message for inserting port found");
            log_msg("Values in the message are rank-{} port- {} rank_max_index -{} rank_minIndex- {}, new_port_index-{} bitmask -- {}",
                            {hdr.packet_out.rank, hdr.packet_out.port, hdr.packet_out.rank_max_index, hdr.packet_out.rank_min_index, hdr.packet_out.new_port_index, hdr.packet_out.bitmask  });
            stored_bitmask.write( (bit<32>)0, hdr.packet_out.bitmask[K - 1 :0]);
            rank_to_max_index.write((bit<32>)hdr.packet_out.rank, hdr.packet_out.rank_max_index);
            rank_to_min_index.write((bit<32>)hdr.packet_out.rank, hdr.packet_out.rank_min_index);
            rank_to_port_map.write((bit<32>)hdr.packet_out.new_port_index, (bit<9>)hdr.packet_out.port);

        }

    }
}

#endif