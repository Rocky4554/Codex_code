# Problems API Management Endpoints

This document tracks Problem and Language management APIs.

## Problem Endpoints

- `GET /api/problems` - list problems (public)
- `GET /api/problems/{id}` - get problem by id (public)
- `POST /api/problems` - create problem (auth required)
- `PUT /api/problems/{id}` - update problem (auth required)
- `DELETE /api/problems/{id}` - delete problem (auth required)

### Problem Request Body

```json
{
  "title": "Two Sum",
  "description": "Given an array of integers nums and an integer target...",
  "difficulty": "EASY",
  "timeLimitMs": 5000,
  "memoryLimitMb": 256
}
```

## Language Endpoints

- `GET /api/languages` - list languages (public)
- `POST /api/languages` - create language (auth required)
- `PUT /api/languages/{id}` - update language (auth required)
- `DELETE /api/languages/{id}` - delete language (auth required)

### Language Request Body

```json
{
  "name": "Python",
  "version": "3.11",
  "dockerImage": "python:3.11-slim",
  "fileExtension": ".py",
  "compileCommand": "",
  "executeCommand": "python solution.py"
}
```

## Troubleshooting

### Redis Cloud Connection
If the application fails to connect to Redis Cloud, check:
- **Address:** Port 11661 usually does NOT support SSL/TLS by default in free Redis Cloud tiers. Use `redis://` instead of `rediss://`.
- **Authentication:** Ensure `redisson.single-server-config.username` is set to `default` and the password is correct (check for case-sensitivity).
- **Configuration:** Use `RedissonConfig.java` to ensure custom properties are loaded over Spring auto-configuration.
