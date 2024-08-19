# JavDB Craw
This project is a crawler for javdb.com. It can search for videos based on keywords or actors, and export to a CSV file. 
### Installation
 Clone the repository:
   ```sh
   git clone https://github.com/DonLeeFK/jav_craw
   cd jav_craw
   ```
   
### Usage
Use the Makefile to run the program:
```sh
make run
```
First time running, it will download the required packages and dependencies. So it may take a while.
Or you can run with arguments like this:
```sh
make run ARGS="--mode joyu --detail --pages 10"
```
This will search for "joyu" in JavDB and show detailed information for the first 10 pages.



#### Options
```
usage: JavDB Craw [options]

optional arguments:
  -h, --help            show this help message and exit
  -m {joyu,keyword}, --mode {joyu,keyword}
                        search mode, joyu or keyword
  -d, --detail          whether or not if you want verbose info
  -p PAGES, --pages PAGES
                        How many pages you wanna search
```
#### Clean up
Use `make clean` to remove the downloaded packages and dependencies.

### Others
After you have generated a CSV file, you can use `make magnet` to get magnet links for each video, or use `make analyze` to analyze the data.
```

```