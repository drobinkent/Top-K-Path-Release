p4-leaf-ecmp: p4src/src/leaf.p4
	$(info *** Building P4 program for the leaf switch...)
	@mkdir -p p4src/Build
	p4c-bm2-ss --arch v1model -o p4src/Build/leaf.json \
		--p4runtime-files p4src/Build/leaf_p4info.txt --Wdisable=unsupported \
		p4src/src/leaf.p4 -Dports=256 -DENABLE_DEBUG_TABLES -DDP_ALGO_ECMP -DECN_ENABLED -DK=4
	sudo cp ./p4src/Build/leaf.json /tmp/
	sudo cp ./p4src/Build/leaf_p4info.txt /tmp/
	@echo "*** P4 program for leaf switch compiled successfully! Output files are in p4src/Build"

p4-spine-ecmp: p4src/src/spine.p4
	$(info *** Building P4 program for the spine switch...)
	@mkdir -p p4src/Build
	p4c-bm2-ss --arch v1model -o p4src/Build/spine.json \
		--p4runtime-files p4src/Build/spine_p4info.txt --Wdisable=unsupported \
		p4src/src/spine.p4 -Dports=256  -DENABLE_DEBUG_TABLES -DDP_ALGO_ECMP -DECN_ENABLED -DK=4
	sudo cp ./p4src/Build/spine.json /tmp/
	sudo cp ./p4src/Build/spine_p4info.txt /tmp/
	@echo "*** P4 program for spine switch compiled successfully! Output files are in p4src/Build"

p4-ecmp: p4-leaf-ecmp p4-spine-ecmp
	$(info *** Building P4 program with ECMP routing for the leaf and spine switch...)


p4-leaf-top-k-path: p4src/src/leaf.p4
	$(info *** Building P4 program for the leaf switch for -top-k-path...)
	@mkdir -p p4src/Build
	p4c-bm2-ss --arch v1model -o p4src/Build/leaf.json \
		--p4runtime-files p4src/Build/leaf_p4info.txt --Wdisable=unsupported \
		p4src/src/leaf.p4 -Dports=256 -DENABLE_DEBUG_TABLES -DDP_ALGO_TOP_K_PATH -DECN_ENABLED -DK=4
	sudo cp ./p4src/Build/leaf.json /tmp/
	sudo cp ./p4src/Build/leaf_p4info.txt /tmp/
	@echo "*** P4 program for leaf switch compiled successfully! Output files are in p4src/Build"



p4-spine-top-k-path: p4src/src/spine.p4
	$(info *** Building P4 program for the spine switch for -top-k-path...)
	@mkdir -p p4src/Build
	p4c-bm2-ss --arch v1model -o p4src/Build/spine.json \
		--p4runtime-files p4src/Build/spine_p4info.txt --Wdisable=unsupported \
		p4src/src/spine.p4 -Dports=256  -DENABLE_DEBUG_TABLES -DDP_ALGO_TOP_K_PATH -DECN_ENABLED -DK=4
	sudo cp ./p4src/Build/spine.json /tmp/
	sudo cp ./p4src/Build/spine_p4info.txt /tmp/
	@echo "*** P4 program for spine switch compiled successfully! Output files are in p4src/Build"

p4-top-k-path: p4-leaf-top-k-path p4-spine-top-k-path
	$(info *** Building P4 program with -top-k-path load balancing for the leaf and spine switch...)



p4-leaf-hula: p4src/src/leaf.p4
	$(info *** Building P4 program for the leaf switch for hula...)
	@mkdir -p p4src/Build
	p4c-bm2-ss --arch v1model -o p4src/Build/leaf.json \
		--p4runtime-files p4src/Build/leaf_p4info.txt --Wdisable=unsupported \
		p4src/src/leaf.p4 -Dports=256 -DENABLE_DEBUG_TABLES -DDP_ALGO_HULA -DK=4
	sudo cp ./p4src/Build/leaf.json /tmp/
	sudo cp ./p4src/Build/leaf_p4info.txt /tmp/
	@echo "*** P4 program for leaf switch compiled successfully! Output files are in p4src/Build"

p4-spine-hula: p4src/src/spine.p4
	$(info *** Building P4 program for the spine switch for hula...)
	@mkdir -p p4src/Build
	p4c-bm2-ss --arch v1model -o p4src/Build/spine.json \
		--p4runtime-files p4src/Build/spine_p4info.txt --Wdisable=unsupported \
		p4src/src/spine.p4 -Dports=256  -DENABLE_DEBUG_TABLES  -DDP_ALGO_HULA -DK=4
	sudo cp ./p4src/Build/spine.json /tmp/
	sudo cp ./p4src/Build/spine_p4info.txt /tmp/
	@echo "*** P4 program for spine switch compiled successfully! Output files are in p4src/Build"

p4-hula: p4-leaf-hula p4-spine-hula
	$(info *** Building P4 program with CLB load balancing for the leaf and spine switch for hula...)

p4-leaf-range-match-tcam-routing: p4src/src/leaf.p4
	$(info *** Building P4 program for the leaf switch...)
	@mkdir -p p4src/Build
	p4c-bm2-ss --arch v1model -o p4src/Build/leaf.json \
		--p4runtime-files p4src/Build/leaf_p4info.txt --Wdisable=unsupported \
		p4src/src/leaf.p4 -Dports=256 -DENABLE_DEBUG_TABLES -DRANGE_TCAM_ROUTING -DECN_ENABLED -DK=4
	sudo cp ./p4src/Build/leaf.json /tmp/
	sudo cp ./p4src/Build/leaf_p4info.txt /tmp/
	@echo "*** P4 program for leaf switch compiled successfully! Output files are in p4src/Build"

p4-spine-range-match-tcam-routing: p4src/src/spine.p4
	$(info *** Building P4 program for the spine switch...)
	@mkdir -p p4src/Build
	p4c-bm2-ss --arch v1model -o p4src/Build/spine.json \
			--p4runtime-files p4src/Build/spine_p4info.txt --Wdisable=unsupported \
			p4src/src/spine.p4 -Dports=256  -DENABLE_DEBUG_TABLES -DRANGE_TCAM_ROUTING -DECN_ENABLED -DK=4
	sudo cp ./p4src/Build/spine.json /tmp/
	sudo cp ./p4src/Build/spine_p4info.txt /tmp/
	@echo "*** P4 program for spine switch compiled successfully! Output files are in p4src/Build"

p4-range-match-tcam-routing: p4-leaf-range-match-tcam-routing p4-spine-range-match-tcam-routing
        $(info *** Building P4 program with range-match-tcam-routing routing for the leaf and spine switch...)


start_clos: MininetSimulator/clos.py
	$(info *** Starting clos topology DCN using MininetSimulator/clos.py...)
	sudo  python3 -E MininetSimulator/clos.py

start_ctrlr: Mycontroller.py
	$(info *** Starting Mycontroller...)
	rm -rf log/controller.log
	python3 Mycontroller.py

create-result-folders:
	mkdir ./testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.2
	mkdir ./testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.4
	mkdir ./testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.5
	mkdir ./testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.7
	mkdir ./testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_0.8
	mkdir ./testAndMeasurement/TEST_RESULTS/WebSearchWorkLoad_load_factor_1.0

create-algowise-result-folder:
	mkdir ./testAndMeasurement/TEST_RESULTS/ECMP_RESULTS
	mkdir ./testAndMeasurement/TEST_RESULTS/P4KP_RESULTS
	mkdir ./testAndMeasurement/TEST_RESULTS/HULA_RESULTS

clear-logs:
	sudo rm -rf /tmp/*
	rm -rf testAndMeasurement/TEST_RESULTS/*
	rm -rf testAndMeasurement/TEST_LOG/*
	rm -rf result/*
	rm -rf log/*
	rm -rf result/*
	sudo pkill -f iperf

clear-deployment-logs:
	rm -rf log/*

clear-iperf-processes:
	sudo pkill -f iperf

count-iperf-processes:
	ps -aux | grep -c "iperf"




process-topkpath:
	python3 ResultProcessorExecutor.py testAndMeasurement/TEST_RESULTS/ecmp/TopKPathTesterWithTopKPath testAndMeasurement/TEST_RESULTS/TopKPath/TopKPathTesterWithTopKPath ECMP P4TE ./ProcessedResultImages/l2strideSmallLarge-highRationForLargeFlows


