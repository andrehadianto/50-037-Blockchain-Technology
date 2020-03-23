# 50.037 Blockchain Project
This project aims to simulate blockchain circulation in a small scale. On top of normal blockchain minings and transactions, it also supports simulation of Selfish Mining Attack and 51% Attack (Majority attack)

## Getting Started
--- 
### Installation
- Clone the project
- On the root folder, run `.\blockchain\Scripts\activate` on bash terminal
- run `python -m pip install -r requirements.txt`

## Usage Methods
--- 
## Blockchain environment
### Initalization
We simulate normal blockchain environment with 2 different miners and 1 SPV client.  
In 3 different terminals, run the following codes:
```
python MinerApp.py -p 5004 -s normal
```
```
python MinerApp.py -p 5005 -s normal
```
```
python SPVApp.py
```
Open another terminal to run the control script
```
```

### Selfish Mining Attack
We simulate the selfish mining attack with 2 different miners and 1 SPV client. 1 miner will act as a normal miner and the other miner will be the selfish miner.  
In 3 different terminals, run the following codes:
```
python MinerApp.py -p 5004 -s selfish
```
```
python MinerApp.py -p 5005 -s selfish
```
```
python SPVApp.py
```
Selfish miner 
### 51% Attack (Majority Attack)


## Authors
- Andre Hadianto Lesmana (1002837)
- Antonio Miguel Canlas Quizon (1003014)
- Kenneth Ng (1002793)
- Teo Yong Quan (1002828)