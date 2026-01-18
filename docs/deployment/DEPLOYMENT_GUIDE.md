# Deployment Guide

This document explains how to deploy the Webhook server to production.

## 📋 Supported Platforms

- **Render.com** (Recommended - Free tier available)
- **Railway.app** (Free tier available)
- **Fly.io** (Free tier available)

---

## 🚀 Deployment to Render.com

### Prerequisites

1. Render.com account (free tier available)
2. GitHub repository connected to Render
3. LINE Developers account with Bot credentials

### Step 1: Prepare Repository

The repository includes the following files for Render.com deployment:

- `Procfile` - Defines the command to run the webhook server
- `render.yaml` - Render.com service configuration (optional)
- `requirements.txt` - Python dependencies

### Step 2: Create Web Service on Render.com

1. Log in to [Render.com Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `information-delivery-bot-webhook`
   - **Region**: Choose closest region
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: Leave empty
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.webhook_server:app`

### Step 3: Configure Environment Variables

Add the following environment variables in Render.com dashboard:

| Key | Value | Required | Description |
|-----|-------|----------|-------------|
| `LINE_CHANNEL_ACCESS_TOKEN` | Your token | Yes | LINE Channel Access Token |
| `LINE_CHANNEL_SECRET` | Your secret | Yes | LINE Channel Secret |
| `PORT` | `10000` | No | Port number (automatically set by Render) |
| `GMAIL_ACCOUNT` | Your email | No | Gmail account for email collection |
| `GMAIL_APP_PASSWORD` | Your password | No | Gmail app password |
| `GEMINI_API_KEY` | Your API key | No | Gemini API key for summarization |

**Note**: `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_CHANNEL_SECRET` are required for the webhook server to function.

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for the build to complete
3. Once deployed, copy the service URL (e.g., `https://information-delivery-bot-webhook.onrender.com`)

### Step 5: Configure LINE Developers Webhook URL

1. Go to [LINE Developers Console](https://developers.line.biz/console/)
2. Select your channel
3. Go to "Messaging API" settings
4. Set Webhook URL to: `https://your-service-url.onrender.com/webhook`
5. Click "Verify" to test the connection
6. Enable "Use webhook"

### Step 6: Test the Deployment

1. Send a message to your LINE Bot
2. Check Render.com logs to confirm webhook is received
3. Verify that the Bot responds correctly

---

## 🚂 Deployment to Railway.app

### Step 1: Create Project

1. Log in to [Railway.app](https://railway.app/)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select your repository

### Step 2: Configure Service

Railway will automatically detect the `Procfile`. Configure environment variables:

- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `PORT` (automatically set by Railway)
- Other optional variables as needed

### Step 3: Set Webhook URL

1. Copy the Railway service URL
2. Configure LINE Developers Webhook URL: `https://your-service-url.railway.app/webhook`

---

## ✈️ Deployment to Fly.io

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login

```bash
fly auth login
```

### Step 3: Initialize Fly App

```bash
fly launch
```

### Step 4: Configure Environment Variables

```bash
fly secrets set LINE_CHANNEL_ACCESS_TOKEN=your_token
fly secrets set LINE_CHANNEL_SECRET=your_secret
```

### Step 5: Deploy

```bash
fly deploy
```

### Step 6: Set Webhook URL

Configure LINE Developers Webhook URL: `https://your-app.fly.dev/webhook`

---

## 🔧 Configuration

### Health Check Endpoint

The webhook server includes a health check endpoint at `/health` that returns `OK` when the server is running.

You can use this endpoint to:
- Monitor service health
- Set up uptime monitoring
- Verify deployment status

### Logs

Monitor your deployment logs to troubleshoot issues:

- **Render.com**: Dashboard → Service → Logs
- **Railway.app**: Dashboard → Service → Logs
- **Fly.io**: `fly logs`

### Troubleshooting

#### Webhook Not Receiving Requests

1. Verify Webhook URL is correctly set in LINE Developers Console
2. Check that the service is running (check health endpoint)
3. Review logs for errors
4. Verify environment variables are set correctly

#### Signature Verification Errors

1. Verify `LINE_CHANNEL_SECRET` is correct
2. Check that the secret matches the one in LINE Developers Console
3. Review server logs for detailed error messages

#### Service Crashes

1. Check logs for Python errors
2. Verify all dependencies are in `requirements.txt`
3. Ensure environment variables are set
4. Check that the start command is correct

---

## 📝 Notes

- Free tier services may spin down after inactivity. The first request after inactivity may be slower.
- For production use, consider upgrading to a paid plan for better reliability.
- Keep your `LINE_CHANNEL_SECRET` secure and never commit it to version control.

---

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit sensitive credentials to the repository
2. **HTTPS**: Always use HTTPS for webhook URLs (provided by all platforms)
3. **Signature Verification**: Always enable signature verification in production
4. **Rate Limiting**: Consider implementing rate limiting for production use

---

**Last Updated**: 2025-01-18

