import math

import numpy as np
import pygame

width = 800
height = 600

pygame.init()
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chain line simulation")
info_font = pygame.font.SysFont(None, 22)

x1, y1 = 100, 100
x2, y2 = 700, 500

running = True

is_dragging = False
point_dragging = None

chain_length = 800

a: float | None = None
c: float | None = None
sigm: float | None = None


def solve_k(target: float) -> float:
    """Solve sinh(k) / k = target for the non-negative catenary parameter k."""
    if not math.isfinite(target) or target < 1:
        raise ValueError("target must be a finite number greater than or equal to 1")
    if target == 1:
        return 0.0

    log_target = math.log(target)

    def log_sinhc(value: float) -> float:
        if value < 1e-3:
            value_squared = value * value
            return math.log1p(
                value_squared / 6 + value_squared**2 / 120 + value_squared**3 / 5040
            )
        return value + math.log1p(-math.exp(-2 * value)) - math.log(2 * value)

    low = 0.0
    high = 1.0
    while log_sinhc(high) < log_target:
        high *= 2

    for _ in range(80):
        middle = (low + high) / 2
        if log_sinhc(middle) < log_target:
            low = middle
        else:
            high = middle

    return (low + high) / 2


def calculate_chain_line():
    global a, c, sigm
    if x1 <= x2:
        left_x, left_y = x1, y1
        right_x, right_y = x2, y2
    else:
        left_x, left_y = x2, y2
        right_x, right_y = x1, y1

    H = right_x - left_x
    v = right_y - left_y
    chord_length = math.hypot(H, v)

    # A chain cannot be shorter than the straight-line distance between its ends.
    if H == 0 or chain_length <= chord_length:
        a = c = sigm = None
        return

    target = math.sqrt((chain_length - abs(v)) * (chain_length + abs(v))) / H
    k = solve_k(target)
    a = 0.5 * H / k

    # Pygame's y-axis points down, so use the inverted catenary orientation.
    midpoint_offset = math.asinh(-v / (2 * a * math.sinh(k)))
    c = a * midpoint_offset - 0.5 * (left_x + right_x)
    sigm = left_y + a * math.cosh((left_x + c) / a)


def handle_mouse_down(pos: tuple[int, int]):
    global is_dragging, point_dragging
    if is_dragging:
        return
    distance_to_point1 = math.hypot(pos[0] - x1, pos[1] - y1)
    distance_to_point2 = math.hypot(pos[0] - x2, pos[1] - y2)
    if distance_to_point1 < distance_to_point2:
        point_dragging = "point1"
    else:
        point_dragging = "point2"
    is_dragging = True


def handle_mouse_up(pos: tuple[int, int]):
    global is_dragging, point_dragging
    is_dragging = False
    match point_dragging:
        case "point1":
            global x1, y1
            x1, y1 = pos
        case "point2":
            global x2, y2
            x2, y2 = pos
        case _:
            pass
    point_dragging = None

    calculate_chain_line()


def draw_dragging():
    if not is_dragging:
        return
    pygame.draw.circle(window, (255, 0, 0), pygame.mouse.get_pos(), 5)


def draw_chain_info():
    chord_length = math.hypot(x2 - x1, y2 - y1)
    lines = [
        f"Chain length (L): {chain_length:.1f} px",
        f"Endpoint distance: {chord_length:.1f} px",
    ]

    if a is None or c is None or sigm is None:
        lines.append(f"No curve: increase L above {chord_length:.1f} px.")
    else:
        lines.extend(
            [
                f"Catenary parameter (a): {a:.2f} px",
                f"Horizontal offset (c): {c:.2f} px",
                f"Vertical offset (σ): {sigm:.2f} px",
            ]
        )
    lines.append("Use the mouse wheel to adjust L.")

    padding = 10
    line_height = info_font.get_linesize()
    panel_width = max(info_font.size(line)[0] for line in lines) + padding * 2
    panel_height = len(lines) * line_height + padding * 2
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((255, 255, 255, 220))
    window.blit(panel, (10, 10))
    pygame.draw.rect(window, (80, 80, 80), (10, 10, panel_width, panel_height), 1)

    for index, line in enumerate(lines):
        text = info_font.render(line, True, (25, 25, 25))
        window.blit(text, (10 + padding, 10 + padding + index * line_height))


def draw_chain_line():
    pygame.draw.line(window, (200, 200, 240), (x1, y1), (x2, y2), 2)
    if not is_dragging:
        pygame.draw.circle(window, (10, 10, 10), (x1, y1), 5)
        pygame.draw.circle(window, (10, 10, 10), (x2, y2), 5)
    else:
        if point_dragging == "point1":
            pygame.draw.circle(window, (220, 220, 220), (x1, y1), 5)
            pygame.draw.circle(window, (10, 10, 10), (x2, y2), 5)
        elif point_dragging == "point2":
            pygame.draw.circle(window, (10, 10, 10), (x1, y1), 5)
            pygame.draw.circle(window, (220, 220, 220), (x2, y2), 5)
    if a is None or c is None or sigm is None:
        return
    points_x = np.linspace(min(x1, x2), max(x1, x2), 100)
    points_y = [-a * math.cosh((x + c) / a) + sigm for x in points_x]
    points = list(zip(points_x, points_y))
    pygame.draw.lines(window, (0, 0, 0), False, points, 2)


calculate_chain_line()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_mouse_down(event.pos)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            handle_mouse_up(event.pos)
        if event.type == pygame.MOUSEWHEEL:
            if event.dict["y"] > 0:
                chain_length += 10
            else:
                chain_length -= 10
            calculate_chain_line()

    window.fill((255, 255, 255))
    draw_chain_line()
    draw_dragging()
    draw_chain_info()

    pygame.display.flip()
