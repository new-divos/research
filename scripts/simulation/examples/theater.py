#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import statistics
import typing as t

import simpy


RANDOM_SEED: t.Final[int] = 43
SIM_TIME: t.Final[int] = 90


class Theater:
    def __init__(
        self,
        env: simpy.Environment,
        num_cashiers: int,
        num_servers: int,
        num_ushers: int,
    ) -> None:
        self.__env = env
        self.__wait_times: t.List[float] = []

        self.__cashier = simpy.Resource(self.__env, num_cashiers)
        self.__server = simpy.Resource(self.__env, num_servers)
        self.__usher = simpy.Resource(self.__env, num_ushers)

    def add(self, delay: float) -> None:
        self.__wait_times.append(delay)

    def run(self) -> t.Generator[t.Any, None, None]:
        idx = 0
        while True:
            idx += 1
            moviegoer = Moviegoer(idx, self)
            self.__env.process(moviegoer.go())

            # Wait a bit before generating a new person
            yield self.__env.timeout(0.2)

    def calculate(self) -> t.Tuple[int, int]:
        average_wait = statistics.mean(self.__wait_times)

        # Pretty print the results
        minutes, frac_minutes = divmod(average_wait, 1)
        seconds = frac_minutes * 60
        return round(minutes), round(seconds)

    @property
    def env(self) -> simpy.core.Environment:
        return self.__env

    @property
    def cashier(self) -> simpy.resources.resource.Resource:
        return self.__cashier

    @property
    def server(self) -> simpy.resources.resource.Resource:
        return self.__server

    @property
    def usher(self) -> simpy.resources.resource.Resource:
        return self.__usher


class Moviegoer:
    def __init__(self, idx: int, theater: Theater) -> None:
        self.__idx = idx
        self.__theater = theater

    def go(self) -> t.Generator[t.Any, None, None]:
        # Moviegoer arrives at the theater
        arrival_time = self.__theater.env.now

        with self.__theater.cashier.request() as request:
            yield request
            yield self.__theater.env.process(self.purchase_ticket())

        with self.__theater.usher.request() as request:
            yield request
            yield self.__theater.env.process(self.check_ticket())

        if random.random() > 0.5:
            with self.__theater.server.request() as request:
                yield request
                yield self.__theater.env.process(self.sell_food())

        self.__theater.add(self.__theater.env.now - arrival_time)

    def purchase_ticket(self) -> t.Generator[simpy.events.Timeout, None, None]:
        yield self.__theater.env.timeout(random.randint(1, 3))

    def check_ticket(self) -> t.Generator[simpy.events.Timeout, None, None]:
        yield self.__theater.env.timeout(3 / 60)

    def sell_food(self) -> t.Generator[simpy.events.Timeout, None, None]:
        yield self.__theater.env.timeout(random.randint(1, 5))


if __name__ == "__main__":
    # Setup
    random.seed(RANDOM_SEED)
    num_cashiers = int(input("Input # of cashiers working: "))
    num_servers = int(input("Input # of servers working: "))
    num_ushers = int(input("Input # of ushers working: "))

    # Run the simulation
    env = simpy.Environment()
    theater = Theater(env, num_cashiers, num_servers, num_ushers)
    env.process(theater.run())
    env.run(until=SIM_TIME)

    # View the results
    mins, secs = theater.calculate()
    print(
        "Running simulation...",
        f"\nThe average wait time is {mins} minutes and {secs} seconds.",
    )
