# 🛰️ Rainbow Six Siege Drone

A Raspberry Pi–powered surveillance drone inspired by *Rainbow Six Siege*. You can control the drone use WASD and it has an onboard camera.

---

## 🧩 Parts List
You’re free to source your own parts, but here are the ones we used:

| Component             | Link |
|-----------------------|------|
| **Motors, Screws & Wires** | [Amazon Link](https://a.co/d/3BgiAKo) |
| **L298N with jumpers** | [Amazon Link](https://a.co/d/dn5BVuh) |
| **Battery Pack**                | [Amazon Link](https://a.co/d/glCc2qe) |
| **Battery Charger**             | [Amazon Link](https://a.co/d/avXQsUM) |
| **Camera Module**              | [Amazon Link](https://a.co/d/7FEJZUs) |
| **T-Connector for battery**                | [Amazon Link](https://a.co/d/bJOUHKB) |
| **Raspberry Pi**              | *Find your own* – RPi 4 Model B or newer is highly recommended |
| **Power Bank (for RPi)**       | Any standard USB power bank should work, make sure it fits on the baseplate |

**Also you will need to 3d print baseplate.stl**
---

## ⚙️ Setup Instructions

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
   
 2. **Run Code**
    ```bash
    python3 app.py
    ```
3. (Optional) Run on Startup:
    Use crontab to auto-start the script on boot:
    ```bash
    crontab -e
    ```
4. Add this following at the end
    ```bash
    @reboot sleep 30 && cd /path/to/your/project && /usr/bin/python3 app.py
    ```
    Replace ```/path/to/your/project``` with your directory
