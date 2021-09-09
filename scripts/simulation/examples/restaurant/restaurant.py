#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple
import random
import typing as t

import simpy


RANDOM_SEED: t.Final[int] = 43
SIM_TIME: t.Final[int] = 240
NUM_ITEMS: t.Final[int] = 10  # Number of items per food option.
FOODS: t.Final[t.List[str]] = [
    "Spicy Chicken",
    "Poached Chicken",
    "Tomato Chicken Skillet",
    "Honey Mustard Chicken",
]

Restaurant = namedtuple(
    "Restaurant",
    [
        # a resource with capacity 1 (the staff can only serve one customer at time)
        "staff",
        # options of food the restaurant offers
        "foods",
        # number of items per option of food
        "available",
        # events when each option of food runs out
        "run_out",
        # the time when each option of food runs out
        "when_run_out",
        # number of customers who leave the line because their food option runs out
        "rejected_customers",
    ],
)


def customer(
    env: simpy.Environment, food: str, num_food_order: int, restaurant: Restaurant
) -> t.Generator[simpy.events.Timeout, None, None]:
    """
    Customer tries to order a certain number of a particular food,
    if that food ran out, customer leaves. If there is enought food left,
    customer orders food.
    """

    with restaurant.staff.request():
        # If there is not enough food left, customer leaves.
        if restaurant.available.get(food, 0) < num_food_order:
            restaurant.rejected_customers[food] += 1
            return

        # If there is enough food left, customer orders food.
        restaurant.available[food] -= num_food_order
        # The time it takes to prepare food.
        yield env.timeout(10 * num_food_order)

        # If there is no food left after customer orders, triggered
        # run out event.
        if restaurant.available[food] == 0 and not restaurant.run_out[food].triggered:
            restaurant.run_out[food].succeed()
            restaurant.when_run_out[food] = env.now

        yield env.timeout(2)


def customer_arrivals(
    env: simpy.Environment, restaurant: Restaurant
) -> t.Generator[simpy.events.Timeout, None, None]:
    """Create new customers until the simulation reaches the time limit"""

    while True:
        yield env.timeout(10 * random.random())

        # Choose a random choice from the menu.
        food = random.choice(restaurant.foods)

        # Number of a food choice the customer order.
        num_food_order = random.randint(1, 6)

        if restaurant.available.get(food):
            env.process(customer(env, food, num_food_order, restaurant))


if __name__ == "__main__":
    random.seed(RANDOM_SEED)

    env = simpy.Environment()
    restaurant = Restaurant(
        staff=simpy.Resource(env, capacity=1),
        foods=FOODS,
        available={food: NUM_ITEMS for food in FOODS},
        run_out={food: env.event() for food in FOODS},
        when_run_out={food: None for food in FOODS},
        rejected_customers={food: 0 for food in FOODS},
    )

    # Start process and run.
    env.process(customer_arrivals(env, restaurant))
    env.run(until=SIM_TIME)

    for food in FOODS:
        if restaurant.run_out[food]:
            timeout = restaurant.when_run_out[food]
            if timeout is None:
                timeout = SIM_TIME

            print(
                f"The food {food} ran out {round(timeout, 2)} "
                "minutes after the restaurant opens."
            )
            print(
                f"Number of people leaving queue when the {food} ran out is "
                f"{restaurant.rejected_customers[food]}.\n"
            )
