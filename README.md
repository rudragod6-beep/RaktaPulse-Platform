# 🩸 RaktaPulse - Community Blood Management System

Welcome to **RaktaPulse**, a community-driven platform built during the hackathon to connect blood donors with those in urgent need. Our mission is to ensure that no life is lost due to a lack of blood availability by leveraging real-time location data and community alerts.

## ✨ Features

- **📍 Real-time Donor Matching**: Find donors within a 10km radius using geolocation.
- **🚨 Emergency Alerts**: Simulated SMS broadcast to nearby donors for critical requests.
- **💬 P2P Chat**: Integrated messaging for donors and requesters to coordinate.
- **🛡️ Health Tracking**: Manage vaccination records and digital health reports.
- **🏆 Gamification**: Earn badges for your contributions to the community.

## 🛠️ Technical Stack

- **Backend**: Python 3.11, Django 5.x
- **Database**: MariaDB/MySQL
- **Frontend**: Bootstrap 5, FontAwesome, Leaflet.js (Maps)
- **Deployment**: Apache, Cloudflare Tunnel

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. **Database Setup**:
   ```bash
   python3 manage.py migrate
   ```

3. **Run the Server**:
   ```bash
   python3 manage.py runserver
   ```

---
*Developed with ❤️ for the Hackathon 2026. Let's save lives, one drop at a time.*
