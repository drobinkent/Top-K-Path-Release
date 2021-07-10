#include <core.p4>

#include <v1model.p4>
#include "CONSTANTS.p4"
#include "headers.p4"
#include "parser.p4"


#ifndef TOP_K_PATH_SELECTIOR
#define TOP_K_PATH_SELECTIOR
control k_path_selector(inout parsed_headers_t    hdr,
                        inout local_metadata_t    local_metadata,
                        inout standard_metadata_t standard_metadata)
{
    action best_path_finder_action_without_param() {
        local_metadata.best_path_rank =INVALID_RANK;
        local_metadata.flag_hdr.best_path_finderMat_hit = false;
    }
    action best_path_finder_action_with_param(bit<16> rank) {
        local_metadata.best_path_rank = rank;
        local_metadata.flag_hdr.best_path_finderMat_hit = true;
    }
    table best_path_finder_mat {
        key = {
            local_metadata.best_path_selector_bitmask: ternary;
        }
        actions = {
            best_path_finder_action_without_param;
            best_path_finder_action_with_param;
        }
        default_action = best_path_finder_action_without_param;
    }

    action worst_path_finder_action_with_param(bit<16> rank) {
        local_metadata.worst_path_rank =rank;
        local_metadata.flag_hdr.worst_path_finderMat_hit = true;

    }
    action worst_path_finder_action_without_param() { //we do not neeeed this bcz our bitmask will lways give us a path
        local_metadata.worst_path_rank =INVALID_RANK;
        local_metadata.flag_hdr.worst_path_finderMat_hit = false;
    }

    table worst_path_finder_mat {
        key = {
            local_metadata.worst_path_selector_bitmask: ternary;
        }
        actions = {
            worst_path_finder_action_with_param;
            worst_path_finder_action_without_param;
        }
        default_action = worst_path_finder_action_without_param;
    }

    action kth_path_finder_action_with_param(bit<16> rank) {
        local_metadata.kth_path_rank =rank;
        local_metadata.flag_hdr.kth_path_finderMat_hit = true;
    }
    action kth_path_finder_action_without_param() {
        local_metadata.kth_path_rank =0;
        local_metadata.flag_hdr.kth_path_finderMat_hit = false;
    }

    table kth_path_finder_mat {
        key = {
            local_metadata.kth_path_selector_bitmask: ternary;
        }
        actions = {
            kth_path_finder_action_without_param;
            kth_path_finder_action_with_param;
        }
        default_action = kth_path_finder_action_without_param;
    }




    apply {
         {
            //destination calculation
            //bit<32> destination_index = (bit<32>)hdr.ipv6.dst_addr[31:16] ; //rightmost 16 bit shows the ToR ID in our scheme. This basically dones nonthing. just a casting
            //And used for doccumentatin purpose. we can directly use the 8 bits of tor id. no need to take xtra variable


            bit<K> stored_bitmask_read_value = 0;
            stored_bitmask.read(stored_bitmask_read_value, (bit<32>)0);
            local_metadata.best_path_selector_bitmask =  ALL_1_256_BIT[K-1:0];
            //log_msg("traffic class is {}", {hdr.ipv6.traffic_class});
            //log_msg("Stored bitmask after read is {}",{stored_bitmask_read_value});
            //log_msg("kth path selector bitmask is {}",{local_metadata.kth_path_selector_bitmask});
            //bit<K> temp_mask = ALL_1_256_BIT[K-1:0] << local_metadata.rank_of_path_to_be_searched;
            //log_msg("All 1 bitmask bitmask after is shifting {} times is  {}",{local_metadata.rank_of_path_to_be_searched, temp_mask});
            local_metadata.kth_path_selector_bitmask = stored_bitmask_read_value & local_metadata.kth_path_selector_bitmask ;
            //local_metadata.best_path_selector_bitmask = stored_bitmask_read_value;
            //local_metadata.worst_path_selector_bitmask = stored_bitmask_read_value;
            //log_msg("local_metadata.kth_path_selector_bitmask  after AND of stored_bitmask_read_value & local_metadata.kth_path_selector_bitmask is : {}",{local_metadata.kth_path_selector_bitmask});
            //best_path_finder_mat.apply();
            kth_path_finder_mat.apply();
            //worst_path_finder_mat.apply();
         }
    }
}


#endif










