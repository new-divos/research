#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typing as t
from random import seed, random

import simpy

RANDOM_SEED: t.Final[int] = 43


def customer(
    env: simpy.Environment, name: str, restaurant: simpy.Resource, **duration: int
) -> t.Generator[t.Any, None, None]:
    # There is a new customer between 0 and 10 minutes.
    yield env.timeout(10 * random())
    print(
        f"{name} enters the restaurant and for the waiter "
        f"to come at {round(env.now, 2)}"
    )

    with restaurant.request() as req:
        yield req

        print(f"Sits are available. {name} get sitted at {round(env.now, 2)}")
        timeout = duration.get("get_sitted")
        if timeout:
            yield env.timeout(timeout)

        print(f"{name} starts looking at the menu at {round(env.now, 2)}")
        timeout = duration.get("choose_food")
        if timeout:
            yield env.timeout(timeout)

        print(f"Waiters start getting the order from {name} at {round(env.now, 2)}")
        timeout = duration.get("give_order")
        if timeout:
            yield env.timeout(timeout)

        print(f"{name} starts waiting for food at {round(env.now, 2)}")
        timeout = duration.get("wait_for_food")
        if timeout:
            yield env.timeout(timeout)

        print(f"{name} starts eating at {round(env.now, 2)}")
        timeout = duration.get("eat")
        if timeout:
            yield env.timeout(timeout)

        print(f"{name} starts paying at {round(env.now, 2)}")
        timeout = duration.get("pay")
        if timeout:
            yield env.timeout(timeout)

        print(f"{name} leaves at {round(env.now, 2)}")


if __name__ == "__main__":
    seed(RANDOM_SEED)

    env = simpy.Environment()
    # Model restaurant that can only allow 2 customers at once.
    restaurant = simpy.Resource(env, capacity=2)

    for i in range(5):
        env.process(
            customer(
                env,
                f"Customer {i}",
                restaurant,
                get_sitted=1,
                choose_food=10,
                give_order=5,
                wait_for_food=20,
                eat=45,
                pay=10,
            )
        )

    env.run(until=100)
