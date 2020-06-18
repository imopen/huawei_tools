# huawei_tools
Tools for testing and setting Huawei LTE Routers

## Thanks
First of all, thanks to: 
* Salamek for https://github.com/Salamek/huawei-lte-api
* octave21 for https://github.com/octave21/huawei-lte
* Speedtest CLI for https://www.speedtest.net/apps/cli

## Huawei Band Test
### Installation
You need speedtest command line tool. You can grab it at: https://www.speedtest.net/apps/cli  
Install it based on your operating system .
  
  
You need also huawei-lte-api, you can install it with:
`pip3 install huawei-lte-api`

### What it does
An example is worth a thousand words.  
Your needs is to test the speed of your 4G provider and which bands combination is better.  
Your provider offers, for example, bands 1, 3, 7 and carrier aggregation.
You can test all day long and look at the best combination.  
You set the config variable, for example `bands = ["7+3", "1+3", "1+7", "7"]`, with all the bands combinations you would like to test.
You launch script and it would tests your bands every hour (configurable),
 launching a speed test for you for every combination you specify.  
 Pay attention that order matters, on `"7+3"` combination the first band `7` is the base one, the other `3` work if carrier aggregation is available.

It will report the result on `INFO` log level, in csv style, so you can analyze it on a spreadsheet editor.

