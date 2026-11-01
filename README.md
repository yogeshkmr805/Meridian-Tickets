# Meridian Tickets: Seat Reservation Service

Meridian Tickets sells seats to concerts and stadium shows. Popular tours go on sale at exactly 10:00 AM local time, and demand arrives in a single burst within seconds of that moment.

This repository holds the seat-reservation path: the code that takes a fan's request to reserve seats and either confirms the reservation or returns an honest "sold out" response.

## Background

During a recent arena show sale, the reservation service failed within the first ninety seconds of the on-sale. The service ran on a fixed pool of EC2 instances behind a load balancer. CPU saturated almost immediately, and autoscaling took about four minutes to bring new capacity online. Thousands of fans received timeout errors instead of a clear sold-out message.

The requirements that came out of that incident:

- **Absorb spikes.** The reservation path must handle roughly 50x normal traffic within seconds of an on-sale opening.
- **Stay cheap when idle.** Most days nobody is buying tickets, so the service should cost close to nothing when there is no traffic.
- **Fail honestly.** When seats are gone, users get a clear sold-out response, not a timeout.

Serverless compute fits this combination of instant scale and near-zero idle cost, so the reservation function is implemented on AWS Lambda.

## Current Status

This project is in early development. The current focus is the reservation function itself, which is the first piece of the Lambda-based path. Load testing against a simulated on-sale burst and the surrounding infrastructure (API entry point, data store, and monitoring) are still to come.

## How It Works (Planned Design)

1. A client sends a reservation request for a show, a section, and a quantity of seats.
2. The reservation function checks seat availability and attempts to claim the seats atomically, so two requests can never sell the same seat.
3. On success, the function returns a confirmed reservation.
4. If the requested seats are no longer available, the function returns a sold-out response immediately instead of waiting on capacity.

Because each invocation is independent, Lambda can run many copies in parallel during a spike and scale back to zero afterward.