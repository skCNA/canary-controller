# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Changelog

### v2.1.0 (2025-10-24) - Frontend Enhancement Release
**Major User Experience Improvements**

#### New Features
- **Enhanced Input Fields**: Click-to-expand functionality for better text editing
- **Modern Toast Notifications**: Replaced disruptive alerts with elegant toast system
- **Real-time Feedback**: Character counting and inline validation messages
- **Ajax Operations**: Non-refreshing form submissions for smoother workflow
- **Keyboard Shortcuts**: Enter to save, Escape to cancel

#### Bug Fixes
- Fixed input field overflow issues where long text was not visible
- Improved error handling for lock/unlock operations
- Enhanced form validation with better user feedback

#### Technical Improvements
- Modular JavaScript architecture with separation of concerns
- Enterprise-grade code structure
- Removed all redundant files and debug elements
- Improved accessibility and mobile responsiveness

#### Code Structure
- Consolidated JavaScript from 3 files into 1 unified module
- Eliminated inline JavaScript from HTML templates
- Implemented proper module pattern with clear interfaces
- Added comprehensive error handling and logging

#### Breaking Changes
- Updated JavaScript file structure (now uses `canary-main.js`)
- Enhanced form submission behavior (no page refresh)
- Modified error presentation (toast notifications instead of alerts)

---

### Previous Versions

## Project Overview

Canary Controller is a Flask-based web application for managing Kubernetes Ingress Canary deployments. It provides a web interface to configure canary strategies (weight-based, header-based, cookie-based) for NGINX Ingress Controller.

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py
# Server runs on http://0.0.0.0:8888
```

### Docker Development
```bash
# Build image
docker build -t canary-controller .

# Run container
docker run -p 8888:8888 canary-controller
```

### Production Deployment
```bash
# Using Gunicorn (as specified in Dockerfile)
gunicorn -w 1 -k gevent -b 0.0.0.0:8888 app:create_app()
```

## Architecture

### Core Application Structure
- **Flask App Factory Pattern**: `app/__init__.py` creates the Flask app using `create_app()`
- **Blueprint-based Routes**: Main routes defined in `app/routes.py` as a "main" blueprint
- **Kubernetes Integration**: `app/kubectl_utils.py` handles all Kubernetes API interactions
- **Concurrency Control**: Global lock table prevents simultaneous modifications to same Ingress

### Key Components

#### Routes (`app/routes.py`)
- `GET /` - Main dashboard showing all Canary Ingress
- `GET /set` - Updates Ingress annotations (requires lock)
- `POST /lock` - Locks Ingress for modifications
- `POST /unlock` - Unlocks Ingress

#### Kubernetes Utils (`app/kubectl_utils.py`)
- `get_ingresses()` - Fetches all Ingress with `canary: "true"` annotation
- `set_ingress_annotations()` - Patches Ingress annotations
- Config loading priority: in-cluster config → local kubeconfig at `/Users/admin/.kube/config-devops`

#### Concurrency Management
- Global lock table with 24-hour TTL automatic cleanup
- User identification via `X-Auth-Request-Email` header (falls back to "anonymous")
- Thread-safe operations using `threading.RLock()`

## Configuration

### Kubernetes Config Path
Default kubeconfig path: `/Users/admin/.kube/config-devops`
Modify in `app/kubectl_utils.py:7` if different path needed.

### Authentication
- Uses `X-Auth-Request-Email` header for user identification
- Supports OIDC integration in-cluster
- Anonymous access defaults to user "anonymous"

### Supported Canary Strategies
1. **Weight-based**: `nginx.ingress.kubernetes.io/canary-weight` (0-100)
2. **Header-based**: `nginx.ingress.kubernetes.io/canary-by-header`, `canary-by-header-value`, `canary-by-header-pattern`
3. **Cookie-based**: `nginx.ingress.kubernetes.io/canary-by-cookie`

## Dependencies

Core dependencies from `requirements.txt`:
- Flask==3.0.3 (Web framework)
- gunicorn==21.2.0 (Production WSGI server)
- kubernetes==30.1.0 (Kubernetes Python client)
- gevent==25.9.1 (Async worker for gunicorn)

## Frontend Architecture

### Modern UI Enhancements (2025-10-24)
The frontend has been completely refactored to provide an enterprise-grade user experience:

#### Enhanced Features
- **Input Field Expansion**: Click-to-expand input fields with smooth animations
- **Toast Notification System**: Modern, non-intrusive feedback system replacing alerts
- **Real-time Character Counting**: Shows character count for text inputs
- **Form Validation**: Client-side validation with inline error messages
- **Keyboard Shortcuts**: Enter to save, Escape to cancel
- **Ajax Operations**: Non-refreshing form submissions
- **Responsive Design**: Mobile-friendly interface

#### Frontend Asset Structure
```
app/static/
├── css/
│   ├── bootstrap.min.css (External library)
│   └── canary-input.css (Custom styles for enhanced UI)
└── js/
    └── canary-main.js (Integrated all JavaScript functionality)
```

#### JavaScript Modules
- **Toast System**: Unified notification management
- **InputExpander**: Input field expansion and character counting
- **FormHandler**: Ajax form submission handling
- **FormValidator**: Real-time form validation
- **LockService**: Lock/Unlock API management

#### User Experience Improvements
- No page refreshes for form submissions
- Visual feedback for all user actions
- Graceful error handling with user-friendly messages
- Accessibility improvements with proper ARIA labels
- Production-ready code with no debug elements

### Legacy Frontend (Deprecated)
- Previous implementation used separate files for validation
- Alert-based error handling (replaced with Toast system)
- Static form submission (replaced with Ajax)

## Important Notes
- The application only processes Ingress with `nginx.ingress.kubernetes.io/canary: "true"` annotation
- All modifications require acquiring a lock first to prevent concurrent changes
- Kubernetes RBAC permissions are handled externally through the kubeconfig
- In-cluster deployment uses service account permissions