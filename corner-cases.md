# corner cases

| Schedule | Description | Behavior |
| --- | --- | --- |
| `on=(M,7);off=(M,7)` | On and Off times are the same | ? |
| `off=[(M,9),(M,18)]` | On times are for the same day | ? |
| `off=(F-M,9)` | Support for circular days | ? |
