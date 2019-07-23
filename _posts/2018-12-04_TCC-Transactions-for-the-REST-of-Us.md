---
layout:     post
title:     Transactions for the REST of Us
subtitle:   Transactions for the REST of Us
date:       2018-09-22
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - TCC
    - Transactions 
    - REST 
typora-copy-images-to: ..\img
typora-root-url: ..
---

# Transactions for the REST of Us

https://dzone.com/articles/transactions-for-the-rest-of-us



Does REST need transactions? In this article, we take a pragmatic approach driven by concrete examples, which can benefit from atomic transactions across REST services. We then show how Try-Confirm/Cancel (TCC) can offer a simple, interoperable solution that is aligned with REST/ HTTP and Hypermedia. TCC can be universally applied because it is based on a design pattern rather than a product or technology. For a specific but important class of systems — reservation systems — it provides both a transaction model as well as a lightweight form of "BPM" over REST. 



## REST Systems That Benefit From Distributed Atomic Transactions

We claim that a whole class of systems termed "distributed reservation systems" — even if implemented in REST — benefit from transactions. The following two examples will show you why:

1. **Travel:** Booking a flight and a rental car together at two independent providers. Suppose you want to book a flight to Barcelona and a rental car to drive to the South of Spain. You don't want a car without the flight, and you don't need a flight if there is no car available.

2. **Telco:** Reserving a custom phone number for a customer — subject to billing conditions. A telco company allows selected customers to purchase customized phone numbers. The phone number is checked for availability and, if available, reserved for the customer. Then, a separate billing service is called for the billing process. When billing succeeds, the number is assigned to the customer. If billing fails, then the phone number is released again for the next customer. It would be bad for the telco if it assigned phone numbers without billing the customer or if it billed customers for phone numbers not assigned.

As a generalization, we would like to have reservation processes across multiple, independent REST services where failures before completion are guaranteed to have no effect. This is similar to the classic well-known transactional programming model, where transactions roll back if they do not reach the commit stage.





## Our Solution: Try-Confirm/Cancel (TCC)

We offer a solution for distributed atomic transactions across REST services that aligns well with HTTP and REST principles and offers the simplest thing that could possibly work. We promised to be pragmatic, so let's define our solution by its desired behavior in terms of, say, the travel example.

### The Happy Path

We want the travel example's "happy path" to work like this:

- **Step 1:** Book the flight at the airline provider via HTTP POST. The airline gives back a URI to con rm and an expiration deadline for confirmation.
- **Step 2:** Rent the car at the car rental company via HTTP POST. The car rental company returns a URI to con rm and an expiration deadline for confirmation.
- **Step 3:** Confirm both previous steps by calling PUT on each of the URIs returned.

### Either Cancel Everywhere or Confirm Everywhere

The airline and/or the car rental company are free to autonomously cancel their bookings after the expiration deadline. This means that any failures before Step 3 (i.e., not executing step 3) imply that neither the airline provider nor the car rental company receive a confirmation before their respective expiration deadlines, after which they are free to cancel autonomously — thereby releasing the business resources they have been reserving until then. The net result: cancel everywhere (after some time).

Any failures after Step 3 do not affect the atomicity of the outcome since both the flight and the car have already been confirmed, so both reservations have been successful.

### The Tricky Part

Failures during Step 3 are trickier. Temporary outages of either participant can be resolved by resending the confirmation message. After all, PUT is idempotent, so we can keep retrying it as long as necessary. However, as soon as the airline provider has been confirmed, confirmation to the car rental may still fail (for instance, due to intermediate expiration followed by autonomous cancel). This is always possible and would lead to a "heuristic" anomaly — just like you will find in any distributed transaction system ever built. To minimize the occurrence of heuristics and to facilitate their resolution, smart implementations can be based on a specialized and reusable TCC coordinator that makes informed decisions about whether to proceed in Step 3 or not, keeps a recoverable progress log and performs smart retries where possible. This way, the number of anomalies may be reduced to practically zero.

## Implementing TCC

TCC only works if each of the roles (participant service, application, and coordinator) follow their part of the protocol. While this may seem like a constraint, in reality, the protocol is so simple that it can be easily achieved in many application domains.

### The TCC Service/Participant

TCC participants (like the airline or the car rental) implement a simple lifecycle model for service invocations ("reservations"). Each invocation of a participant service goes through the following three states:

1. **Initial:** Nothing has been done yet.
2. **Reserved:** An invocation ("Try")—probably via HTTP POST with a local database transaction within the service—has lead to a reservation on behalf of the client process. The reserved state is identified by a unique URI that can be used to con rm, and an associated expiration date/time after which the participant can autonomously cancel and move back to the initial state. In the case of a flight reservation system, this corresponds to a seat reservation identified by a URI and with associated expiration date/time. As a minor but useful extension, a participant in this state can accept HTTP DELETE in case it wants to be notified of failures before it times out by itself.
3. **Final:** This is where the reservation becomes permanent, meaning it can no longer be easily and automatically canceled. This state is reached when a reserved participant receives a confirmation message within the specified time frame, by HTTP PUT.

For reporting purposes, the participant service's database should reflect these three states. In particular: the distinction between reserved and final state needs to be clear for each reservation because:

1. Autonomous cancel is only allowed during reserved state.
2. Sales reporting probably only wants to take the final reservations into account.
3. Penalties may be levied to clients that perform cancellations on finalized bookings, but not on temporary reservations.

### The TCC Application/Workflow

The application or workflow logic is according to the happy path outlined above. In particular, no specific error path logic is needed — which simplifies the logic and makes it more reliable by taking out the hard-to-test parts. Either Step 3 is reached (implying confirmation), or not (implying cancellation).

### The TCC Conformation/Coordinator

When the happy path reaches Step 3, the TCC coordinator service comes into play: it accepts the set of URIs to con rm and tries to do a smart job by confirming and retrying them if needed,
or canceling when that is the better option — at least for those participants that accept DELETE.

## A RESTful Solution

TCC ts really well with REST. Every participant (the car reservation company and the airline) always returns a URI pointing to the reserved resource. This uses hypermedia so
that clients can inspect the URI with GET to inquire about its validity (when is the reservation going to expire?) but the URI can also be used to con rm the reservation by sending idempotent PUT requests. We have de ned a specific MIME type for TCC participants to facilitate compatibility between participants, applications, and the coordinator. This means you can define participants today and have them participate in the transactions of tomorrow.

## References

- For a more elaborate discussion of TCC for REST, see [this recorded presentation](https://www.infoq.com/presentations/Transactions-HTTP-REST).
- For details on the coordinator API and the minimum requirements for the participants API see: Guy Pardon, and Cesare Pautasso, "Atomic Distributed Transactions: a RESTful Design", Proc. of the 5th International Workshop on Web APIs and RESTful Design (WS-REST), Seoul, Korea, ACM, April, 2014. .
- The detailed TCC API specification (including how to implement your own participant) is available [here](https://atomikos.com/Blog/TransactionsForRestApiDocs?Source=dzone).