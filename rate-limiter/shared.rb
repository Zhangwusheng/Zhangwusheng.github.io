require 'redis'

class RateLimitError < RuntimeError; end
# In the real world this would be a class not a global variable
def redis
  $_redis ||= Redis.new
end