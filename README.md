# rest_social
Social network on Django Rest Framework
## Requests:
**1.	/register/**

POST request for registration. Requires 3 fields. 

{
 "username": "...",
 "password": "...",
 "email": "..."
}

Creates a new user with validated credentials, hashed password.

Codes of responses:
-	400 – Incorrect post data. It may be problem with formatting or syntax.
-	201 – User is created. Success.

**2.	/login/**

POST request for authorization. Requires 2 fields – username and password.

{
  "username": "...",
  "password": "..."
}

Authenticates user (if it’s possible) and return JWT token, which user should add as header (with key ‘token’) for each next request, that requires authentication.

Codes of responses:
-	400 – Incorrect post data.
-	200 – Successful authorization, responded with JWT token.

**3.	/add-post/**

POST request, which helps to create a new post. Requires token and content-type (“application/json”) headers.

{
  "title": "...",
  "content": "..."
}

Codes of responses:
-	400 – Bad request
-	403 – Forbidden access for actual user or failed auth checking.
-	200 – Correct response with JSON of all user’s chats.

**4. /posts/**

GET request for returning all posts in DB with pagination ability. Requires token and content-type headers, and 1 parameter in request – NUM_PAGE (integer value for pagination feature. By default, it will show first page).

Codes of responses:
-	400 – Incorrect parameters added.
-	404 – Invalid page number.
-	403 – Failed auth checking.
-	200 – Success.

**5.	/post/POST_ID**

GET request for retrieving specific post. Required one parameter - POST_ID number.

Codes of responses:
-	400 – Bad request structure or incorrect POST data.
-	403 – Non auth user.
-	200 – Success.

**6.	/change-mark/**

POST request for setting like / unlike. Format of changing has to be displayed in the fields.
If you want to set like, that it should be: like = 1, unlike = 0; and vice versa.

{
	“post_id”: ..,
	“like”: "...”,
	"unlike": "..."
}

Codes of responses:
-	400 – Bad request structure or incorrect POST data.
-	403 – Non auth user.
-	200 – Successful mark changing.

##### Aditional techniques:
* unit tests (in the tests folder)
* custom authorization (with JWT usage)
* custom pagination (for the /posts/ endpoint)
* emailhunter.co email verification

Required modules are in the requirements.txt. Also you need to create .env file with sensitive data
(secret key and emailhunter API key)