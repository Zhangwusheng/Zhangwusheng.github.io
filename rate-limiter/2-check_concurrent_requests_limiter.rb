require_relative 'shared'

# The maximum length a request can take
TTL = 60

# How many concurrent requests a user can have going at a time
CAPACITY = 100

SCRIPT = File.read('concurrent_requests_limiter.lua')

def check_concurrent_requests_limiter(user)
  @timestamp = Time.new().to_i

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
  check_concurrent_requests_limiter(user)

  # Do the actual work here

  post_request_bookkeeping(user)
end

def test_check_concurrent_requests_limiter
  id = Random.rand(1000000).to_s

  # Pounding the server is fine as long as you finish the request
  for i in 0..CAPACITY*10
    do_request(id)
  end

  # But concurrent is not
  for i in 0..CAPACITY-1
    check_concurrent_requests_limiter(id)
  end
  begin
    check_concurrent_requests_limiter(id)
    raise "it didn't work"
  rescue
    puts "it worked"
  end
end

test_check_concurrent_requests_limiter