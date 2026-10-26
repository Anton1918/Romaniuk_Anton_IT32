import math
import sys

NAME = "Anton Romaniuk"
GROUP = "IT-32"

# --- константи (мої розміри) ---
ROOM_L, ROOM_W, ROOM_H = 2.5, 3.0, 4.3   # м
DOOR_W, DOOR_H = 0.9, 2.0                # м
WINDOW_W, WINDOW_H = 1.4, 1.5            # м
TILE_SIDE = 0.30                         # м (30 x 30 см)
TILE_PRICE = 42.30                       # грн за плитку
SPARE = 0.10                             # запас 10 %
PAINT_LAYERS = 2
PAINT_COVERAGE = 10.0                    # м2 на 1 л за один шар
CAN_VOLUME = 2.5                         # л


def main():
    print(f"{NAME}, {GROUP}")

    if min(ROOM_L, ROOM_W, ROOM_H, TILE_SIDE, TILE_PRICE) <= 0:
        print("error: dimensions and price must be positive", file=sys.stderr)
        sys.exit(1)

    # 1. площі
    floor_area = ROOM_L * ROOM_W
    wall_area = 2 * (ROOM_L + ROOM_W) * ROOM_H - DOOR_W * DOOR_H - WINDOW_W * WINDOW_H
    if wall_area <= 0:
        print("error: door and window are larger than walls", file=sys.stderr)
        sys.exit(1)

    # 2. діагоналі
    floor_diag = math.hypot(ROOM_L, ROOM_W)
    room_diag = math.dist((0, 0, 0), (ROOM_L, ROOM_W, ROOM_H))

    # 3. плитка
    tile_area = TILE_SIDE ** 2
    tiles_exact = floor_area / tile_area
    tiles_round = round(tiles_exact)
    tiles_floor = math.floor(tiles_exact)
    tiles_ceil = math.ceil(tiles_exact)
    tiles_buy = math.ceil(tiles_exact * (1 + SPARE))

    # 4. фарба
    paint_l = wall_area * PAINT_LAYERS / PAINT_COVERAGE
    cans = math.ceil(paint_l / CAN_VOLUME)

    # 5. вартість двома способами
    cost_mul = tiles_buy * TILE_PRICE
    cost_sum = 0.0
    for _ in range(tiles_buy):
        cost_sum += TILE_PRICE

    print(f"room:         {ROOM_L} x {ROOM_W} x {ROOM_H} m")
    print(f"floor area:   {floor_area:.2f} m2")
    print(f"wall area:    {wall_area:.2f} m2 (without door and window)")
    print(f"floor diag:   {floor_diag:.2f} m")
    print(f"room diag:    {room_diag:.2f} m")
    print()
    print(f"tiles exact:  {tiles_exact:.2f}")
    print(f"    round:    {tiles_round}")
    print(f"    floor:    {tiles_floor}")
    print(f"    ceil:     {tiles_ceil}")
    print(f"tiles to buy: {tiles_buy} (+{SPARE:.0%} spare)")
    print(f"paint:        {paint_l:.2f} l -> {cans} cans of {CAN_VOLUME} l")
    print()
    print(f"tiles cost:   {cost_mul:.2f} UAH")
    print(f"sum == mul:   {cost_sum == cost_mul}")
    print(f"isclose:      {math.isclose(cost_sum, cost_mul)}")
    print(f"difference:   {abs(cost_sum - cost_mul)}")


if __name__ == "__main__":
    main()
