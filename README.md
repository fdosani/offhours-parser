# offhours-parser

Messing around to create some helper utils for the following Issue in cloud-custodian:
[https://github.com/capitalone/cloud-custodian/issues/13](https://github.com/capitalone/cloud-custodian/issues/13)


#### Schedule format:
```
# up mon-fri from 7am-7pm; eastern time
off=(M-F,19);on=(M-F,7)
# up mon-fri from 6am-9pm; up sun from 10am-6pm; pacific time
off=[(M-F,21),(U,18)];on=[(M-F,6),(U,10)];tz=pt
```
*note: I'm using ';' to separate each key tag. Original issue was using ','*

#### Possible values:

| field | values                   |
|-------|--------------------------|
| days  | M, T, W, H, F, S, U      |
| hours | 1, 2, 3, ..., 22, 23, 24 |

Days can be specified in a range (ex. M-F).

If the timezone is not supplied, it's assumed et (eastern time), but this default could be configurable.

#### Parser output:

The schedule parser will return a dict or None (if the schedule is invalid):

```
# off=[(M-F,21),(U,18)],on=[(M-F,6),(U,10)],tz=pt
{
  'off': [{ 'days': "M", hour: 21 },
    { 'days': "T", hour: 21 },
    { 'days': "W", hour: 21 },
    { 'days': "H", hour: 21 },
    { 'days': "F", hour: 21 },
    { 'days': "U", hour: 18 }],

  'on': [{ 'days': "M", hour: 6 },
      { 'days': "T", hour: 6 },
      { 'days': "W", hour: 6 },
      { 'days': "H", hour: 6 },
      { 'days': "F", hour: 6 },
      { 'days': "U", hour: 10 }],
  'tz': "pt"
}
```
*note: I'm expanding date ranges into the individual dates. Makes it easier to consume later*


#### Usage:
```
>>> import parser as p
>>> offhours = p.parse_off_hours("off=(M-F,19);on=(M-F,7);tz=pt")
>>> offhours
{'on': [{'days': 'M', 'hour': 7}, {'days': 'T', 'hour': 7}, {'days': 'W', 'hour': 7}, {'days': 'H', 'hour': 7}, {'days': 'F', 'hour': 7}],
'off': [{'days': 'M', 'hour': 19}, {'days': 'T', 'hour': 19}, {'days': 'W', 'hour': 19}, {'days': 'H', 'hour': 19}, {'days': 'F', 'hour': 19}],
'tz': 'pt'}
```
