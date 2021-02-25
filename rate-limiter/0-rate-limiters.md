---
layout:     post
title:     Scaling your API with rate limiters
subtitle:   Scaling your API with rate limiters
date:       2021-02-25
author:     Paul Tarjan
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - rate limiters
    - redis
typora-copy-images-to: ..\img
typora-root-url: ..
---

# [Scaling your API with rate limiters ](https://stripe.com/blog/rate-limiters)

[Paul Tarjan](https://twitter.com/ptarjan) on March 30, 2017 in [Engineering](https://stripe.com/blog/engineering)

Availability and reliability are paramount for all web applications and APIs. If you’re providing an API, chances are you’ve already experienced sudden increases in traffic that affect the quality of your service, potentially even leading to a service outage for all your users.

The first few times this happens, it’s reasonable to just add more capacity to your infrastructure to accommodate user growth. However, when you’re running a production API, not only do you have to make it robust with techniques like [idempotency](https://stripe.com/blog/idempotency), you also need to build for scale and ensure that one bad actor can’t accidentally or deliberately affect its availability.

Rate limiting can help make your API more reliable in the following scenarios:

- One of your users is responsible for a spike in traffic, and you need to stay up for everyone else.
- One of your users has a misbehaving script which is accidentally sending you a lot of requests. Or, even worse, one of your users is intentionally trying to overwhelm your servers.
- A user is sending you a lot of lower-priority requests, and you want to make sure that it doesn’t affect your high-priority traffic. For example, users sending a high volume of requests for analytics data could affect critical transactions for other users.
- Something in your system has gone wrong internally, and as a result you can’t serve all of your regular traffic and need to drop low-priority requests.

At Stripe, we’ve found that carefully implementing a few [rate limiting](https://en.wikipedia.org/wiki/Rate_limiting) strategies helps keep the API available for everyone. In this post, we’ll explain in detail which rate limiting strategies we find the most useful, how we prioritize some API requests over others, and how we started using rate limiters safely without affecting our existing users’ workflows.

------

## Rate limiters and load shedders

A *rate limiter* is used to control the rate of traffic sent or received on the network. When should you use a rate limiter? If your users can afford to change the pace at which they hit your API endpoints without affecting the outcome of their requests, then a rate limiter is appropriate. If spacing out their requests is not an option (typically for real-time events), then you’ll need another strategy outside the scope of this post (most of the time you just need more infrastructure capacity).

Our users can make a lot of requests: for example, batch processing payments causes sustained traffic on our API. We find that clients can always (barring some extremely rare cases) spread out their requests a bit more and not be affected by our rate limits.

Rate limiters are amazing for day-to-day operations, but during incidents (for example, if a service is operating more slowly than usual), we sometimes need to drop low-priority requests to make sure that more critical requests get through. This is called *load shedding*. It happens infrequently, but it is an important part of keeping Stripe available.

A *load shedder* makes its decisions based on the whole state of the system rather than the user who is making the request. Load shedders help you deal with emergencies, since they keep the core part of your business working while the rest is on fire.

------

## Using different kinds of rate limiters in concert

Once you know rate limiters can improve the reliability of your API, you should decide which types are the most relevant.

At Stripe, we operate 4 different types of limiters in production. The first one, the *Request Rate Limiter*, is by far the most important one. We recommend you start here if you want to improve the robustness of your API.

### Request rate limiter

This rate limiter restricts each user to *N* requests per second. Request rate limiters are the first tool most APIs can use to effectively manage a high volume of traffic.

Our rate limits for requests is constantly triggered. It has rejected millions of requests this month alone, especially for test mode requests where a user inadvertently runs a script that’s gotten out of hand.

Our API provides the same rate limiting behavior in both test and live modes. This makes for a good developer experience: scripts won't encounter side effects due to a particular rate limit when moving from development to production.

After analyzing our traffic patterns, we added the ability to briefly burst above the cap for sudden spikes in usage during real-time events (e.g. a flash sale.)

![img](/img/1-request-rate-limiter-932b66006916fed9452bc10f3944ce6d64b36ff4.svg)

Request rate limiters restrict users to a maximum number of requests per second.

### Concurrent requests limiter

Instead of “You can use our API 1000 times a second”, this rate limiter says “You can only have 20 API requests in progress at the same time”. Some endpoints are much more resource-intensive than others, and users often get frustrated waiting for the endpoint to return and then retry. These retries add more demand to the already overloaded resource, slowing things down even more. The concurrent rate limiter helps address this nicely.

Our concurrent request limiter is triggered much less often (12,000 requests this month), and helps us keep control of our CPU-intensive API endpoints. Before we started using a concurrent requests limiter, we regularly dealt with resource contention on our most expensive endpoints caused by users making too many requests at one time. The concurrent request limiter totally solved this.

It is completely reasonable to tune this limiter up so it rejects more often than the Request Rate Limiter. It asks your users to use a different programming model of “Fork off X jobs and have them process the queue” compared to “Hammer the API and back off when I get a HTTP 429”. Some APIs fit better into one of those two patterns so feel free to use which one is most suitable for the users of your API.

![img](https://b.stripecdn.com/site-srv/assets/img/blog/posts/rate-limiters/2-concurrent-requests-limiter-2bd58bae3d4b1ae3e250bffef6c6663234d53ea0.svg)

Concurrent request limiters manage resource contention for CPU-intensive API endpoints.

### Fleet usage load shedder

Using this type of load shedder ensures that a certain percentage of your fleet will always be available for your most important API requests.

We divide up our traffic into two types: critical API methods (e.g. creating charges) and non-critical methods (e.g. listing charges.) We have a Redis cluster that counts how many requests we currently have of each type.

We always reserve a fraction of our infrastructure for critical requests. If our reservation number is 20%, then any non-critical request over their 80% allocation would be rejected with status code 503.

We triggered this load shedder for a very small fraction of requests this month. By itself, this isn’t a big deal—we definitely had the ability to handle those extra requests. But we’ve had other months where this has prevented outages.

![img](https://b.stripecdn.com/site-srv/assets/img/blog/posts/rate-limiters/3-fleet-usage-load-shedder-cea89ac2145de1015fb1027e971371f7acc0bab5.svg)

Fleet usage load shedders reserves fleet resources for critical requests.

### Worker utilization load shedder

Most API services use a set of workers to independently respond to incoming requests in a parallel fashion. This load shedder is the final line of defense. If your workers start getting backed up with requests, then this will shed lower-priority traffic.

This one gets triggered very rarely, only during major incidents.

We divide our traffic into 4 categories:

1. Critical methods
2. POSTs
3. GETs
4. Test mode traffic

We track the number of workers with available capacity at all times. If a box is too busy to handle its request volume, it will slowly start shedding less-critical requests, starting with test mode traffic. If shedding test mode traffic gets it back into a good state, great! We can start to slowly bring traffic back. Otherwise, it’ll escalate and start shedding even more traffic.

It’s very important that shedding and bringing load happen slowly, or you can end up flapping (“I got rid of testmode traffic! Everything is fine! I brought it back! Everything is awful!”). We used a lot of trial and error to tune the rate at which we shed traffic, and settled on a rate where we shed a substantial amount of traffic within a few minutes.

Only 100 requests were rejected this month from this rate limiter, but in the past it’s done a lot to help us recover more quickly when we have had load problems. This load shedder limits the impact of incidents that are already happening and provides damage control, while the first three are more preventative.

![img](https://b.stripecdn.com/site-srv/assets/img/blog/posts/rate-limiters/4-worker-utilization-load-shedder-d928a534123d18207df897fe15b282f1d16c9923.svg)

Worker utilization load shedders reserve workers for critical requests.

------

## Building rate limiters in practice

Now that we’ve outlined the four basic kinds of rate limiters we use and what they’re for, let’s talk about their implementation. What rate limiting algorithms are there? How do you actually implement them in practice?

We use the [token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket) to do rate limiting. This algorithm has a centralized bucket host where you take tokens on each request, and slowly drip more tokens into the bucket. If the bucket is empty, reject the request. In our case, every Stripe user has a bucket, and every time they make a request we remove a token from that bucket.

We implement our rate limiters using Redis. You can either operate the Redis instance yourself, or, if you use Amazon Web Services, you can use a managed service like [ElastiCache](https://aws.amazon.com/elasticache/).

Here are important things to consider when implementing rate limiters:

- **Hook the rate limiters into your middleware stack safely.** Make sure that if there were bugs in the rate limiting code (or if Redis were to go down), requests wouldn’t be affected. This means catching exceptions at all levels so that any coding or operational errors would fail open and the API would still stay functional.
- **Show clear exceptions to your users.** Figure out what kinds of exceptions to show your users. In practice, you should decide if you want [HTTP 429](https://tools.ietf.org/html/rfc6585#section-4) (Too Many Requests) or [HTTP 503](https://tools.ietf.org/html/rfc7231#section-6.6.4) (Service Unavailable) and what is the most accurate depending on the situation. The message you return should also be actionable.
- **Build in safeguards so that you can turn off the limiters.** Make sure you have kill switches to disable the rate limiters should they kick in erroneously. Having feature flags in place can really help should you need a human escape valve. Set up alerts and metrics to understand how often they are triggering.
- **Dark launch each rate limiter to watch the traffic they would block.** Evaluate if it is the correct decision to block that traffic and tune accordingly. You want to find the right thresholds that would keep your API up without affecting any of your users’ existing request patterns. This might involve working with some of them to change their code so that the new rate limit would work for them.

------

## Conclusion

Rate limiting is one of the most powerful ways to prepare your API for scale. The different rate limiting strategies described in this post are not all necessary on day one, you can gradually introduce them once you realize the need for rate limiting.

Our recommendation is to follow the following steps to introduce rate limiting to your infrastructure:

1. Start by building a Request Rate Limiter. It is the most important one to prevent abuse, and it’s by far the one that we use the most frequently.
2. Introduce the next three types of rate limiters over time to prevent different classes of problems. They can be built slowly as you scale.
3. Follow good launch practices as you're adding new rate limiters to your infrastructure. Handle any errors safely, put them behind feature flags to turn them off easily at any time, and rely on very good observability and metrics to see how often they’re triggering.



# Scaling your API with rate limiters

The following are examples of the four types rate limiters discussed in the [accompanying blog post](https://stripe.com/blog/rate-limiters). In the examples below I've used pseudocode-like Ruby, so if you're unfamiliar with Ruby you should be able to easily translate this approach to other languages. Complete examples in Ruby are also provided later in this gist.

In most cases you'll want all these examples to be classes, but I've used simple functions here to keep the code samples brief.

## Request rate limiter

This uses a basic token bucket algorithm and relies on the fact that Redis scripts execute atomically. No other operations can run between fetching the count and writing the new count.

The [full script with a small test suite is available](#file-1-check_request_rate_limiter-rb), but here is a sketch:

```ruby
# How many requests per second do you want a user to be allowed to do?
REPLENISH_RATE = 100

# How much bursting do you want to allow?
CAPACITY = 5 * REPLENISH_RATE

SCRIPT = File.read('request_rate_limiter.lua')

def check_request_rate_limiter(user)
  # Make a unique key per user.
  prefix = 'request_rate_limiter.' + user

  # You need two Redis keys for Token Bucket.
  keys = [prefix + '.tokens', prefix + '.timestamp']

  # The arguments to the LUA script. time() returns unixtime in seconds.
  args = [REPLENISH_RATE, CAPACITY, Time.new.to_i, 1]

  begin
    allowed, tokens_left = redis.eval(SCRIPT, keys, args)
  rescue RedisError => e
    # Fail open. We don't want a hard dependency on Redis to allow traffic.
    # Make sure to set an alert so you know if this is happening too much.
    # Our observed failure rate is 0.01%.
    puts 'Redis failed: ' + e
    return
  end

  if !allowed
    raise RateLimitError.new(status_code = 429)
  end
end
```

Here is the corresponding `request_rate_limiter.lua` script:

```lua
local tokens_key = KEYS[1]
local timestamp_key = KEYS[2]

local rate = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local fill_time = capacity/rate
local ttl = math.floor(fill_time*2)

local last_tokens = tonumber(redis.call("get", tokens_key))
if last_tokens == nil then
  last_tokens = capacity
end

local last_refreshed = tonumber(redis.call("get", timestamp_key))
if last_refreshed == nil then
  last_refreshed = 0
end

local delta = math.max(0, now-last_refreshed)
local filled_tokens = math.min(capacity, last_tokens+(delta*rate))
local allowed = filled_tokens >= requested
local new_tokens = filled_tokens
if allowed then
  new_tokens = filled_tokens - requested
end

redis.call("setex", tokens_key, ttl, new_tokens)
redis.call("setex", timestamp_key, ttl, now)

return { allowed, new_tokens }
```

## Concurrent requests limiter

Because Redis is so fast, doing the naive thing works. Just add a random token to a set at the start of a request and remove it from the set when you're done. If the set is too large, reject the request.

Again the [full code is available](#file-2-check_concurrent_requests_limiter-rb) and a sketch follows:

```ruby
# The maximum length a request can take
TTL = 60

# How many concurrent requests a user can have going at a time
CAPACITY = 100

SCRIPT = File.read('concurrent_requests_limiter.lua')

class ConcurrentRequestLimiter
  def check(user)
    @timestamp = Time.new.to_i

    # A string of some random characters. Make it long enough to make sure two machines don't have the same string in the same TTL.
    id = Random.new.bytes(4)
    key = 'concurrent_requests_limiter.' + user
    begin
      # Clear out old requests that probably got lost
      redis.zremrangebyscore(key, '-inf', @timestamp - TTL)
      keys = [key]
      args = [CAPACITY, @timestamp, id]
      allowed, count = redis.eval(SCRIPT, keys, args)
    rescue RedisError => e
      # Similarly to above, remember to fail open so Redis outages don't take down your site
      log.info('Redis failed: ' + e)
      return
    end

    if allowed
      # Save it for later so we can remove it when the request is done
      @id_in_redis = id
    else
      raise RateLimitError.new(status_code: 429)
    end
  end

  # Call this method after a request finishes
  def post_request_bookkeeping(user)
    if not @id_in_redis
      return
    end
    key = 'concurrent_requests_limiter.' + user
    removed = redis.zrem(key, @id_in_redis)
  end

  def do_request(user)
    check(user)

    # Do the actual work here

    post_request_bookkeeping(user)
  end
end
```

The content of `concurrent_requests_limiter.lua` is simple and is meant to guarantee the atomicity of the ZCARD and ZADD.

```lua
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local timestamp = tonumber(ARGV[2])
local id = ARGV[3]

local count = redis.call("zcard", key)
local allowed = count < capacity

if allowed then
  redis.call("zadd", key, timestamp, id)
end

return { allowed, count }
```

## Fleet usage load shedder

We can now move from preventing abuse to adding stability to your site with load shedders. If you can categorize traffic into buckets where no fewer than X% of your workers should be available to process high-priority traffic, then you're in luck: this type of algorithm can help. We call it a _load shedder_ instead of a rate limiter because it isn't trying to reduce the rate of a specific user's requests. Instead, it adds backpressure so internal systems can recover. 

When this load shedder kicks in it will start dropping non-critical traffic. There should be alarm bells ringing and people should be working to get the traffic back, but at least your core traffic will work. For Stripe, high-priority traffic has to do with creating charges and moving money around, and low-priority traffic has to do with analytics and reporting.

The great thing about this load shedder is that its implementation is identical to the Concurrent Requests Limiter, except you don't use a user-specific key, you just use a global key.

```ruby
limiter = ConcurrentRequestLimiter.new
def check_fleet_usage_load_shedder
  if is_high_priority_request
    return
  end

  begin
    return limiter.do_request('fleet_usage_load_shedder')
  rescue RateLimitError
    raise RateLimitError.new(status_code: 503)
  end
end
```

## Worker utilization load shedder

This load shedder is the last resort, and only kicks in when a machine is under heavy pressure and needs to offload. The code for determining how many workers are in use is dependent on your infrastructure. The general outline is to figure out some measure of "Is our infrastructure currently failing?" If that function returns something non-zero, start throwing out your least important requests (after waiting a short period to allow imprecise measurements) with higher and higher probability. After a period of time doing that, move on to more requests until you are throwing out everything except for the most critical traffic.

The most important behavior for this load shedder is to slowly take action. Don't start throwing out traffic until your infrastructure has been sad for quite a while (30 seconds), and don't instantaneously add traffic back. Sharp changes in shedding amounts will cause wild swings and lead to failure modes that are hard to diagnose.

As before, the [full script with a small test suite is available](#file-3-check_worker_utilization_load_shedder-rb), and here is a sketch:

```ruby
END_OF_GOOD_UTILIZATION = 0.7
START_OF_BAD_UTILIZATION = 0.8

# Assuming a sample rate of 8 seconds, so 28 == 2.5 * 8 == guaranteed 3 samples
NUMBER_OF_SECONDS_BEFORE_SHEDDING_STARTS = 28
NUMBER_OF_SECONDS_TO_SHED_ALL_TRAFFIC = 120

RESTING_SHED_AMOUNT = -NUMBER_OF_SECONDS_BEFORE_SHEDDING_STARTS / NUMBER_OF_SECONDS_TO_SHED_ALL_TRAFFIC

@shedding_amount_last_changed = 0
@shedding_amount = 0

def check_worker_utilization_load_shedder
  chance = drop_chance(current_worker_utilization)
  if chance == 0
    dropped = false
  else
    dropped = Random.rand() < chance
  end
  if dropped
    raise RateLimitError.new(status_code: 503)
  end
end

def drop_chance(utilization)
  update_shedding_amount_derivative(utilization)
  how_much_traffic_to_shed
end

def update_shedding_amount_derivative(utilization)
  # A number from -1 to 1
  amount = 0

  # Linearly reduce shedding
  if utilization < END_OF_GOOD_UTILIZATION
    amount = utilization / END_OF_GOOD_UTILIZATION - 1
  # A dead zone
  elsif utilization < START_OF_BAD_UTILIZATION
    amount = 0
  # Shed traffic
  else
    amount = (utilization - START_OF_BAD_UTILIZATION) / (1 - START_OF_BAD_UTILIZATION)
  end

  # scale the derivative so we take time to shed all the traffic
  @shedding_amount_derivative = clamp(amount, -1, 1) / NUMBER_OF_SECONDS_TO_SHED_ALL_TRAFFIC
end

def how_much_traffic_to_shed
  now = Time.now().to_f
  seconds_since_last_math = clamp(now - @shedding_amount_last_changed, 0, NUMBER_OF_SECONDS_BEFORE_SHEDDING_STARTS)
  @shedding_amount_last_changed = now
  @shedding_amount += seconds_since_last_math * @shedding_amount_derivative
  @shedding_amount = clamp(@shedding_amount, RESTING_SHED_AMOUNT, 1)
end

def current_worker_utilization
  # Returns a double from 0 to 1.
  # 1 means every process is busy, .5 means 1/2 the processes are working, and 0 means the machine is servicing 0 requests
  # This is infra dependent on how to read this value
end

def clamp(val, min, max)
  if val < min
    return min
  elsif val > max
    return max
  else
    return val
  end
end
```