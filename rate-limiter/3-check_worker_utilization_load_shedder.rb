require_relative 'shared'

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
  @current_worker_utilization # For easy stubbing in the test example
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

def test_check_worker_utilization_load_shedder
  # Business as usual
  @current_worker_utilization = 0
  for i in (0..1000)
    check_worker_utilization_load_shedder
  end

  # Workers are exhausted
  @current_worker_utilization = 1
  shed_count = 0
  for i in (0..NUMBER_OF_SECONDS_BEFORE_SHEDDING_STARTS + NUMBER_OF_SECONDS_TO_SHED_ALL_TRAFFIC)
    begin
      check_worker_utilization_load_shedder
    rescue RateLimitError
      shed_count += 1
    end
    sleep 1
  end
  puts "#{shed_count} requests were dropped" # Should be ~60

  # Should be shedding all traffic
  begin
    check_worker_utilization_load_shedder
    raise "it didn't work"
  rescue RateLimitError
    puts "it worked"
  end
end

test_check_worker_utilization_load_shedder