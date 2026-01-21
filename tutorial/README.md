# Tutorial Guide

This folder contains a progressive tutorial for learning OAuth2 authentication in FastAPI.

## 📚 Learning Path

Work through the files in order:

### Step 1: Basic FastAPI Application
**File:** `step1_basic.py`

Learn the basics of FastAPI before adding authentication.

```bash
uvicorn tutorial.step1_basic:app --reload
```

**Concepts:**
- Creating a FastAPI app
- Defining routes
- Using the automatic API docs

---

### Step 2: Password Hashing
**File:** `step2_password_hashing.py`

Learn how to securely store and verify passwords.

```bash
uvicorn tutorial.step2_password_hashing:app --reload
```

**Concepts:**
- Password hashing with bcrypt
- Why never store plain text passwords
- Verifying passwords
- User authentication

**Try:**
- POST `/login` with correct credentials
- POST `/login` with wrong credentials
- GET `/demo/hash/yourpassword` to see how hashing works

---

### Step 3: JWT Tokens
**File:** `step3_jwt_tokens.py`

Learn how to create and validate JWT tokens.

```bash
uvicorn tutorial.step3_jwt_tokens:app --reload
```

**Concepts:**
- What JWT tokens are
- Creating JWT tokens
- Decoding and validating tokens
- Token expiration

**Try:**
- POST `/login` to get a token
- POST `/validate` with your token
- GET `/demo/token` to see token internals
- Visit https://jwt.io and paste your token!

---

### Step 4: Complete OAuth2
**File:** `step4_complete.py`

The complete OAuth2 implementation with protected routes!

```bash
uvicorn tutorial.step4_complete:app --reload
```

**Concepts:**
- OAuth2PasswordBearer
- Protected routes with dependencies
- Token-based authentication flow
- Public vs protected endpoints

**Try:**
- Visit http://127.0.0.1:8000/docs
- Try accessing protected routes without auth (401 error)
- Login via POST `/token`
- Click "Authorize" and paste your token
- Access protected routes successfully!

---

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:

- ✅ How to create a FastAPI application
- ✅ How to securely hash and verify passwords
- ✅ What JWT tokens are and how they work
- ✅ How to implement OAuth2 password flow
- ✅ How to protect API routes with authentication
- ✅ How to use FastAPI dependencies for authentication

---

## 💡 Tips

1. **Run each step in order** - concepts build on each other
2. **Read all the comments** - they explain WHY, not just HOW
3. **Try the exercises** - hands-on practice is key
4. **Use the interactive docs** - visit /docs for each step
5. **Experiment** - try breaking things to understand how they work!

---

## 🤔 Common Questions

### "What's the difference between authentication and authorization?"
- **Authentication**: Who are you? (Login)
- **Authorization**: What can you do? (Permissions)

This tutorial covers authentication. For authorization, you'd add role/permission checks.

### "Is this production-ready?"
Almost! For production, you should:
- Use environment variables for SECRET_KEY
- Use a real database (not a dictionary)
- Enable HTTPS only
- Add rate limiting
- Implement refresh tokens
- Add proper logging

### "Where do I go from here?"
- Add user registration
- Implement password reset
- Add role-based access control (RBAC)
- Connect to PostgreSQL/MySQL
- Deploy to cloud (Heroku, AWS, GCP)

---

## 📖 Additional Resources

- [FastAPI Security Tutorial](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - Decode and verify tokens
- [OAuth 2.0 Specification](https://oauth.net/2/)

---

Happy learning! 🚀
