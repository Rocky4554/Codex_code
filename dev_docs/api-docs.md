# API Documentation

This document describes all available endpoints in the Codex Platform application, including request/response examples, headers, and payloads for use in Postman or similar tools.

## Base URL

- Local: `http://localhost:8080`

## Authentication

Protected endpoints require:
- `Authorization: Bearer <token>`

## Common Error Responses

These are returned by the global exception handler:

### 400 Bad Request (validation / illegal argument)

```json
{ "error": "message" }
```

Or for validation errors:

```json
{
  "fieldName": "validation message"
}
```

### 401 Unauthorized

If you call a protected endpoint without a valid JWT, Spring Security returns `401`.

---

## 1. Authentication

### Register
- **Endpoint:** `POST /api/auth/register`
- **Headers:**
  - Content-Type: application/json
- **Request Body:**
```json
{
  "username": "string (3-50 chars)",
  "email": "user@example.com",
  "password": "string (min 6 chars)"
}
```
- **Response Example:**
```json
{
  "token": "jwt-token-string",
  "userId": "uuid",
  "username": "string",
  "email": "user@example.com"
}
```

### Login
- **Endpoint:** `POST /api/auth/login`
- **Headers:**
  - Content-Type: application/json
- **Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```
- **Response Example:**
```json
{
  "token": "jwt-token-string",
  "userId": "uuid",
  "username": "string",
  "email": "user@example.com"
}
```

---

## 2. User

> All endpoints require `Authorization: Bearer <token>` header.

### Get Profile
- **Endpoint:** `GET /api/user/profile`
- **Headers:**
  - Authorization: Bearer <token>
- **Response Example:**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "user@example.com",
  ...
}
```

### Get My Submissions
- **Endpoint:** `GET /api/user/submissions`
- **Headers:**
  - Authorization: Bearer <token>
- **Response Example:**
```json
[
  { "id": "uuid", "problemId": "uuid", "status": "string", ... },
  ...
]
```

### Get My Problems
- **Endpoint:** `GET /api/user/problems`
- **Headers:**
  - Authorization: Bearer <token>
- **Response Example:**
```json
[
  { "problemId": "uuid", "status": "string", ... },
  ...
]
```

---

## 3. Problems

### Get All Problems
- **Endpoint:** `GET /api/problems`
- **Response Example:**
```json
[
  { "id": "uuid", "title": "string", ... },
  ...
]
```

### Get Problem by ID
- **Endpoint:** `GET /api/problems/{id}`
- **Response Example:**
```json
{
  "id": "uuid",
  "title": "string",
  ...
}
```

> If the problem does not exist, the API returns `404 Not Found`.

---

## 4. Submissions

### Submit Code
- **Endpoint:** `POST /api/submissions`
- **Headers:**
  - Content-Type: application/json
  - Authorization: Bearer <token>
- **Request Body:**
```json
{
  "problemId": "uuid",
  "languageId": "uuid",
  "sourceCode": "string"
}
```
- **Response Example:**
```json
{
  "submissionId": "uuid",
  "status": "string",
  "message": "string"
}
```

---

## 5. Submission Events (SSE)

### Stream Submission Events
- **Endpoint:** `GET /api/submissions/{id}/events`
- **Headers:**
  - Accept: text/event-stream
  - Authorization: Bearer <token>
- **Response:**
  - Server-Sent Events stream for submission status updates.

---

## 6. Languages

### Get All Languages
- **Endpoint:** `GET /api/languages`
- **Response Example:**
```json
[
  { "id": "uuid", "name": "string", ... },
  ...
]
```

---

## Notes
- Replace `<token>` with the JWT token received from login/register.
- All UUIDs are standard UUID strings.
- Fields marked with `...` indicate additional properties returned by the API.
- Use the example payloads as templates in Postman.
