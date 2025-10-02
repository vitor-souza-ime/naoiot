
# 🔥 NAO IoT Fire Detection

This project implements a **fire detection system** using the **NAO robot**, the **BLIP (Bootstrapping Language-Image Pre-training)** model for image captioning, and integration with **ThingSpeak** for IoT alerting.

📂 Repository: [naoiot](https://github.com/vitor-souza-ime/naoiot)  
📄 Main file: `main.py`

---

## ⚙️ Features

- Connects to the **NAO robot** and captures images in real time.  
- Uses the **BLIP model** (`Salesforce/blip-image-captioning-large`) to generate captions from images.  
- Detects fire-related events based on keywords in generated captions.  
- Sends real-time alerts to **ThingSpeak** (IoT platform).  
- Text-to-Speech: the NAO robot verbally announces fire alerts.  
- Saves monitoring images and log files for audit and traceability.  

---

## 🛠 Requirements

- Python 3.8+  
- [PyTorch](https://pytorch.org/)  
- [Transformers](https://huggingface.co/docs/transformers/index)  
- [Pillow](https://pillow.readthedocs.io/)  
- [Matplotlib](https://matplotlib.org/)  
- [Requests](https://docs.python-requests.org/)  
- [NAOqi SDK](http://doc.aldebaran.com/2-1/dev/python/index.html)  

Install dependencies:

```bash
pip install torch torchvision transformers pillow matplotlib requests
````

---

## 🚀 How to Run

1. Clone this repository:

   ```bash
   git clone https://github.com/vitor-souza-ime/naoiot.git
   cd naoiot
   ```

2. Configure your **ThingSpeak API key** in `main.py`:

   ```python
   THINGSPEAK_API_KEY = "YOUR_API_KEY"
   ```

3. Update the NAO robot IP and port in the `connect_to_nao()` function if needed:

   ```python
   session = connect_to_nao("ROBOT_IP", 9559)
   ```

4. Run the main program:

   ```bash
   python main.py
   ```

---

## 📊 ThingSpeak Integration

The system sends the following fields to ThingSpeak:

* `field1`: Fire status (1 = fire detected, 0 = normal)
* Additional fields can be extended (e.g., detection time, latency).

---

## 📂 Output

The program automatically creates a timestamped output folder:

* `monitor_*.png` → monitoring snapshots
* `FIRE_ALERT_*.jpg` → images when fire is detected
* `FIRE_ALERT_*.txt` → logs with details of the detection

---

## 🧠 How It Works

1. The NAO camera captures an image.
2. BLIP generates a caption describing the scene.
3. The system checks for **fire-related keywords** (e.g., "fire", "smoke", "flames").
4. If fire is detected:

   * An alert is sent to ThingSpeak.
   * The NAO robot verbally announces the detection.
   * The image and log are saved.
5. If no fire is detected, the status is sent as normal (`0`).

---

## ⚠️ Notes

* Ensure that the NAO robot is accessible on the network.
* ThingSpeak requires an active API key.
* This project is for **research and educational purposes**; do not use as a certified fire alarm system.

---

## 📜 License

MIT License.
See [LICENSE](LICENSE) for details.


Do you want me to also include an **example ThingSpeak dashboard screenshot** section in the README (with a placeholder image), so people can see how alerts are visualized?
```
