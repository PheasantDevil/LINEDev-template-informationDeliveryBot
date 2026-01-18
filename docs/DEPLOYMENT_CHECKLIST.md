# Deployment Checklist

Use this checklist to ensure a smooth deployment process.

## ✅ Pre-Deployment

- [ ] All environment variables are documented in `.env.example`
- [ ] `Procfile` is configured correctly
- [ ] `requirements.txt` includes all dependencies
- [ ] Tests are passing (`pytest tests/`)
- [ ] Code quality checks pass (`flake8 src/`)

## ✅ Platform Selection

- [ ] Chosen deployment platform (Render.com / Railway.app / Fly.io)
- [ ] Account created and logged in
- [ ] GitHub repository is connected

## ✅ Service Configuration

- [ ] Service name is set
- [ ] Region is selected
- [ ] Build command is configured: `pip install -r requirements.txt`
- [ ] Start command is configured: `gunicorn --bind 0.0.0.0:$PORT src.webhook_server:app`
- [ ] Health check path is set: `/health`

## ✅ Environment Variables

- [ ] `LINE_CHANNEL_ACCESS_TOKEN` is set
- [ ] `LINE_CHANNEL_SECRET` is set
- [ ] `PORT` is set (usually auto-set by platform)
- [ ] `GMAIL_ACCOUNT` is set (if using email collection)
- [ ] `GMAIL_APP_PASSWORD` is set (if using email collection)
- [ ] `GEMINI_API_KEY` is set (if using AI summarization)

## ✅ LINE Developers Configuration

- [ ] Webhook URL is set to: `https://your-service-url/webhook`
- [ ] Webhook URL is verified (green checkmark)
- [ ] "Use webhook" is enabled
- [ ] "Auto-reply messages" is disabled (if not needed)

## ✅ Deployment

- [ ] Initial deployment is successful
- [ ] Service is running (check `/health` endpoint)
- [ ] Logs show no errors

## ✅ Testing

- [ ] Health check endpoint responds: `curl https://your-service-url/health`
- [ ] Index endpoint responds: `curl https://your-service-url/`
- [ ] Webhook receives test messages from LINE Bot
- [ ] Bot responds correctly to commands
- [ ] User registration works
- [ ] Category subscription works
- [ ] Site list command works
- [ ] Help message displays correctly

## ✅ Monitoring

- [ ] Logs are accessible
- [ ] Error monitoring is set up (optional)
- [ ] Uptime monitoring is configured (optional)

## ✅ Documentation

- [ ] Deployment guide is reviewed
- [ ] Troubleshooting steps are documented
- [ ] Team members are notified of deployment

---

**Deployment Date**: _________________

**Deployed By**: _________________

**Service URL**: _________________

**Notes**: 
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

