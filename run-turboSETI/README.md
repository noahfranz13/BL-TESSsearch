# README
This README gives instructions to setup to run the multiTurbo.py script on multiple files at GBT.

## Setting up a Conda Environment
The environment.yml file in this repo is for a conda environment called runTurbo
that has all of the necessary dependencies installed. Run the following commands to
activate it in the directory you plan to run multiTurbo:

1) ```source /home/noahf/miniconda3/bin/activate runTurbo```
2) ```conda activate runTurbo```

## Setting up an SQL table
For ease and to keep it cheap it is probably best to create a table and then
upload it to my existing SQL Server on the BL GCP. This server is called
`noahf-tess-filetracking`. If you choose to do this, reach out to me for the password
and username, otherwise you can set this up with your own databases information.
Even still, the table uploaded to this needs to have specific columns to work with
this script. Those columns are:
```
row_num     : the number of the row, MUST be unique otherwise information will be overwritten
turboSETI   : if the file has been run through turboSETI, either 'TRUE' or 'FALSE'.
filepath    : path to turboSETI input file, inlcuding name
filename    : Just the name of the file being passed into turboSETI
target_name : Name of target in the file passed into turboSETI
toi         : ON target of the cadence to specify the output directory
splice      : If the file is spliced of unspliced
runtime     : Empty column for the runtime to be written to
outpath     : Empty column for the output file paths to be written to
```
The columns need those specific names and should follow those descriptions. Then,
once this table exists as a csv, you can upload it to a GCP bucket and follow these
steps to add it to the SQL database.

### Add your IP Address to the Known Hosts  
To access the GCP SQL database, you must add your IP address as a known host on GCP.
Doing this is fairly easy, just follow these 6 steps:

1) Open a terminal with mysql installed, GBT is one option but if you'd prefer to
do it locally you can install mysql with https://www.mysql.com/downloads/
2) Run the command `curl ifconfig.me` to print your IP address and copy it
3) On the Breakthrough Listen GCP page, navigate to SQL on the left side, then
choose the `noahf-tess-filetracking` option
4) Choose connections on the left side
5) Click `Add Network` and give it a descriptive name and paste your IP address
6) Click `Done` and then `Save`

### Create a new Table Schema in the database
To upload your csv file, you must have an empty SQL Table to hold your data.
Create this table by following these steps:

1) Navigate to the Overview page of the SQL database and copy the Public IP Address
2) Open the same terminal from above with mysql installed and run
`mysql --host=IP --username=USER -p`
and replace IP with the Public IP Address and USER with your username. Then type
in your password to enter the mysql terminal.
3) Run the following sequence of commands to create a SQL table, replace tablename
with the name you want for your table. The second command assumes your table only
has the columns described above, however, if it has more add more columns accordingly.

```USE FileTracking```
```
CREATE TABLE tablename (
row_num INT,
target_name VARCHAR(300),
toi VARCHAR(100),
filename VARCHAR(300),
filepath VARCHAR(500),
splice VARCHAR(100),
turboSETI VARCHAR(100),
runtime FLOAT NULL DEFAULT 0,
outpath VARCHAR(500) NULL DEFAULT 'NONE'
);
 ```
 
4) To check that it worked run `DESCRIBE tablename` and make sure all your columns
are there

### Upload your csv file to GCP
Make sure you first add your csv file to a GCP bucket, then you can follow these
steps.
1) From the overview page of the GCP SQL `noahf-tess-filetracking` database, click
the import button on the top bar
2) Type the path to your data in the Source box
3) Change the File Format to csv
4) Under Database choose `FileTracking`
5) Under Table enter the `tablename` you chose above
6) Click the Import button at the bottom
7) Open the table in a SQL GUI to check that the import was successful. You can
use phpMyAdmin (https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-phpmyadmin-on-ubuntu-20-04
  and https://stackoverflow.com/questions/16801573/how-to-access-remote-server-with-local-phpmyadmin-client)

### Making Global Variables
The last step to setup the SQL database is you must add 3 global variables to
your `.bash_profile` in the home directory on the machine you will be running
multiTurbo on. All you have to do is navigate to your home directory, open the
.bash_profile file, and add the following lines to it:
```
export GCP_USR="USERNAME"
export GCP_IP="IP ADDRESS"
export GCP_PASS="PASSWORD"
```
Where you replace the USERNAME, IP ADDRESS, and PASSWORD with your SQL databases
respective information. If you are using the `noahf-tess-filetracking`, reach out
to me to get this information!

## Running multiTurbo
Once you have followed the steps above you should have a conda evironment and SQL
table setup. Then from there you should be ready to run the multiTurbo python script!
When running the multiTurbo script has the following options:
```
INPUT OPTIONS
  outdir      : output directory of turboSETI files, will consist of subdirectories
              labelled by TOI (ON target). This is Required.
  sqlTable    : The name of your SQL Table. This is Required
  nnodes      : number of compute nodes to run on, default is 64
  timer       : times the run if set to true, default is True
  debug       : prints specific lines to help debug subprocess default is False
  splicedonly : If True only spliced files are run through default is False
  ```

An example to run the multiTurbo script from the command line is
```python3 multiTurbo.py --outdir my/path/to/output --sqlTable myTableName```
