# Flow

This page will present you a complete registration and authentication flow once you've setup **FastAPI Users**. Each example will be presented with a `cURL` and an `axios` example.

## 1. Registration

First step, of course, is to register as a user.

### Request

=== "cURL"
    ``` bash
    curl \
    -H "Content-Type: application/json" \
    -X POST \
    -d "{\"email\": \"king.arthur@camelot.bt\",\"password\": \"guinevere\"}" \
    http://localhost:8000/auth/register
    ```

=== "axios"
    ```ts
    axios.post('http://localhost:8000/auth/register', {
        email: 'king.arthur@camelot.bt',
        password: 'guinevere',
    })
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

### Response

You'll get a JSON response looking like this:

```json
{
    "id": "4fd3477b-eccf-4ee3-8f7d-68ad72261476",
    "email": "king.arthur@camelot.bt",
    "is_active": true,
    "is_superuser": false
}
```

!!! info
    Several things to bear in mind:

    * If you have defined other required fields in your `User` model (like a first name or a birthdate), you'll have to provide them in the payload.
    * The user is active by default.
    * The user cannot set `is_active` or `is_superuser` itself at registration. Only a superuser can do it by PATCHing the user.

## 2. Login

Now, you can login as this new user.

You can generate a [login route](../configuration/routers/auth.md) for each [authentication backend](../configuration/authentication/index.md). Each backend will have a different response.

### JWT backend

#### Request

=== "cURL"
    ``` bash
    curl \
    -H "Content-Type: multipart/form-data" \
    -X POST \
    -F "username=king.arthur@camelot.bt" \
    -F "password=guinevere" \
    http://localhost:8000/auth/jwt/login
    ```

=== "axios"
    ```ts
    const formData = new FormData();
    formData.set('username', 'king.arthur@camelot.bt');
    formData.set('password', 'guinevere');
    axios.post(
        'http://localhost:8000/auth/jwt/login',
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

!!! warning
    Notice that we don't send it as a JSON payload here but with **form data** instead. Also, the email is provided by a field named **`username`**.

#### Response

You'll get a JSON response looking like this:

```json
{
    "access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiNGZkMzQ3N2ItZWNjZi00ZWUzLThmN2QtNjhhZDcyMjYxNDc2IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTg3ODE4NDI5fQ.anO3JR8-WYCozZ4_2-PQ2Ov9O38RaLP2RAzQIiZhteM",
    "token_type": "bearer"
}
```

You can use this token to make authenticated requests as the user `king.arthur@camelot.bt`. We'll see how in the next section.

### Cookie backend

#### Request

=== "cURL"
    ``` bash
    curl \
    -v \
    -H "Content-Type: multipart/form-data" \
    -X POST \
    -F "username=king.arthur@camelot.bt" \
    -F "password=guinevere" \
    http://localhost:8000/auth/cookie/login
    ```

=== "axios"
    ```ts
    const formData = new FormData();
    formData.set('username', 'king.arthur@camelot.bt');
    formData.set('password', 'guinevere');
    axios.post(
        'http://localhost:8000/auth/cookie/login',
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

!!! warning
    Notice that we don't send it as a JSON payload here but with **form data** instead. Also, the email is provided by a field named **`username`**.

#### Response

You'll get a empty response. However, the response will come with a `Set-Cookie` header (that's why we added the `-v` option in `cURL` to see them).

```
set-cookie: fastapiusersauth=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYzYwNjBmMTEtNTM0OS00YTI0LThiNGEtYTJhODc1ZGM1Mzk1IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTg3ODE4OTQ3fQ.qNA4oPVYhoqrJIk-zvAyEfEVoEnP156G30H_SWEU0sU; HttpOnly; Max-Age=3600; Path=/; Secure
```

You can make authenticated requests as the user `king.arthur@camelot.bt` by setting a `Cookie` header with this cookie.

!!! tip
    The cookie backend is more suited for browsers, as they handle them automatically. This means that if you make a login request in the browser, it will automatically store the cookie and automatically send it in subsequent requests.

## 3. Get my profile

Now that we can authenticate, we can get our own profile data. Depending on your [authentication backend](../configuration/authentication/index.md), the method to authenticate the request will vary. We'll stick with JWT from now on.

### Request

=== "cURL"
    ``` bash
    export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiNGZkMzQ3N2ItZWNjZi00ZWUzLThmN2QtNjhhZDcyMjYxNDc2IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTg3ODE4NDI5fQ.anO3JR8-WYCozZ4_2-PQ2Ov9O38RaLP2RAzQIiZhteM";
    curl \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -X GET \
    http://localhost:8000/users/me
    ```

=== "axios"
    ```ts
    const TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiNGZkMzQ3N2ItZWNjZi00ZWUzLThmN2QtNjhhZDcyMjYxNDc2IiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNTg3ODE4NDI5fQ.anO3JR8-WYCozZ4_2-PQ2Ov9O38RaLP2RAzQIiZhteM';
    axios.get(
        'http://localhost:8000/users/me', {
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
        },
    })
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

### Response

You'll get a JSON response looking like this:

```json
{
    "id": "4fd3477b-eccf-4ee3-8f7d-68ad72261476",
    "email": "king.arthur@camelot.bt",
    "is_active": true,
    "is_superuser": false
}
```

!!! tip
    If you use one of the [dependency callable](./dependency-callables.md) to protect one of your own endpoint, you'll have to authenticate exactly in the same way.

## 4. Update my profile

We can also update our own profile. For example, we can change our password like this.

### Request

=== "cURL"
    ``` bash
    curl \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -X PATCH \
    -d "{\"password\": \"lancelot\"}" \
    http://localhost:8000/users/me
    ```

=== "axios"
    ```ts
    axios.patch(
        'http://localhost:8000/users/me',
        {
            password: 'lancelot',
        },
        {
            headers: {
                'Authorization': `Bearer ${TOKEN}`,
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

### Response

You'll get a JSON response looking like this:

```json
{
    "id": "4fd3477b-eccf-4ee3-8f7d-68ad72261476",
    "email": "king.arthur@camelot.bt",
    "is_active": true,
    "is_superuser": false
}
```

!!! info
    Once again, the user cannot set `is_active` or `is_superuser` itself. Only a superuser can do it by PATCHing the user.

## 5. Become a superuser 🦸🏻‍♂️

If you want to manage the users of your application, you'll have to become a **superuser**.

The very first superuser can only be set at **database level**: open it through a CLI or a GUI, find your user and set the `is_superuser` column/property to `true`.

### 5.1. Get the profile of any user

Now that you are a superuser, you can leverage the power of [superuser routes](./routes.md#superuser). You can for example get the profile of any user in the database given its id.

#### Request

=== "cURL"
    ``` bash
    curl \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -X GET \
    http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476
    ```

=== "axios"
    ```ts
    axios.get(
        'http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476', {
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
        },
    })
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

#### Response

You'll get a JSON response looking like this:

```json
{
    "id": "4fd3477b-eccf-4ee3-8f7d-68ad72261476",
    "email": "king.arthur@camelot.bt",
    "is_active": true,
    "is_superuser": false
}
```

### 5.1. Update any user

We can now update the profile of any user. For example, we can promote it as superuser.

#### Request

=== "cURL"
    ``` bash
    curl \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -X PATCH \
     -d "{\"is_superuser\": true}" \
    http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476
    ```

=== "axios"
    ```ts
    axios.patch(
        'http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476',
        {
            is_superuser: true,
        },
        {
            headers: {
                'Authorization': `Bearer ${TOKEN}`,
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

#### Response

You'll get a JSON response looking like this:

```json
{
    "id": "4fd3477b-eccf-4ee3-8f7d-68ad72261476",
    "email": "king.arthur@camelot.bt",
    "is_active": true,
    "is_superuser": true
}
```

### 5.2. Delete any user

Finally, we can delete a user.

#### Request

=== "cURL"
    ``` bash
    curl \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -X DELETE \
    http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476
    ```

=== "axios"
    ```ts
    axios.delete(
        'http://localhost:8000/users/4fd3477b-eccf-4ee3-8f7d-68ad72261476',
        {
            headers: {
                'Authorization': `Bearer ${TOKEN}`,
            },
        },
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

#### Response

You'll get an empty response.

## 6. Logout

We can also end the session. Note that it doesn't apply to every [authentication backends](../configuration/authentication/index.md). For JWT, it doesn't make sense to end the session, the token is valid until it expires. However, for **Cookie** backend, the server will clear the cookie.

### Request

=== "cURL"
    ``` bash
    curl \
    -H "Content-Type: application/json" \
    -H "Cookie: fastapiusersauth=$TOKEN" \
    -X POST \
    http://localhost:8000/auth/cookie/logout
    ```

=== "axios"
    ```ts
    axios.post('http://localhost:8000/auth/cookie/logout',
        null,
        {
            headers: {
                'Cookie': `fastapiusersauth=${TOKEN}`,
            },
        }
    )
    .then((response) => console.log(response))
    .catch((error) => console.log(error));
    ```

### Response

You'll get an empty response.

## Conclusion

That's it! You now have a good overview of how you can manage the users through the API. Be sure to check the [Routes](./routes.md) page to have all the details about each endpoints.
