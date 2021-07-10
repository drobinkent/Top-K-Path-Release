# For accuracy test presented in the paper go to the "top-k-path-Accuracy" folder. Rename it to "Top-K-_path" and follow the Readme.md file inside that folder. 

# For the stateful memory consumption comparison presented in the paper look at "StatefulMemoryConsumptionCalculator.py" 



# For performance improvement section of the paper. at first look at the "top-k-path-Accuracy/Top-K-Path/Readme.md" to understand how to start and run the mininet based testbed. 
    
    Then look at follwoing part 

We have generated traffic flow configuration (where flow arrival time is generated from Poisson distribution and the traffic load is generated 
according the a real life data center workload) 




In Top-K-Path/MininetSimulator/ClosConstants.py file change the file name that you want to use the simulate the traffic. Here as an 
example we have simulated the traffic to generate 0.8 load factor fo the network. you can change the file name to generate a different workload.  

    TCP_SERVER_COMAND_FILE = "Top-K-Path/testAndMeasurement/TEST_RESULTS/FlowInfos/WebSearchWorkLoad_load_factor_0.8.serverdat"
    TCP_CLIENT_COMAND_FILE = "Top-K-Path/testAndMeasurement/TEST_RESULTS/FlowInfos/WebSearchWorkLoad_load_factor_0.8.clientdat"


Then in  Top-K-Path/ConfigConst.py change  the data plane algorithm you want to use

    ALGORITHM_IN_USE = DataplnaeAlgorithm.DP_ALGO_BASIC_ECMP
    ALGORITHM_IN_USE = DataplnaeAlgorithm.DP_ALGO_BASIC_HULA
    ALGORITHM_IN_USE = DataplnaeAlgorithm.DP_ALGO_TOP_K_PATH

Use whichever algorithm you want to use. 