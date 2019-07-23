---
layout:     post
title:     Do You Really Know CORS?
subtitle:   What do you really know about Cross-Origin Resource Sharing? Check out this post to learn more about CORS and the Same-Origin Policy for improving app security. 
date:       2019-05-22
author:     老张
header-img: img/post-bg-2015.jpg
catalog: true
tags:
    - CORS
    - Cross-Origin
    - Same-Origin Policy
    - SOP
typora-copy-images-to: ..\img
typora-root-url: ..
---

# Do You Really Know CORS? 

## Cross-Origin Resource Sharing

*No 'Access-Control-Allow-Origin' header is present on the requested resource. Origin http://www.sesamestreet.com is, therefore, not allowed access.*



If you work with a frontend, sometimes, the chances are that  you’ve seen the error above before. When it had happened to you for the  first time, as any proper developer does, you googled it. As a result,  you have probably seen some advice on StackOverflow that includes`Access-Control-Allow-Origin` in your server’s response, and then, you can happily return to your code.

Surprisingly, this is the end of the experience with  Cross-Origin Resource Sharing (CORS) for many developers. They know how  to fix the problem, but they don’t always understand why the problem  exists in the first place. In this article, we will dive deeper into  this topic, trying to understand what problem CORS really solves.  However, we will start with the Same-Origin Policy (SOP) concept.

## What Is the Same-Origin Policy?

SOP is a security mechanism implemented in almost all of the  modern browsers. It does not allow documents or scripts loaded from one  origin to access resources from other origins. To understand why it’s so  critical, it’s important to realize that for any HTTP request to a  particular domain, browsers automatically attach any cookies bounded to  that domain. Let’s imagine a cookie — `my_cookie=oreo` — that is stored for the domain CookieMonster.com.



![cookie_1](/img/cookie-1.jpg)



CookieMonster.com is a single-page application that uses a  REST API exposed at CookieMonster.com/api. Thus, for every HTTP call to  the API, `my_cookie=oreo` will be attached to the request. 

Without Same-Origin Policy, the following scenario would be possible:

![cookie_2](/img/cookie-2.jpg)

SesameStreet.com could reuse the user’s cookie, which was previously stored for CookieMonster.com. Sounds scary? Not yet? Let’s look at the more thought-provoking scenario:

![cookie_3](/img/cookie-3.jpg)

And then:

![cookie_4](/img/cookie-4.jpg)



Without SOP, MaliciousWebsite.com would be able to send a  request to MyBank.com/api using the session cookie stored for  MyBank.com. Why is that? Because, as previously mentioned, browsers  automatically attach cookies bounded to a destination domain. It doesn’t  matter if a request originated from MyBank.com or MaliciousWebsite.com.  As long as a request goes to MyBank.com, the cookies stored for  MyBank.com would be used. As you can see, without Same-Origin Policy, a  Cross-Site Request Forgery (CSRF) attack can be relatively simple —  assuming that authentication is based solely on a session cookie, as  opposed to a token-based authentication. That’s one of the reasons the  SOP was introduced.

Having said that, it has always been possible for the  browser to make cross-origin requests by specifying a resource from a  foreign domain in the `<img>`, `<script>,` or `<iframe>`  tag — and if applicable, cookies might be attached. The crucial  difference is that AJAX call is fired from the JavaScript code, which  has total control and can be potentially dangerous. On the other hand,  tags are in the control of the browser, and no JS code can intercept  HTTP requests that they trigger.

### What Is Origin?

In the previous paragraph, I used domains as an example. But  Same-Origin Policy applies to origins. How is an origin defined? Two  origins are considered to be equal if they have the same protocol, host,  and port  — sometimes referred to as “scheme/host/port tuple." It  explains why we see this error — even if both our backend and frontend  run locally — they use different ports, and thus, they have different  origins.

## What Is CORS?

Even though some people call CORS a security mechanism, it’s  actually the opposite. It’s a way to relax security and make it less  restrictive. SOP is implemented in almost all modern browsers and  because of that, a website from one origin is not allowed to access  resources from foreign origins. CORS is a mechanism to make it possible.

### How Does CORS Work?

CORS defines two types of requests: simple requests and pre-flighted requests.

#### Simple Requests

To put it simply, a simple request is the one that doesn’t  trigger the preflight request. A request doesn’t trigger preflight  request if it meets all of the following conditions:

- Uses a GET, HEAD, or POST method
- Don’t have headers other than the small subset defined in the [specification](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Simple_requests) (any custom or authorization header breaks this condition)
- The only allowed values for Content-Type header are `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain` (`application/json `breaks this condition).

A typical scenario would be:

1. SesameStreet.com is opened in a browser tab. It initiates  AJAX request (using XMLHttpRequest or Fetch API) to GET  CookieMonster.com/api/monsters

2. The browser notices that this is a cross-origin request, and attaches Origin request header:

```
GET api/monsters HTTP/1.1
Host: cookiemonster.com
Origin: https://www.sesamestreet.com
...
```

3. The CORS-configured server checks the `Origin` header, and if the `Origin` is allowed, then it sets the `Access-Control-Allow-Origin` header to the `Origin`  value:

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://www.sesamestreet.com
...
```
4. When the response reaches the browser, the browser verifies if the value under the `Access-Control-Allow-Origin` header matches the origin of the tab the request originated from. 

#### Preflighted Requests

As described earlier, even adding a header, such as  Authorization, causes a request to be preflighted. A request is  pre-flighted if a browser first sends an additional preliminary OPTIONS  request (“preflight request”) in order to determine whether the actual  request (“pre-flighted request”) is safe to send. Let’s look at the  typical flow where we want to create a new monster resource:

1. A browser tab with SesameStreet.com makes AJAX POST  request to CookieMonster.com/api/monsters with a JSON payload using POST  method. The browser knows that sending POST with Content-Type different  from `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain` has to be pre-flighted, so it sends an OPTIONS request with three additional parameters:

- Origin — this one we already know
- Access-Control-Request-Method - HTTP method of the main (preflighted) request
- Access-Control-Request-Headers - HTTP headers of the main (preflighted) request



```
OPTIONS /api/monsters HTTP/1.1
Host: cookiemonster.com
Origin: https://www.sesamestreet.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
...
```



2. The server responds with the allowed origin, methods and headers.
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://www.sesamestreet.com
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```



3. If the origin is allowed and the HTTP method and headers  of the main request are on the list returned by the server, the main  request can be sent. This will be a regular cross-origin request, so it  will include the `Origin` header and the response will contain `Access-Control-Allow-Origin` once again.

Performance note: sending a preflight request every time can  be a performance overhead. This can be mitigated by caching preflight  requests using the `Access-Control-Max-Age` response header. 

## Common Misconception About CORS

At the first glance, CORS configuration on a server side  looks like some sort of ACL (Access Control List). A server returns the  origin that it accepts the requests from. The only way to access a  resource is to send a request from the origin whitelisted by a server,  right? Not really. Remember, that HTTP isn’t used only by browsers and  you can send an HTTP request from any client, like curl, Postman, and so  on. If you prepare a custom HTTP request in those tools, you can put  any `Origin` header you want. You can also skip it and a  server usually returns a correct result anyway. Why is that? Because as I  mentioned earlier, Same-Origin Policy is a concept implemented in  browsers. Other tools or software components don’t care about it that  much.

There is a simple implication based on what you've just  read. If there is a third-party API, which you want your webpage to  consume, but the API returns Access-Control-Allow-Origin header is set  to an origin other than your own, then you can circumvent that problem  by setting up a proxy server. Why? Because as described above, SOP  doesn’t apply server-to-server communication, only to browser-to-server  one.

## Is CORS Safe?

The most important question: is the CSRF scenario from the  beginning of this article possible using CORS? The answer is that it  depends. By default, **CORS does not include cookies into cross-origin requests**.  This is different from older cross-origin techniques, such as JSON-P  (JSON with Padding). This behavior greatly reduces CSRF vulnerabilities.  However, if you really want to send cookies in your request, you can  explicitly permit that. This requires coordination between both the  client and the server side. Your website must set the `withCredentials` property on the XMLHttpRequest to `true` (or `credentials` property in Fetch API set to `include`). Additionally, the server must respond with the `Access-Control-Allow-Credentials` header set to `true`.  With this combination, both parties agree to use credentials when  sending a cross-origin request. Credentials are cookies, authorization  headers, or TLS client certificates. Thankfully, there is one security  measure that prevents an excessive exhibitionism — the following  combination won’t work:


```
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: *
```

If you allow credentials to be sent, then `Access-Control-Allow-Origin`  cannot be set to the wildcard. The server must return an explicit  origin that is allowed to access the resource. The bad news is that many  servers blindly generate the `Access-Control-Allow-Origin` header based on the `Origin` value from the user’s request. If that’s the case, using `Access-Control-Allow-Credentials` set to `true` can be a serious security hole.









