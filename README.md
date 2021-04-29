# pktgen.py

+ pktgen.py is a tui wrapper on Pktgen-DPDK's run.py tool
+ Instructions for launching Pktgen-DPDK
   * To run Pktgen-DPDK, use the script `` pktgen.py ''
     - `` `$. / pktgen.py```
   * After running the script, you should see the following window
![image](https://user-images.githubusercontent.com/77335604/116595648-59d68280-a945-11eb-8e10-3ee541dedbdc.png)
   * The left panel 'Run configurations' lists the Pktgen-DPDK configuration, ```* .cfg``` are the standard Pktgen-DPDK configuration files. The configuration files are located in the Pktgen-DPDK / cfg directory. At any time, you can write and configure a configuration file. For example, for each server, its own configuration files were written, their names coincide with the name of the machine, for example, if we run from IXIA, then accordingly its configuration file is called ```IXIA.cfg```.
   * The panel located in the center displays the contents of the configuration, and to go to this section we use the ```tab``` key.
   * The bottom panel 'Execute' displays the command to run the program (Note: ```pktgen.py``` encapsulates each file through a parser, and if at least one of the configuration file contains a syntax error, the script will not run and will display the corresponding error in the file ).
   * To run the program, go back to the 'Run configurations' panel by pressing the up button until the cursor reaches the panel. Select the desired file and click on ```enter```.
   * After starting Pktgen-DPDK, and it is important to note that the downloaded files in Pktgen-DPDK (.lua, .txt, .sh) are also written in the ```* .cfg``` files. According to the rules of the Pktgen-DPDK itself, the downloaded files are located under the ```Pktgen-DPDK/test``` directory. 
