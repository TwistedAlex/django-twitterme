# django-twitterme

## Tech Stack: 
  Python, Django REST Framework, MySQL, HBase, Redis, Memcached, RabbitMQ, Amazon S3/EC2, Thrift, 
 
## Summary:
  This project is to design, develop, and implement Restful APIs to operate Twitter-like backend service as close to real-world development as possible based on Django REST Framework. For performance optimization, structured and unstructured databases are both implemented in this project according to the nature of the tables.

•	Built push model to fanout news feeds

•	Leveraged Redis and Memcached to reduce DB queries for tables which has lot reads and lot writes

•	Used Key-value store HBase to split DB queries for tables which has less reads and lot writes

•	Utilized denormalization to store the number of comments & likes to reduce DB queries

•	Adapted Message Queue to deliver asynchronized tasks to reduce response time

•	The whole project resulted in 10000 lines of code changes, cost over 3 months

## Features:

- User Authentification: Allow users to log in or sign up with emails 
- Allow users to follow, unfollow other users
- Allow users to view, comment, and like others' posts, also users can cancel their comments and likes on the posts
- Allow users to create, delete, update posts and view the count of likes and comments of their posts
- Send out newfeeds to followers
- Display tweets in newfeeds in endless pagination format 

## APIs

**User and Profile**

`GET /api/users/`   Only admin users have the access permission. <br />

`POST /api/accounts/signup/`  It also creates user profile. <br />
`POST /api/accounts/login/` <br />
`POST /api/accounts/logout/` <br />
`GET /api/accounts/login_status/` <br />

`PUT /api/profiles/:profile_id`    Updates nickname and/or avatar. <br />

**Tweet**

`GET /api/tweets/?user_id=xxx`  <br />

`POST /api/tweets/`  <br />

`GET /api/tweets/:id`  <br />

**Friendship**

`POST /api/friendships/:user_id/follow/` <br />
`POST /api/friendships/:user_id/unfollow/` <br />
`GET /api/friendships/:user_id/followings/` <br />
`GET /api/friendships/:user_id/followers/` <br />

**Newsfeed**

`GET /api/newsfeeds/`  <br />
Endless Pagination![image](https://user-images.githubusercontent.com/40569707/189262557-60712db8-88af-4bc1-8f0d-0632c3abcc4d.png) <br />

**Comment**

`POST /api/comments/`      <br />
`PUT /api/comments/:id`     <br />
`DELETE /api/comments/:id`     <br />
`GET /api/comments/?tweet_id=xxx`   <br />
 
**Like**

`POST /api/likes/`      <br />
`POST /api/likes/cancel/`      <br />

**Notification**

`GET /api/notifications/`    <br />
`GET /api/notifications/unread-count/` <br />
`POST /api/notifications/mark-all-as-read/` <br />
`PUT /api/notifications/:notification_id`    <br />

## django_hbase Module

  Django Rest Framework alike ORM to access hbase.<br />
  
  Implemented functions:
    Deine models and fields similar to DRF.
    Save, create, filter operations similar to Django ORM.
  
## GateKeeper Module(Rate limiter):

  Function: GrayRelease, Whitelisting, Reverse Commit
## System Architecture
![image](https://user-images.githubusercontent.com/40569707/189264018-b3a68d48-c711-47d2-b36a-938307bc3375.png)
