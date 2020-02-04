def _create_pins():
    """
    :rtype: Iterable[int]
    """
    middle = 5000
    for i in range(0, 2 * middle):
        if i % 2 == 0:
            yield middle - i // 2 - 1
        else:
            yield middle + i // 2


PINS = tuple(_create_pins())
assert len(PINS) == 10000, "Len = %d" % len(PINS)
assert min(PINS) == 0000
assert max(PINS) == 9999


def get_pin_index(pin):
    return 0 if pin is None else PINS.index(pin)


def pin_generator(last_pin=None):
    """
    :type last_pin: int or None
    :rtype: Iterable[int]
    """
    start_pos = get_pin_index(last_pin) + 1 if last_pin is not None else 0
    for i in range(start_pos, len(PINS)):
        yield PINS[i]


def test_selector():
    print(get_pin_index(6000))

    l1 = list(pin_generator(last_pin=9997))
    assert len(frozenset(l1)) == 4

    l2 = list(pin_generator(last_pin=4999))
    assert len(frozenset(l2)) == 9999

    l3 = list(pin_generator(last_pin=5000))
    assert len(frozenset(l3)) == 9998


if __name__ == '__main__':
    test_selector()
