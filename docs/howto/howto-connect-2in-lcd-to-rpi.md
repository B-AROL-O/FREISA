# HOWTO Connect SEENGREAT 2inch LCD B to `puppygm01`

TODO

## References

- Purchase on Amazon.it: <https://www.amazon.it/dp/B0DCZ9TXTQ>
- SEENGREAT 2inch LCD Display B Instruction manual Rev 1.1 (8 pages A6)
- <https://www.seengreat.com>
- <https://github.com/seengreat>
- Wiki: <https://seengreat.com/wiki/155>
- Raspberry Pi Pinout: <https://pinout.xyz/>

## Connect wires to Raspberry Pi 40-pin connector

| LCD Pin | LCD Signal | Wire Color | Raspberry Pi GPIO pin    |
|--------:|------------|------------|--------------------------|
|       1 | BL         | Purple     | 18 - GPIO_24 (?)         |
|       2 | DC         | White      | 22 - GPIO_25 (?)         |
|       3 | RST        | Green      | 15 - GPIO_22 (?)         |
|       4 | CS         | Orange     | 24 - GPIO_8 (SPI0 CEO)   |
|       5 | CLK        | Yellow     | 23 - GPIO_11 (SCLK)      |
|       6 | DIN        | Blue       | 19 - GPIO_10 (SPI0 MOSI) |
|       7 | GND        | Black      | 9  - GND                 |
|       8 | VCC        | Red        | 1  - 3V3                 |

TODO

## Run low-level test program

Logged in as `ubuntu@puppygm01`

```bash
sudo apt update && sudo apt -y install wiringpi
sudo gpio -v
```

Result: TODO

<!-- EOF -->
