# HOWTO Connect SEENGREAT 2inch LCD B to `puppygm01`

TODO

## References

- Purchase on Amazon.it: <https://www.amazon.it/dp/B0DCZ9TXTQ>
- SEENGREAT 2inch LCD Display B Instruction manual Rev 1.1 (8 pages A6)
- <https://www.seengreat.com>
- <https://github.com/seengreat>
- Wiki: <https://seengreat.com/wiki/155>

## TODO: Connect wires to Raspberry Pi 40-pin connector

| LCD Pin | LCD Signal | Connect to Raspberry Pi GPIO |
|--------:|------------|------------------------------|
| 1 | BL | ? |
| 2 | DC | ? |
| 3 | RST | ? |
| 4 | CS | ? |
| 5 | CLK | ? |
| 6 | DIN | ? |
| 7 | GND | GND  |
| 8 | VCC | 3.3V |

TODO

## Run low-level test program

Logged in as `ubuntu@puppygm01`

```bash
sudo apt update && sudo apt -y install wiringpi
sudo gpio -v
```

Result: TODO

<!-- EOF -->
