# BL-TESSsearch

This is a repo for my research with Breakthrough Listen and is focused on a search of transiting TESS targets of interest in current Green Bank Telescope data.

## File Organization
The directories are organized as follows:

### Target-Selection
This directory has scripts that I used to choose the transiting TESS targets. In this directory, the gbt-inTransit.py script is the main result and has a my method for figuring out which GBT observations occur during a TESS TOI transit. In addition, the TESStarget-analysis jupyter notebook holds analysis code for plotting the observation locations as well as other checks I ran on the targets. Finally the locate-TIC-files directory holds code I used to attempt to find the Filterbank and hdf5 files for turboSETI analysis.

### recreate-Traas
This directory simply holds some code I used to learn the data structures. I did this by recreating a plot from Traas et al. (2021) using some of the data he stored on the Breakthrough Listen Public Data Archive

### run-turboSETI
This directory holds the multiTurbo and wrapTurbo scripts which work in tandem to run turboSETI on files across all 64 compute nodes at Green Bank. multiTurbo handles the distribution of the turboSETI processes while wrapTurbo marks files as "done" in a SQL database. By marking files as done, we are able to  stop the multiTurbo script for Breakthrough Listen Green Bank Observations and start it back up again from where it left off once the observation it over. The connect-spreadsheet subdirectory houses a script to connect to a google spreadsheet, which I was using instead of the SQL database at first. While this script is unnecessary now, it has useful functions for later if needed. Finally, the prepTurbo subdirectory has scripts and notebooks I used to extract the necessary information from the file names and write it to a csv to be uploaded to the SQL database.

### analysis
This directory has all of my analysis code for the turboSETI output files. This includes the script FindPlot which combines the turboSETI find_event_pipeline and plot_event_pipeline. In addition, the notebook plotAllWaterfall contains the code I used to view the output files from the plot_event_pipeline. Furthermore, the hit_analysis notebook has the code I used to analyze the distribution of hits and events from turboSETI. Finally, the seti_limits_py3 directory and transmitter_rate_vs_EIRP notebook shows my code for calculating the Continuous Waveform Figure of Merit.
