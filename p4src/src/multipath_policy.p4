#include <core.p4>

#include <v1model.p4>
#include "CONSTANTS.p4"
#include "headers.p4"
#include "parser.p4"


#ifndef MULTIPATH_POLICY
#define MULTIPATH_POLICY
control multipath_policy(inout parsed_headers_t    hdr,
                        inout local_metadata_t    local_metadata,
                        inout standard_metadata_t standard_metadata)
{

}

#endif





Assume we want to maintain K-path policy for 3 traffic classes. So we have to matinatin K-path for all 3 classes.
at first based on traffic class the id is defined (0 to 2 for 3 traffic classes) then corrsponding bitmask and in next stage level to link store
indexes are also mltiplied by traffic class index. Let's call the aggregationLayerIndex (agrInd).

Now if we want to keep seperate k path for ToR switches in data center. Assume 10k Tor n a dcn. then agrInd will be 0-9999.


Assume we are using Contra/Mp-hula style probe based monitoring for local data plane by the local cpu. After each interval the probes reports
what percentage of a link capacity is available or not. Based on that assume, the administrator wants to use link-5 for 40% of traffic of short flows,
30% of short flows through port 6, 20% through


need to implement 2 things a) agrIdx support in level to link store b) another table for header field to agrIdx mapping