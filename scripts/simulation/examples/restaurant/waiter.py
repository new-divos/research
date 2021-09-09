#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typing as t

import simpy


def waiter(env: simpy.Environment) -> t.Generator[simpy.events.Timeout, None, None]:
    while True:
        print(f"Start taking orders from customer at {env.now}")
        take_order_duration = 5
        yield env.timeout(take_order_duration)

        print(f"Start giving the orders to the cook at {env.now}")
        give_order_duration = 2
        yield env.timeout(give_order_duration)

        print(f"Start serving customer food at {env.now}")
        serve_order_duratrion = 4
        yield env.timeout(serve_order_duratrion)


if __name__ == "__main__":
    env = simpy.Environment()
    env.process(waiter(env))
    env.run(until=30)
